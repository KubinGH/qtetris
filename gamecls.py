import random
import itertools

from colors import Color
from shapedata import shape_names, shapes, shape_colors, pc_blocks_on, \
                      count_empty_toprows, \
                      count_empty_botrows, \
                      count_empty_leftcols, \
                      count_empty_rightcols

BSIZE = (10, 20)
BWIDTH, BHEIGHT = BSIZE

class TetriminoOverlap(Exception): pass

class Block:
    def __init__(self, color, *, empty=False):
        self.color = color
        self.empty = empty

    def __repr__(self):
        if not self.empty:
            return "<Block({0})>".format(self.color)
        else:
            return "<empty Block>"
        
    @classmethod
    def emptyblock(cls):
        return Block(None, empty=True)

    def __bool__(self):
        return not self.empty

emptyblock_b = Block.emptyblock()

def tetrimino_to_board(tetrimino, o_board, topleft, docopy=True):
    if docopy:  board = o_board.copy()
    else:       board = o_board 
    left, top = topleft
    for col, row in tetrimino.blocks_on():
        if tetrimino.shape[row][col]:
            bcol, brow = col + left, row + top
            if board[bcol, brow]: raise TetriminoOverlap()
            if brow < 0 or bcol < 0: raise IndexError("Negative index")
            board[bcol, brow] = tetrimino.block

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

def random_tetrimino_letter_gen():
    return permutation_random_generator(shape_names)

random_tetrimino_letter = random_tetrimino_letter_gen()

class Tetrimino:
    def __init__(self, shapename, shapes=shapes, colors=shape_colors, rotation=0):
        self.name = shapename
        self.shape = shapes[self.name]
        self.color = colors[self.name]
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
    def random(cls, names=shape_names, generator=random_tetrimino_letter):
        letter = next(generator)
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
        return Block(self.color)

    def _compute_blocks_on(self, topleft=(0, 0)):
        left, top = topleft
        for row in range(self.height):
            for col in range(self.width):
                if self.shape[row][col]:
                    yield (col + left, row + top)

    def blocks_on(self, topleft=(0, 0)):
        blocks = pc_blocks_on[self.name][self.rotation]
        if topleft != (0, 0):
            lt, tp = topleft
            return [(a + lt, b + tp) for a, b in blocks]
        else:
            return blocks

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
        for bcol, brow in self.blocks_on(topleft):
            if not 0 <= brow < board.height or not 0 <= bcol < board.width:
                return False
            elif not board.isempty((bcol, brow)):
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
    def __init__(self, width=BWIDTH, height=BHEIGHT, *, make_empty=True):
        self.width, self.height = width, height
        self.data = [self.empty_row for _ in range(self.height)] if make_empty else None
        self.mask = self.empty_mask() if make_empty else None

    @property
    def empty_row(self):
        return [emptyblock_b for _ in range(self.width)]

    @property
    def empty_mrow(self):
        return [True for _ in range(self.width)]
    
    def empty_mask(self):
        return [self.empty_mrow for _ in range(self.height)]

    @staticmethod
    def make_mask(data):
        return [[obj.empty for elem in row] for row in data]

    @classmethod
    def from_iterable(cls, iterable):
        data = [[item for item in row] for row in iterable]
        board = Board(len(data[0]), len(data))
        board.data = data
        board.mask = make_mask(data)
        return board

    @classmethod
    def from_param(cls, width, height, data, mask):
        obj = cls(width, height, make_empty=False)
        obj.data = data
        obj.mask = mask
        return obj

    def copy(self):
        datacopy = [row.copy() for row in self.data]
        maskcopy = [row.copy() for row in self.mask]
        result = Board.from_param(self.width, self.height, datacopy, maskcopy)
        return result

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
        col, row = index
        if col is not None:
            return self.data[row][col]
        else:
            return self.data[row]
  
    def __setitem__(self, index, obj):
        col, row = index
        if col is not None:
            assert isinstance(obj, Block), "Board can only contain Blocks"
            self.data[row][col] = obj
            self.mask[row][col] = obj.empty
        else:
            print("row set")
            self.data[row] = obj

    def isempty(self, index):
        col, row = index
        return self.mask[row][col]

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
        self.data = result.data; self.mask = result.mask

    def delete_row(self, row_idx):
        self.data.pop(row_idx); self.data.insert(0, self.empty_row)
        self.mask.pop(row_idx); self.mask.insert(0, self.empty_mrow)


def fall_pos(tetrimino, startpos, board):
    def fits(pos): return tetrimino.fits_on(board, pos)
    def inc_height(pos): return (pos[0], pos[1] + 1)
    cpos = startpos
    while fits(cpos):
        cpos = inc_height(cpos)
    if cpos == startpos:
        raise TetriminoOverlap
    return (cpos[0], cpos[1] - 1)
