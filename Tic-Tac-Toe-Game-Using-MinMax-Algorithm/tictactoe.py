import pygame, sys
import numpy as np
import copy, random

from constants import *

# PYGAME SETUP

pygame.init()
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption( "TIC TAC TOE AI" )
screen.fill( BG_COLOR )


class StartMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont('comic sans MS', 60, bold= True)
        self.menu_font = pygame.font.SysFont('comic sans MS', 30)
        self.title_text = self.title_font.render("TIC TAC TOE AI", True, CIRCLE_COLOR)
        self.play_text = self.menu_font.render("PLAY", True, CIRCLE_COLOR)
        self.instructions_text = self.menu_font.render("INSTRUCTIONS", True, CIRCLE_COLOR)
        self.title_rect = self.title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.play_rect = self.play_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.instructions_rect = self.instructions_text.get_rect(center=(WIDTH//2, HEIGHT//1.5))

    def draw(self):
        screen.fill(BG_COLOR)
        screen.blit(self.title_text, self.title_rect)
        pygame.draw.rect(screen, BG_COLOR, self.play_rect, 2)
        pygame.draw.rect(screen, BG_COLOR, self.instructions_rect, 2)
        screen.blit(self.play_text, self.play_rect)
        screen.blit(self.instructions_text, self.instructions_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.play_rect.collidepoint(pos):
                    return "PLAY"
                elif self.instructions_rect.collidepoint(pos):
                    return "INSTRUCTIONS"

class InstructionsMenu:
    def __init__(self, screen):
        self.font = pygame.font.SysFont('helvetica', 20)
        self.exitfont = pygame.font.SysFont('comic sans MS', 30, bold= True)
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.bg_color = BG_COLOR
        self.text_color = (255, 255, 255)
        self.exit_text = self.exitfont.render("EXIT", True, CROSS_COLOR)
        self.exit_rect = self.exit_text.get_rect(center=(self.width // 2, (self.height // 4) + 300))

        self.display()

        
    def display(self):
        self.screen.fill(self.bg_color)
        instructions = [
            "INSTRUCTIONS",
            "\n",
            "Press 'r' to Restart ",
            "There are 2 game modes:",
            "   1. Player v/s Player",
            " 2. Player v/s AI",
            "Press 'g' to change the game mode",
            "Press '0' to play at Level 0 (Random AI)",
            "Press '1' to play at Level 1 (MinMax AI)", 
        ]
        y = self.height // 4
        for line in instructions:
            text = self.font.render(line, True, self.text_color)
            text_rect = text.get_rect(center=(self.width // 2, y))
            self.screen.blit(text, text_rect)
            y += 30
        self.screen.blit(self.exit_text, self.exit_rect)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.exit_rect.collidepoint(pos):
                    return True

class Board:
    def __init__(self):
        self.squares = np.zeros( (ROWS, COLS) )
        self.empty_sqrs = self.squares # [squares]
        self.marked_sqrs = 0

    def final_state(self, show= False):
        '''
            @return 0 if there is no win yet
            @return 1 if palyer 1 wins
            @return 2 if player 2 wins
        '''
        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRCLE_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]
        
        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRCLE_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]
            
        # asc diagonal win check
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRCLE_COLOR if self.squares[2][0] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[2][0]

        # desc diagonal win check
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRCLE_COLOR if self.squares[0][0] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[0][0]

        return 0 # no win yet

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0
    
    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))
        return empty_sqrs
    
    def isfull(self):
        return self.marked_sqrs == 9
    
    def isempty(self):
        return self.marked_sqrs == 0

class AI:
    def __init__(self, level = 1, player = 2) -> None:
        self.level = level
        self.player = player
    
    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))
        return empty_sqrs[idx] # [row col]
    
    def minimax(self, board, maximizing):
        # terminal case
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None # eval, move
        
        # player 2 wins
        if case == 2:
            return -1, None
        
        elif board.isfull():
            return 0, None
        
        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
            return min_eval, best_move


    def eval(self, main_board):
        if self.level == 0:
            # random choice
            eval = 'random'
            move = self.rnd(main_board)

        else:
            # minmax algo choice
            eval, move = self.minimax(main_board, False)
        
        print(f'AI has chosen to the mark the square in pos {move}, with an eval of {eval}')

        return move # row, col

class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1 # 1 - cross; 2 - circles
        self.gamemode = 'ai'
        self.running = True
        self.show_lines()
    
    
    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def show_lines(self):
        # background
        screen.fill( BG_COLOR )

        # 1 horizontal
        pygame.draw.line( screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH )
        # 2 horizontal
        pygame.draw.line( screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH )
        # 1 vertical
        pygame.draw.line( screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH )
        # 2 vertical
        pygame.draw.line( screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH )

    def next_turn(self):
        self.player = self.player % 2 + 1
    
    def draw_fig(self, row, col):
        if self.player == 1:
            # desc line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line( screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)

            # asc line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line( screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)

        elif self.player == 2:
            center = (int(col * SQSIZE + SQSIZE // 2), int(row * SQSIZE + SQSIZE // 2))
            pygame.draw.circle( screen, CIRCLE_COLOR, center, RADIUS, CIRCLE_WIDTH)

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'
    
    def reset(self):
        self.__init__()

    def isover(self):
        return self.board.final_state(show= True) != 0 or self.board.isfull()


def main():

    start_menu = StartMenu()
    instructions_menu = InstructionsMenu(screen)

    while True:
        start_menu.draw()
        pygame.display.update()
        menu_choice = start_menu.handle_events()
        if menu_choice == "INSTRUCTIONS":
            while True:
                instructions_menu.display()
                pygame.display.update()
                exit_choice = instructions_menu.handle_events()
                if exit_choice:
                    break
        elif menu_choice == "PLAY":

            # object
            game = Game()
            board = game.board
            ai = game.ai

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.KEYDOWN:
                        # g - gamemode
                        if event.key == pygame.K_g:
                            game.change_gamemode()
                        
                        # r - reset
                        if event.key == pygame.K_r:
                            game.reset() 
                            board = game.board
                            ai = game.ai

                        # 0 - random ai
                        if event.key == pygame.K_0:
                            ai.level = 0
                        
                        # 1 - unbeatable ai
                        if event.key == pygame.K_1:
                            ai.level = 1
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        row = event.pos[1] // SQSIZE # x coord
                        col = event.pos[0] // SQSIZE # y coord

                        if board.empty_sqr(row, col) and game.running:
                            game.make_move(row, col)

                            if game.isover():
                                game.running = False

                if game.gamemode == 'ai' and game.player == ai.player and game.running:
                    pygame.display.update()
                    row, col = ai.eval(board)
                    game.make_move(row, col)

                    if game.isover():
                        game.running = False
                
                pygame.display.update()  

main()



