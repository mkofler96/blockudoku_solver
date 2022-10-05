from signal import pause
from blockudoku import *
import random
import time
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.WARNING)

score = []

for igame in range(100):
    game = blockudoku(visualization=True)
    game_running = True
    while True:
        pos = random.randint(0, 81)
        current_hand = game.get_current_hand()
        if not current_hand:
            break
        hand_choice = random.choice(game.current_hand)
        possible_moves = game.get_possible_moves(hand_choice)
        if not possible_moves:
            break
        move_choice = random.choice(possible_moves)
        game.add_block_to_field(hand_choice, move_choice)
        time.sleep(1)
    score.append(game.show_score())

print(f"Mean score: {np.mean(score)}")