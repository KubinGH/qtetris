def c_top_nonempty(column):
    result = 0
    for i, block in enumerate(reversed(column)):
        if not block.empty:
            result = i + 1
    return result

def c_agg_height(top_nonempty_list):
    return sum(top_nonempty_list)

def c_complete_lines(mask):
    count = 0
    for row in mask:
        if not any(e for e in row):
            count += 1
    return count

def c_count_holes(columns, _):
    count = 0
    for col in columns:
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

def c_bumpiness(top_nonempty_list):
    count = 0
    for first_top, second_top in _pairs01(top_nonempty_list):
        count += abs(first_top - second_top)
    return count
