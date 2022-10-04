from signal import pause
from blockudoku import *
import random
import time
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.WARNING)

score = []

for igame in range(100):
    game = blockudoku(visualization=False)
    for i in range(1000):
        pos = random.randint(0, 81)
        game.add_block_to_field(random.choice(game.current_hand),pos)

    score.append(game.show_score())

print(f"Mean score: {np.mean(score)}")