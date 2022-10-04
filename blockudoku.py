import random
import logging
from tkinter import E
import numpy as np
import pygame

class blockudoku:
    block_list = {"L": [[1,0,0], 
                        [1,0,0],
                        [1,1,0]],
                "L90": [[0,0,1], 
                        [1,1,1], 
                        [0,0,0]],
                "L180": [[1,1,0], 
                        [0,1,0], 
                        [0,1,0]],
                "L270": [[1,1,1], 
                        [1,0,0], 
                        [0,0,0]],
                "BIGL": [[1,1,1], 
                        [1,0,0], 
                        [1,0,0]],
                "BIGL90": [[1,0,0], 
                            [1,0,0], 
                            [1,1,1]],
                "BIGL180": [[0,0,1], 
                            [0,0,1], 
                            [1,1,1]],
                "BIGL270": [[1,1,1], 
                            [0,0,1], 
                            [0,0,1]],
                "RL": [[0,1,0], 
                        [0,1,0], 
                        [1,1,0]],
                "RL90": [[1,1,1], 
                        [0,0,1], 
                        [0,0,0]],
                "RL180": [[1,1,0], 
                        [1,0,0], 
                        [1,0,0]],
                "RL270": [[1,0,0], 
                        [1,1,1], 
                        [0,0,0]],
                "cross":  [[0,1,0], 
                            [1,1,1], 
                            [0,1,0]],
                "slash2":  [[1,0,0], 
                            [0,1,0], 
                            [0,0,0]],
                "rslash2":  [[0,1,0], 
                            [1,0,0], 
                            [0,0,0]],
                "slash3":  [[0,0,1], 
                            [0,1,0], 
                            [1,0,0]],
                "rslash3": [[1,0,0], 
                            [0,1,0],
                            [0,0,1]],
                "z":  [[1,1,0],
                        [0,1,1], 
                        [0,0,0]],
                "z90":  [[0,1,0], 
                        [1,1,0], 
                        [1,0,0]],
                "rz":  [[0,1,1], 
                        [1,1,0], 
                        [0,0,0]],
                "rz90":  [[1,0,0], 
                        [1,1,0], 
                        [0,1,0]],
                "tetris":  [[0,1,0], 
                            [1,1,1], 
                            [0,0,0]],
                "tetris90":  [[0,1,0], 
                            [1,1,0], 
                            [ 0,1,0]],
                "tetris180":  [[1,1,1], 
                                [0,1,0], 
                                [0,0,0]],
                "tetris270":  [[1,0,0], 
                                [1,1,0], 
                                [1,0,0]],
                "square":[[1,1,0], 
                          [1,1,0], 
                          [0,0,0]]}

    block_color = (150, 50, 255)
    background_color = (255, 255, 255)
    small_border_color = (150, 150, 150)
    large_border_color = (30, 30, 30)
    field_size = (450, 450)
    padding = 7
    padding_hand_board = 25
    hand_size = 200
    border = 25
    screen_size = [field_size[0] + 2*border, field_size[1] + 2*border + hand_size + padding_hand_board] 

    def __init__(self, visualization=True):
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S:', level=logging.DEBUG)
        self.game_field = game_field()
        self.generate_blocks()
        self.draw_blocks()
        self.score = 0
        pygame.init()
        self.font = pygame.font.SysFont('Garamond', 30)
        # size variable is using for set screen size    
        self.screen = pygame.display.set_mode(self.screen_size)
        self.set_background()
        pygame.display.update()
        self.visualization = visualization


    def generate_blocks(self):
        self.blocks = []
        for blck in self.block_list.items():
            self.blocks.append(block(blck))

    def draw_blocks(self):
        drawn_blocks = [random.choice(self.blocks) for x in range(3)]
        logging.info(f"Drawing {drawn_blocks}")
        self.current_hand = drawn_blocks
        return 1

    def add_block_to_field(self, current_block, position):
        r, c = current_block.row_colum(position)
        logging.info(f"User Query: add block {current_block} to field ({r}, {c})")
        success = self.game_field.add_block(current_block, position)
        if success:
            self.current_hand.remove(current_block)
            current_value = np.sum(current_block.shape)
            self.score = self.score + current_value
            logging.info(f"Adding {current_value}. Score is now {self.score}")
        self.update()
        return 1

    def update(self):
        self.score = self.score + self.game_field.check_and_clear()
        if self.visualization:
            self.show_gamefield()
        if len(self.current_hand) == 0:
            self.draw_blocks()
        # to implement clear blocks of 9


    def show_gamefield(self):
        w = self.field_size[0]/9 - self.padding
        h = self.field_size[1]/9 - self.padding
        for irow in range(9):
            for icol in range (9):
                filled = self.game_field.state[irow, icol]
                l = self.border + self.padding/2 + irow*(w+self.padding)
                t = self.border + self.padding/2 + icol*(h+self.padding)
                if filled:
                    color = self.block_color
                else:
                    color = self.background_color
                pygame.draw.rect(self.screen, color, [l, t, w, h], 0) # Rect(left, top, width, height) -> Rect

        # clear hand first
        hand_start_l = self.border
        hand_start_t = self.border + self.field_size[1] + self.padding_hand_board
        pygame.draw.rect(self.screen, self.background_color,
         [hand_start_l, hand_start_t, self.field_size[0], self.hand_size], 0) 
        for iblock, hand_block in enumerate(self.current_hand):
            for irow in range(3):
                for icol in range (3):
                    filled = hand_block.shape[irow, icol]
                    l = hand_start_l + self.padding/2 + irow*(w+self.padding) + iblock*self.field_size[0]/3
                    t = hand_start_t + self.padding/2 + icol*(h+self.padding)
                    
                    if filled:
                        color = self.block_color
                    else:
                        color = self.background_color
                    pygame.draw.rect(self.screen, color, [l, t, w, h], 0) # Rect(left, top, width, height) -> Rect
        score = self.font.render("Score: " + str(self.score), True, (0, 0, 0))
        self.screen.blit(score, (self.border, self.screen_size[1]-1.5*self.border))

        pygame.display.update()


    def set_background(self):
        self.screen.fill((255, 255, 255))
        # create small grid
        for irow in range(9):
            for icol in range (9):
                w = (self.field_size[0])/9
                h = (self.field_size[1])/9
                l = self.border + w*irow
                t = self.border + h*icol
                color = self.small_border_color
                pygame.draw.rect(self.screen, color, [l, t, w, h], 1) # Rect(left, top, width, height) -> Rect
        # create large grid
        for irow in range(3):
            for icol in range (3):
                w = (self.field_size[0])/3
                h = (self.field_size[1])/3
                l = self.border + w*irow
                t = self.border + h*icol
                color = self.large_border_color
                pygame.draw.rect(self.screen, color, [l, t, w, h], 1) # Rect(left, top, width, height) -> Rect

    def show_score(self):
        logging.info(f"Score: {self.score}")
        return self.score


class game_field:
    def __init__(self):
        logging.info("initialized empty gamefield")
        self.state = np.zeros((9,9), dtype=int)

    def __str__(self):
        print("\n")
        print("-----gamefield-----")
        for line in self.state:
            print(line)
        print("-------------------")
        return ""

    def add_block(self, blck, position, execute=True):
        state_overlay = blck.position_to_field(position)
        # i dont know how to catch the error better... not state overlay gives ambigous error
        if type(state_overlay) is list:
            logging.info("Block outside of field")
            return 0
        elif np.max(self.state + state_overlay) > 1:
            logging.info(f"Position {position} is not valid for {blck}")
            return 0
        if execute:
            logging.info("Adding block to current board")
            self.state = self.state + state_overlay
        return 1

    def check_and_clear(self):
        current_score = 0
        # check rows
        mark = np.zeros((9,9), dtype=int)
        for row in range(9):
            if self.state[row,:].all():
                mark[row,:] = 1
        for col in range(9):
            if self.state[:,col].all():
                mark[:,col] = 1
        for box in range(9):
            r, c = divmod(box, 3)
            R = 3*r
            C = 3*c
            if self.state[r:r+3, c:c+3].all():
                mark[r:r+3, c:c+3] = 1
        if mark.any():
            current_score = np.sum(mark)
            logging.info(f"+{current_score} points")
        self.state = self.state - mark
        return current_score



    
class block:
    empty_field = np.zeros((9,9), int)
    def __init__(self, blck):
        self.name = blck[0]
        self.shape = np.array(blck[1],dtype=int)
        logging.info(f"created block {self.name}")
                

    def __repr__(self):
        return self.name


    def position_to_field(self, position):
        A = np.copy(self.empty_field)
        B = np.copy(self.shape)
        r, c = self.row_colum(position)
        if type(position) is tuple:
            (r,c) = position
        else:
            r, c = divmod(position, 9)
        r1 = r+B.shape[0]
        c1 = c+B.shape[1]
        if r < 0 or r1 > 9 or c < 0 or c1 > 9:
            return []
        A[r:r1, c:c1] += B
        return A
    
    def row_colum(self, position):
        if type(position) is tuple:
            (r,c) = position
        else:
            r, c = divmod(position, 9)
        return r, c