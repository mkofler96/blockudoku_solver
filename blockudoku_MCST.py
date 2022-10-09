import random
import logging
from tkinter import E
from turtle import Turtle
import numpy as np
import pygame
from monte_carlo_tree_search import MCTS, Node
import random
from collections import namedtuple
_GMFLD = namedtuple("Gamefield", "state hand score blocks terminal")
_BLK   = namedtuple("Block", "block")

class blockudoku():
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

    def init(self, visualization=True):
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
        logging.debug(f"Score: {self.score}")
        return self.score

    def get_current_hand(self):
        return self.current_hand



class game_field(_GMFLD, Node):
    def __str__(self):
        print("\n")
        print("-----gamefield-----")
        for line in self.state:
            print(line)
        print("-------------------")
        return ""


    def add_block_to_field(self, current_block, position):
        state_overlay = current_block.position_to_field(position)
        success = True
        if type(state_overlay) is list:
            success = False
        elif np.max(self.state + state_overlay) > 1:
            success = False

        return state_overlay, success

    def check_and_clear(self, state):
        current_score = 0
        # check rows
        mark = np.zeros((9,9), dtype=int)
        for row in range(9):
            if state[row,:].all():
                mark[row,:] = 1
        for col in range(9):
            if state[:,col].all():
                mark[:,col] = 1
        for box in range(9):
            r, c = divmod(box, 3)
            R = 3*r
            C = 3*c
            if state[r:r+3, c:c+3].all():
                mark[r:r+3, c:c+3] = 1
        if mark.any():
            current_score = np.sum(mark)
            logging.debug(f"+{current_score} points")
        state = state - mark
        return state, current_score

    def get_possible_moves(self):
        possible_moves = []
        assert(type(self.hand) is list)
        for blck in self.hand:
            possible_moves_hand = []
            for x in range(81):
                state, possible = self.add_block_to_field(blck, x)
                if possible:
                    possible_moves_hand.append(x)
            possible_moves.append(possible_moves_hand)
        if len(self.hand)==0 and len(possible_moves)>0:
            raise RuntimeError("There can't be any possible moves if the hand is empty")
        return possible_moves


    def find_random_child(self):
        if self.terminal:
            return None  # If the game is finished then no moves can be made
        choices = self.get_possible_moves()
        # loop is needed because for some blocks there might not be a possible move, but its still on the hand
        found_possible_choice = False
        while not found_possible_choice:
            i_block = random.choice(range(len(choices)))
            if choices[i_block]:
                found_possible_choice = True
                position = random.choice(choices[i_block])    

        logging.debug("Finding Random Child")
        return self.make_move((i_block, position))

    def find_children(self):
        if self.terminal:  # If the game is finished then no moves can be made
            return set()
        # Otherwise, you can make a move in each of the empty spots
        set_of_all_possible_game_states = set()
        possible_moves = True
        i = 0
        possible_moves = self.get_possible_moves()
        for i_hand in range(len(possible_moves)):
            for position in possible_moves[i_hand]:
                logging.debug(f"Simulating move: {self.hand[i_hand]} (hand {i_hand}), position {position}")
                possible_state = self.make_move((i_hand, position))
                set_of_all_possible_game_states.add(possible_state)
        return set_of_all_possible_game_states


    def make_move(self, index):
        logging.debug("making move")
        blck = self.hand[index[0]]
        position = index[1]
        hand = self.hand.copy()

        # place block from hand to game field
        state_overlay, success = self.add_block_to_field(blck, position)
    
        score_from_placing = 0
        # remove block from hand
        if success:
            hand.remove(blck)
            score_from_placing = np.sum(blck.shape)
            logging.debug(f"Added block {blck} to score {score_from_placing} placing points")
            # state = update game state
            state_with_new_block = self.state + state_overlay
            state_after_clearing, score_from_clearing = self.check_and_clear(state_with_new_block)

        # not sure when to substract hand and refill
        if not hand:
            hand = self.draw_blocks(self.blocks)
            logging.debug(f"Refilling hand to: {hand}")

        possible_moves = self.get_possible_moves()
        is_terminal = not any(possible_moves)
        if is_terminal:
            print("break")
        score = self.score + score_from_placing + score_from_clearing
        logging.debug(f"Score: {score}")
        logging.debug(f"Self.score: {self.score}")
        #_GMFLD = namedtuple("Gamefield", "state hand score blocks terminal")
        return game_field(state_after_clearing, hand, score, self.blocks, is_terminal)


    def reward(self):
        return self.score 

    def is_terminal(self):
        return self.terminal or not any(self.get_possible_moves())

    def __hash__(self):
        state_tuple = tuple(map(tuple, self.state))

        hand_tuple = tuple([tuple(map(tuple, x.shape)) for x in self.hand])
        return hash((state_tuple, hand_tuple))

    def draw_blocks(self, blocks):
        drawn_blocks = [random.choice(blocks) for x in range(3)]
        logging.debug(f"Drawing {drawn_blocks}")
        return drawn_blocks




    
class block:
    empty_field = np.zeros((9,9), int)
    def __init__(self, blck):
        self.name = blck[0]
        self.shape = np.array(blck[1],dtype=int)
        logging.debug(f"created block {self.name}")
                

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
        if A.shape[0] != 9 and A.shape[1] != 9:
            raise ValueError("Shape of A must be 9x9")
        return A
    
    def row_colum(self, position):
        if type(position) is tuple:
            (r,c) = position
        else:
            r, c = divmod(position, 9)
        return r, c

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

def play_game():
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S:', level=logging.INFO)
    tree = MCTS()
    init_state = np.zeros((9,9), dtype=int)
    blocks = []
    for blck in block_list.items():
        blocks.append(block(blck))
    start_hand = [random.choice(blocks) for x in range(3)]
    board = game_field(init_state, start_hand, 0, blocks, False)
    logging.info("playing")
    while True:
        if board.terminal:
            break
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.
        for i in range(50):
            logging.info(f"Iteration {i}")
            tree.do_rollout(board)
        board = tree.choose(board)
        logging.info(f"Board score: {board.score}")
        print(board)
        print(board.terminal)
    logging.info("Finished")




if __name__ == "__main__":
    play_game()