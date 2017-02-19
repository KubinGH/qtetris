def _top_nonempty(column):
    result = 0
    for i, block in enumerate(reversed(column)):
        if not block.empty:
            result = i + 1
    return result

def agg_height(board, top_nonempty_list=None):
    if top_nonempty_list is None:
        top_nonempty_list = [_top_nonempty(col) for col in board.columns]
    return sum(top_nonempty_list)

def complete_lines(board):
    count = 0
    for row in board.mask:
        if not any(e for e in row):
            count += 1
    return count

def count_holes(board):
    count = 0
    for col in board.columns:
        found_empty = 0
        for block in reversed(col):
            if block.empty:
                found_empty += 1
            if not block.empty and found_empty:
                count += found_empty
                break
    return count

def _pairs01(seq):
    last = seq[0]
    for item in seq[1:]:
        yield last, item
        last = item

def bumpiness(board, top_nonempty_list=None):
    count = 0
    if top_nonempty_list is None:
        top_nonempty_list = [_top_nonempty(col) for col in board.columns]
    for first_top, second_top in _pairs01(top_nonempty_list):
        count += abs(first_top - second_top)
    return count
