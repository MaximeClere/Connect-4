import numpy as np
import pygame
import sys
import math
import random

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 1
AI = 2
EMPTY = 0

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)

#Game rules
def create_Board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_Piece(board, row, col, piece):
    board[row][col]=piece

def is_Valid_Location(board, col):
    return board[ROW_COUNT-1][col]==0

def get_Next_Open_Row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col]==0:
            return r

def winning_move(board, piece):
    #Horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    
    #Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    
    #Diagonal /
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
            
    #Diagonal \
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
            
#AI logic
def get_Valid_Location(board):
    return [c for c in range(COLUMN_COUNT) if is_Valid_Location(board, c)]

def evaluate_Window(window, piece):
    score=0
    opp_piece=PLAYER if piece==AI else AI
    
    if window.count(piece)==4:
        score+=100
    elif window.count(piece)==3 and window.count(EMPTY)==1:
        score+=10
    elif window.count(piece)==2 and window.count(EMPTY)==2:
        score+=5
    
    if window.count(opp_piece)==3 and window.count(EMPTY)==1:
        score-=80
    
    return score

def score_Position(board, piece):
    score=0

    center_array=[int(i) for i in list(board[:, COLUMN_COUNT//2])]
    score+=center_array.count(piece)*6

    for r in range(ROW_COUNT):
        row_array=[int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window=row_array[c:c+4]
            score+=evaluate_Window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array=[int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window=col_array[r:r+4]
            score+=evaluate_Window(window, piece)
    
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window=[board[r+i][c+i] for i in range(4)]
            score+=evaluate_Window(window, piece)
    
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT-3):
            window=[board[r-i][c+i] for i in range(4)]
            score+=evaluate_Window(window, piece)
    
    return score

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations=get_Valid_Location(board)
    terminal=winning_move(board,PLAYER) or winning_move(board,AI) or len(valid_locations)==0
    if depth==0 or terminal:
        if terminal:
            if winning_move(board, AI):
                return (None, 1e9)
            elif winning_move(board, PLAYER):
                return (None, -1e9)
            else: # match nul
                return (None, 0)
        else:
            return (None, score_Position(board, AI))
        
    if maximizingPlayer:
        value=-math.inf
        best_col=random.choice(valid_locations)
        for col in valid_locations:
            row=get_Next_Open_Row(board, col)
            b_copy=board.copy()
            drop_Piece(b_copy, row, col, AI)
            new_score=minimax(b_copy, depth-1, alpha, beta, False)[1]
        
            if new_score > value:
                value=new_score
                best_col=col

            alpha=max(alpha, value)
            if alpha>=beta:
                break
        return best_col, value

    else:
        value=math.inf
        best_col=random.choice(valid_locations)
        for col in valid_locations:
            row=get_Next_Open_Row(board, col)
            b_copy=board.copy()
            drop_Piece(b_copy, row, col, PLAYER)
            new_score=minimax(b_copy, depth-1, alpha, beta, True)[1]  

            if new_score < value:
                value=new_score
                best_col=col
        
            beta=min(beta, value)
            if alpha>=beta:
                break
        return best_col, value

            
#Board drawing with Pygame
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
           pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
           pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c]==PLAYER:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c]==AI: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update() 

#Difficulty (depth)
def chooseDepth():
    difficulty=["Easy", "Medium", "Hard"]
    font_btn=pygame.font.SysFont("monospace", 20)
    buttons=[]
    btn_width=100
    btn_height=100
    spacing=20
    start_x=(width - (3*btn_width + 2*spacing)) // 2
    y=height // 2 - btn_height // 2
    for i in range(3):
        rect=pygame.Rect(start_x + i*(btn_width + spacing), y, btn_width, btn_height)
        buttons.append((rect, difficulty[i]))

    choosing=True
    while choosing:
        screen.fill(BLACK)
        prompt = font_btn.render("Choose difficulty :", True, (255,255,255))
        screen.blit(prompt, (width//2 - prompt.get_width()//2, y - 100))

        for rect, diff in buttons:
            pygame.draw.rect(screen, BLUE, rect)
            txt = font_btn.render(diff, True, WHITE)
            screen.blit(txt, (rect.x + rect.width//2 - txt.get_width()//2, 
                              rect.y + rect.height//2 - txt.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, diff in buttons:
                    if rect.collidepoint(pos):
                        if diff == "Easy":
                            return 1
                        elif diff == "Medium":
                            return 3
                        elif diff == "Hard":
                            return 6

#Init
board=create_Board()
pygame.init()
screen=pygame.display.set_mode(size)
font=pygame.font.SysFont("monospace", 75)
DEPTH = chooseDepth()
draw_board(board)
pygame.display.update()

game_over=False
turn=random.randint(PLAYER, AI)

#Game loop
while not game_over:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            sys.exit()
        
        if event.type==pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx=event.pos[0]
            if turn==PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        if event.type==pygame.MOUSEBUTTONDOWN:
            if turn==PLAYER:
                posx=event.pos[0]
                col=int(math.floor(posx/SQUARESIZE))

                if is_Valid_Location(board, col):
                    row=get_Next_Open_Row(board, col)
                    drop_Piece(board, row, col, PLAYER)

                    if winning_move(board, PLAYER):
                        label=font.render("Player wins !", 1, RED)
                        screen.blit(label, (40,10))
                        game_over=True
            
                    turn = AI
                    draw_board(board)
    
    if turn==AI and not game_over:
        if DEPTH==1:
            if random.randint(0,4)==0:
                col, minimax_score=(random.choice(get_Valid_Location(board)), 0)
            else:
                col, minimax_score=minimax(board, DEPTH, -math.inf, math.inf, True)
        else:
            col, minimax_score=minimax(board, DEPTH, -math.inf, math.inf, True)

        if is_Valid_Location(board, col):
            row=get_Next_Open_Row(board, col)
            drop_Piece(board, row, col, AI)

            if winning_move(board, AI):
                label=font.render("AI wins !", 1, YELLOW)
                screen.blit(label, (40,10))
                game_over=True
            
            turn=PLAYER
            draw_board(board)
        
    if game_over:
        pygame.time.wait(3000)



