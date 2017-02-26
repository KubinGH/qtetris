def calc_board_posfix(board_size, block_size):
    return (block_size, block_size)

def calc_window_size(board_size, block_size):
    board_size_px = (board_size[0] * block_size, board_size[1] * block_size)
    return (board_size_px[0] + int((6 + 2/3) * block_size),
            board_size_px[1] + 2 * block_size)

def calc_score_pos(board_size, block_size):
    board_size_px = (board_size[0] * block_size, board_size[1] * block_size)
    return (board_size_px[0] + 2 * block_size, 3 * block_size)

def calc_ntbox_pos(board_size, block_size):
    board_size_px = (board_size[0] * block_size, board_size[1] * block_size)
    return (board_size_px[0] + 2 * block_size, int((7 + 1/3) * block_size))
    
