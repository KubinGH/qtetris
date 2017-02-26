import random
from gamecls import Block, Tetrimino, TetriminoOverlap, Board, fall_pos, random_tetrimino_letter_gen
from qgenes import agg_height, complete_lines, count_holes, bumpiness, fitness
from qutils import get_possible_outcomes, get_possible_boards

BWIDTH, BHEIGHT = (10, 20)

SCORE_PER_LINES = [0, 40, 100, 300, 1200]

class GameOver(Exception): pass

class Game:
    def __init__(self, bwidth=BWIDTH, bheight=BHEIGHT):
        self.board = Board(bwidth, bheight)
        self.reset_falling()
        self.last_fpos = self.last_fpos_rot = None
        self.last_fpos_setpoint = self.fpos
        self.tetrimino_letter_generator = random_tetrimino_letter_gen()
        self.next_tetrimino = Tetrimino.random(self.tetrimino_letter_generator)
        self.swapped_f = False
        self.just_placed_tetrimino = False
        self.score = self.dropped_tetriminos = 0
        self.best_outcome = None

    def reset_falling(self):
        self.ftetrimino = None
        self.fpos = (None, None)
        
    def swap_falling(self):
        if self.swapped_f:
            return None
        self.swapped_f = True
        f, n = self.ftetrimino, self.next_tetrimino
        f = Tetrimino(f.name)
        self.ftetrimino, self.next_tetrimino = n, f
        self.fpos = self.random_valid_fpos(self.ftetrimino)
        self.last_fpos = self.last_fpos_rot = self.last_fpos_setpoint = None


    def random_valid_fpos(self, tetrimino):
        row = tetrimino.rowfix_top
        possible_cols = tetrimino.possible_cols(self.board.width)
        random.shuffle(possible_cols)
        for col in possible_cols:
            fits = tetrimino.fits_on(self.board, (col, row))
            if fits:
                return (col, row)
        return None
    
    def random_valid_tetrimino(self):
        tetrimino = self.next_tetrimino
        self.next_tetrimino = Tetrimino.random(self.tetrimino_letter_generator)
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
            self.just_placed_tetrimino = True
            self.dropped_tetriminos += 1
            self.reset_falling()
            self.swapped_f = False

    def get_last_fpos(self):
        r = fall_pos(self.ftetrimino, self.fpos, self.board)
        return "hit_already" if r[1] == self.fpos[1] else r

    def set_last_fpos(self):
        if self.fpos[0] != self.last_fpos_setpoint[0] or  \
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
            for i, row in enumerate(self.board.mask):
                if all(not block for block in row):
                    lines += 1
                    to_pop = i
                    done = False
                    break
            if to_pop is not None:
                self.board.delete_row(to_pop)

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
            
    def ai_compute_outcomes(self, weights, *, double=True):
        if double:
            outcomes = get_possible_outcomes(self.board, self.ftetrimino)
            if not outcomes:
                return None
            pboards = get_possible_boards(self.board, outcomes)
            max_fitness = float("-inf"); best_outcome = None
            for i, pboard in enumerate(pboards):
                outcomes2 = get_possible_outcomes(pboard, self.next_tetrimino)
                pboards2 = get_possible_boards(pboard, outcomes2)
                fitness_vals = {b: fitness(b, weights) for b in pboards2}
                best_fitness = max(fitness_vals.values())
                if best_fitness > max_fitness:
                    max_fitness = best_fitness              
                    best_outcome = outcomes[i]
            self.best_outcome = best_outcome
        else:
            outcomes = get_possible_outcomes(self.board, self.ftetrimino)
            if not outcomes:
                return None
            pboards = get_possible_boards(self.board, outcomes)
            fitness_vals = {b: fitness(b, weights) for b in pboards}
            best_idx = max(range(len(outcomes)),
                                key=lambda x: fitness_vals[pboards[x]])
            self.best_outcome = outcomes[best_idx]

    def ai_move(self):
        self.fpos = self.best_outcome["start_pos"]
        self.ftetrimino.rotate(self.best_outcome["rotation"])      
    
    def handle_new_falling_tetrimino(self):
        rand = self.random_valid_tetrimino()
        if rand is None:
            return "game_over"
        else:
            self.ftetrimino, self.fpos = rand
            return "ok"

    def handle_gravity(self):
        try:
            self.gravity_full()
        except TetriminoOverlap:
            return "game_over"
        else:
            return "ok"
        
    


if __name__ == "__main__":
    game = Game()
