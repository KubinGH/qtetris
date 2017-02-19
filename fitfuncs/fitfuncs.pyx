cpdef int c_top_nonempty(list column):
    cdef int result = 0
    cdef int i
    cdef int j = -1
    for i in range(len(column) - 1, -1, -1):
        j += 1
        if not column[i].empty:
            result = j + 1
    return result

cpdef int c_agg_height(board, list top_nonempty_list):
    return sum(top_nonempty_list)
    
cpdef int c_complete_lines(board):
    cdef int count = 0
    cdef list row
    for row in board.mask:
        if not any(row):
            count += 1
    return count
    
cpdef int c_count_holes(board, list top_nonempty_list):
    cdef int count = 0
    cdef int i
    cdef int j = -1
    cdef int ctop = 0
    cdef int height = board.height
    cdef list col
    for col in board.columns:
        j += 1
        ctop = top_nonempty_list[j]
        if ctop <= 1: continue
        for i in range(ctop - 1, 0, -1):
            if col[-i].empty:
                count += 1
    return count

cpdef int c_bumpiness(board, list top_nonempty_list):
    cdef int width = len(top_nonempty_list)
    cdef int i, b
    cdef int count = 0
    for a in range(width - 1):
        b = a + 1
        count += abs(top_nonempty_list[a] - top_nonempty_list[b])
    return count       
        