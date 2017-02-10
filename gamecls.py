import random
import itertools

from colors import Color
from shapedata import shape_names, shapes, shape_colors, \
                      count_empty_toprows, \
                      count_empty_botrows, \
                      count_empty_leftcols, \
                      count_empty_rightcols
                    

BSIZE = (10, 20)
BWIDTH, BHEIGHT = BSIZE

class TetriminoOverlap(Exception): pass

class Block:
    def __init__(self, color, num, empty=False):
        self.color = color
        self.num = num
        self.empty = empty

    def __repr__(self):
        if not self.empty:
            return "<Block({0}, {1})>".format(self.color, self.num)
        else:
            return "<empty Block>"
        
    @classmethod
    def emptyblock(cls):
        return Block(None, 0, empty=True)

    def __bool__(self):
        return not self.empty


def tetrimino_to_board(tetrimino, o_board, topleft, docopy=True):
    if docopy:  board = o_board.copy()
    else:       board = o_board 
    left, top = topleft
    for col, row in tetrimino.blocks_on():
        if tetrimino.shape[row][col]:
            bcol, brow = col + left, row + top
            if board[brow][bcol]: raise TetriminoOverlap()
            if brow < 0 or bcol < 0: raise IndexError("Negative index")
            board[brow][bcol] = tetrimino.block

    return board

_FORCEDSEQ = []
_DISABLED = []

def permutation_random_generator(sequence, _forced=_FORCEDSEQ, _disabled=_DISABLED):
    for item in _forced:
        yield item
    while True:
        cseq = [item for item in sequence]
        random.shuffle(cseq)
        for item in cseq:
            if item not in _disabled:
                yield item

random_tetrimino_letter = permutation_random_generator(shape_names)

class Tetrimino:
    tnums = itertools.count(1)
    def __init__(self, shapename, shapes=shapes, colors=shape_colors, rotation=0):
        self.name = shapename
        self.shape = shapes[self.name]
        self.color = colors[self.name]
        self.num = next(Tetrimino.tnums)
        self.rotation = 0

    def __repr__(self):
        return "<Tetrimino({0})>".format(self.name)

    def __eq__(self, other):
        if not isinstance(other, Tetrimino):
            return False
        return self.shape == other.shape and \
               self.color == other.color and \
               self.rotation == other.rotation
        
    def copy(self):
        obj = Tetrimino.from_param(self.shape, self.color, self.rotation)
        obj.name = self.name
        return obj
        
    @classmethod
    def from_param(cls, shape, color):
        nonedict = {None: None}
        obj = cls(None, nonedict, nonedict)
        obj.name = None
        obj.shape = shape
        obj.color = color
        obj.rotation = 0
        return obj
    
    @classmethod
    def random(cls, names=shape_names):
        letter = next(random_tetrimino_letter)
        return cls(letter)

    @property
    def width(self):
        return len(self.shape[0])

    @property
    def height(self):
        return len(self.shape)

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def block(self):
        return Block(self.color, self.num)

    def blocks_on(self, topleft=(0, 0)):
        left, top = topleft
        for row in range(self.height):
            for col in range(self.width):
                if self.shape[row][col]:
                    yield (col + left, row + top)

    def get_bounds(self):
        lft = top = float("INF")
        rgt = bot = -float("INF")
        for block in self.blocks_on():
            lft = min(lft, block[0])
            rgt = max(rgt, block[0] + 1)
            top = min(top, block[1])
            bot = max(bot, block[1] + 1)
        return lft, rgt, top, bot
        
    def get_actsize(self, bounds=None):
        lft, rgt, top, bot = self.get_bounds() if bounds is None else bounds
        return (rgt - lft, bot - top)
            
    def actwidth(self):
        return self.actsize()[0]

    def actheight(self):
        return self.actsize()[1]
    
    def to_board(self, o_board, topleft):
        return tetrimino_to_board(self, o_board, topleft)

    def fits_on(self, board, topleft):
        left, top = topleft
        for col, row in self.blocks_on():
            bcol, brow = col + left, row + top
            if brow < 0 or bcol < 0:
                return False
            elif bcol >= board.width or brow >= board.height:
                return False
            elif not board[brow][bcol].empty:
                return False
        return True
                
    def rotated(self, times=1):
        if times > 0:
            rotate = lambda shape: list(list(row) for row in zip(*shape[::-1]))
        elif times < 0:
            rotate = lambda shape: list(list(row) for row in zip(*shape))[::-1]

        i = -1 if times < 0 else 1
        rotation = self.rotation
        shape = self.shape
        for _ in range(abs(times)):
            rotation += i
            shape = rotate(shape)
        rotation = (rotation + 4) % 4

        obj = Tetrimino.from_param(shape, self.color)
        obj.name = self.name
        obj.rotation = rotation
        return obj

    def rotate(self, times=1):
        obj = self.rotated(times)
        self.rotation = obj.rotation
        self.shape = obj.shape

    @property
    def rowfix_top(self):
        return count_empty_toprows(self)

    @property
    def rowfix_bot(self):
        return count_empty_botrows(self)

    @property
    def colfix_left(self):
        return count_empty_leftcols(self)

    @property
    def colfix_right(self):
        return count_empty_rightcols(self)

    def possible_cols(self, board_width):
        return list(range(-self.colfix_left,
                          board_width - self.width + self.colfix_right + 1))

class Board:
    def __init__(self, width=BWIDTH, height=BHEIGHT):
        self.width, self.height = width, height
        self.data = [self.empty_row() for _ in range(self.height)]

    def empty_row(self):
        return [Block.emptyblock() for _ in range(self.width)]

    @classmethod
    def from_iterable(cls, iterable):
        data = []
        for row in iterable:
            data.append([])
            for item in row:
                data[-1].append(item)
        board = Board(len(data[0]), len(data))
        board.data = data
        return board

    def copy(self):
        return Board.from_iterable(self)
        
    def __repr__(self):
        return "<Board({0}, {1})>".format(self.width, self.height)

    def pprint(self, byempty=True):
        for row in self.data:
            if byempty:
                print([1 if not block.empty else 0 for block in row])
            else:
                print(row)
        
    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, obj):
        self.data[index] = obj

    @property
    def rows(self):
        return self.data

    @property
    def columns(self):
        return [list(c) for c in zip(*self.data)]

    def on_board(self, tetrimino, topleft):
        return tetrimino_to_board(tetrimino, self, topleft)

    def place_tetrimino(self, tetrimino, topleft):
        result = tetrimino_to_board(tetrimino, self, topleft)
        self.data = result.data


def fall_pos(tetrimino, startpos, board):
    def fits(pos): return tetrimino.fits_on(board, pos)
    def inc_height(pos): return (pos[0], pos[1] + 1)
    cpos = startpos
    while fits(cpos):
        cpos = inc_height(cpos)
    if cpos == startpos:
        raise TetriminoOverlap
    return (cpos[0], cpos[1] - 1)
