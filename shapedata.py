from random import choice
from colors import Color

shape_names = ["I", "T", "O", "L", "J", "S", "Z"]

shapes = {
    "I": [[0, 1, 0, 0],
          [0, 1, 0, 0],
          [0, 1, 0, 0],
          [0, 1, 0, 0]],

    "T": [[0, 0, 0],
          [1, 1, 1],
          [0, 1, 0]],

    "O": [[1, 1],
          [1, 1]],

    "L": [[0, 1, 0],
          [0, 1, 0],
          [0, 1, 1]],

    "J": [[0, 1, 0],
          [0, 1, 0],
          [1, 1, 0]],

    "S": [[0, 0, 0],
          [0, 1, 1],
          [1, 1, 0]],

    "Z": [[0, 0, 0],
          [1, 1, 0],
          [0, 1, 1]]
}

shape_colors = {
    "I": Color.RED,
    "T": Color.PURPLE,
    "O": Color.CYAN,
    "L": Color.YELLOW,
    "J": Color.MAGENTA,
    "S": Color.BLUE,
    "Z": Color.GREEN
}

def _allelem(iterable, elem):
    return all(e == elem for e in iterable)

def count_empty_toprows(tetrimino):
    counter = 0
    for row in tetrimino.shape:
        if _allelem(row, 0):
            counter += 1
        else:
            break
    return counter

def count_empty_botrows(tetrimino):
    counter = 0
    for row in reversed(tetrimino.shape):
        if _allelem(row, 0):
            counter += 1
        else:
            break
    return counter

def count_empty_leftcols(tetrimino):
    counter = 0
    for col in zip(*tetrimino.shape):
        if _allelem(col, 0):
            counter += 1
        else:
            break
    return counter
        
def count_empty_rightcols(tetrimino):
    counter = 0
    for col in reversed(list(zip(*tetrimino.shape))):
        if _allelem(col, 0):
            counter += 1
        else:
            break
    return counter
