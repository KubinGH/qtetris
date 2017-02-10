from gamecls import Tetrimino, TetriminoOverlap, fall_pos
from shapedata import shape_names

def all_rotations(tetrimino):
    result = []
    for i in range(4):
        this = tetrimino.rotated(i)
        if this.shape not in [r.shape for r in result]:
            result.append(this)
    return result

rotations = {k: all_rotations(Tetrimino(k)) for k in shape_names}
    
def get_possible_outcomes(board, tetrimino):
    result = []
    for rtetri in rotations[tetrimino.name]:
        row = -rtetri.rowfix_top
        for col in rtetri.possible_cols(board.width):
            start = (col, row)
            try:
                fall = fall_pos(rtetri, start, board)
            except TetriminoOverlap:
                pass
            else:
                result.append({"name": rtetri.name,
                               "rotation": rtetri.rotation,
                               "fall_pos": fall,
                               "start_pos": start}) 
    return result

def get_possible_boards(board, outcomes):
    result = []
    for outcome in outcomes:
        tetrimino = Tetrimino(outcome["name"])
        tetrimino.rotate(outcome["rotation"])
        this_board = board.on_board(tetrimino, outcome["fall_pos"])
        result.append(this_board)
    return result
