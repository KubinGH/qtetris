import random
from gamecls import Block, Tetrimino, TetriminoOverlap, Board
from shapedata import empty_toprows, empty_leftcols, empty_rightcols

BWIDTH, BHEIGHT = (10, 20)

SCORE_PER_LINES = [0, 40, 100, 300, 1200]

RANDOM_POS_TRIES = 4

class Game:
    def __init__(self, bwidth=BWIDTH, bheight=BHEIGHT):
        self.board = Board(bwidth, bheight)
        self.fboard = self.board.copy()
        self.reset_falling()
        self.last_fpos = self.last_fpos_rot = None
        self.last_fpos_setpoint = self.fpos
        self.next_tetrimino = Tetrimino.random()
        self.swapped_f = False
        self.score = 0

    def reset_falling(self):
        self.ftetrimino = self.fpos = None
        
    def swap_falling(self):
        if self.swapped_f:
            return None
        self.swapped_f = True
        f, n = self.ftetrimino, self.next_tetrimino
        self.ftetrimino, self.next_tetrimino = n, f
        self.fpos = self.random_valid_fpos(self.ftetrimino)
        self.last_fpos = self.last_fpos_rot = self.last_fpos_setpoint = None


    def random_valid_fpos(self, tetrimino):
        row = -(empty_toprows[tetrimino.name])
        colfix_lo = -(empty_leftcols[tetrimino.name])
        colfix_hi = -(tetrimino.width) + empty_rightcols[tetrimino.name]
        possible_cols = list(range(colfix_lo, BWIDTH + colfix_hi + 1))
        random.shuffle(possible_cols)
        for col in possible_cols:
            fits = tetrimino.fits_on(self.board, (col, row))
            if fits:
                return (col, row)
        return None        
    
    def random_valid_tetrimino(self):
        tetrimino = self.next_tetrimino
        self.next_tetrimino = Tetrimino.random()
        for _ in range(4):
            rand_fpos = self.random_valid_fpos(tetrimino)
            if rand_fpos is not None:
                return tetrimino, rand_fpos
        return None

    def process_gravity(self):
        if self.ftetrimino is None:
            return None

        else:
            next_fpos = (self.fpos[0], self.fpos[1] + 1)
            free = self.ftetrimino.fits_on(self.board, next_fpos)
            if free:
                self.fpos = next_fpos
                return "ok"
            else:
                return "hit"

    def gravity_full(self):
        gravity_status = self.process_gravity()
        if gravity_status == "hit":
            self.board.place_tetrimino(self.ftetrimino, self.fpos)
            self.fboard = self.board.copy()
            self.reset_falling()
            self.swapped_f = False

    def get_last_fpos(self):
        fits_on = lambda pos: self.ftetrimino.fits_on(self.board, pos)
        next_fpos = (self.fpos[0], self.fpos[1] + 1)
        free = fits_on(next_fpos)
        if not free: return "hit_already"
        else:
            while free:
                next_fpos = (next_fpos[0], next_fpos[1] + 1)
                free = fits_on(next_fpos)
            return (next_fpos[0], next_fpos[1] - 1)

    def set_last_fpos(self):
        if self.fpos != self.last_fpos_setpoint or  \
               self.ftetrimino.rotation != self.last_fpos_rot:
            self.last_fpos_setpoint = self.fpos
            self.last_fpos_rot = self.ftetrimino.rotation
            self.last_fpos = self.get_last_fpos()

    def check_for_full(self):
        done = False
        lines = 0
        while not done:
            done = True
            to_pop = None
            for i, row in enumerate(self.board.data):
                if all(not block.empty for block in row):
                    lines += 1
                    to_pop = i
                    done = False
                    break
            if to_pop is not None:
                self.board.data.pop(to_pop)
                self.board.data.insert(0, self.board.empty_row())

        self.score += SCORE_PER_LINES[lines]

    def f_rotate(self):
        rotated = self.ftetrimino.rotated()
        if rotated.fits_on(self.board, self.fpos):
            self.ftetrimino = rotated
    
    def f_moveright(self):
        next_pos = (self.fpos[0] + 1, self.fpos[1])
        if self.ftetrimino.fits_on(self.board, next_pos):
            self.fpos = next_pos


    def f_moveleft(self):
        next_pos = (self.fpos[0] - 1, self.fpos[1])
        if self.ftetrimino.fits_on(self.board, next_pos):
            self.fpos = next_pos

if __name__ == "__main__":
    game = Game()
