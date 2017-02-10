import time

import pygame

import qclock
from colors import Color
from gamecls import Tetrimino, TetriminoOverlap
from game import Game, GameOver
from extdraw import draw_rect

from qgenes import agg_height, complete_lines, count_holes, bumpiness, fitness
from qutils import get_possible_outcomes, get_possible_boards

BOARD_SIZE = (10, 20)
WINDOW_SIZE = (500, 660)
BLOCK_SIZE = 30

BOARD_SIZE_PX = (300, 600)
BOARD_POSFIX = (30, 30)

SCORE_POS = (360, 90)
NTBOX_POS = (360, 220)

DRAWGRID = True

NODELAY = False
FASTMODE = False

def set_nodelay(boolean):
    global NODELAY, FPS, GSECS, GSECS_DOWN, MSECS
    NODELAY = boolean
    if NODELAY:
        set_fastmode(False)
        FPS = GSECS = GSECS_DOWN = MSECS = 0
    else:
        FPS = 120
        GSECS = 0.3
        GSECS_DOWN = 0.1
        MSECS = 0.1

def toggle_delay():
    global NODELAY
    NODELAY = not NODELAY
    set_nodelay(NODELAY)


def set_fastmode(boolean):
    global FASTMODE, GSECS, GSECS_DOWN
    FASTMODE = boolean
    if FASTMODE:
        set_nodelay(False)
        GSECS = GSECS_DOWN = 0.01
    else:
        GSECS = 0.3
        GSECS_DOWN = 0.1

def toggle_fastmode():
    global FASTMODE
    FASTMODE = not FASTMODE
    set_fastmode(FASTMODE)

DBGSECS = 0.1

set_nodelay(NODELAY)

#aggheight, completelines, holes, bumpiness
AI_HINTS = True
AI_CONTROL = True
WEIGHTS = [-100,
           1000,
           -3000,
           -200]

if AI_CONTROL:
    set_fastmode(True)

class App(Game):
    def __init__(self, screen, *, board_size=BOARD_SIZE):
        super().__init__(*board_size)
        self.window_size = screen.get_size()
        self.screen = screen
        self.resetting = False
        try:
            self.font = pygame.font.SysFont("Corbel", 50)
            self.msgfont = pygame.font.SysFont("Monospace", 25, bold=True)
        except:
            self.font = self.msgfont = pygame.font.Font("freesansbold.ttf", 50)
        self.scoreheader = self.font.render("Score", True, Color.WHITE)
        self.gameovertext = self.msgfont.render("Game Over!", True, Color.RED)
        self.r_next_tetrimino = self.nt_box = None
        
    def run(self):
        self.board_surface = pygame.Surface(BOARD_SIZE_PX)

        qclocks = {"left":      qclock.Clock(),
                   "right":     qclock.Clock(),
                   "gravity":   qclock.Clock(),
                   "draw":      qclock.Clock(),
                   "dbg":       qclock.Clock()}

        moving = {"right": False,
                  "left": False,
                  "down": False}
                      
        do_rotate = False
        self.rscore = None; self.scoretext = None
        pausing = False
        
        clock = pygame.time.Clock()
        done = False
        while not done:
            ## Events ##
            quitting = self.check_for_quit()
            if quitting: return
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        do_rotate = True
                        
                    elif event.key == pygame.K_SPACE:
                        self.swap_falling()
                    
                    elif event.key == pygame.K_p:
                        pausing = True
                    
                    elif event.key == pygame.K_r:
                        self.resetting = True
                        return
                    
                    elif event.key == pygame.K_n:
                        toggle_delay()

                    elif event.key == pygame.K_f:
                        toggle_fastmode()
                    
            #Pause
            while pausing:
                quitting = self.check_for_quit()
                if quitting: return
                #Unpause
                for event in pygame.event.get(pygame.KEYDOWN):
                    if event.key == pygame.K_p:
                        pausing = False
                        break
                        

            moving["down"]  = pressed_keys[pygame.K_DOWN]
            moving["left"]  = pressed_keys[pygame.K_LEFT]
            moving["right"] = pressed_keys[pygame.K_RIGHT]
            
            ## Logic ##
            #New falling tetrimino
            if self.ftetrimino is None:
                rand = self.random_valid_tetrimino()
                if rand is None:
                    self.game_over()
                    break
                else:
                    self.ftetrimino, self.fpos = rand
                    self.outcomes = get_possible_outcomes(self.board, self.ftetrimino)
                    self.pboards = get_possible_boards(self.board, self.outcomes)
                    fitness_fix = count_holes(self.board) * WEIGHTS[2]
                    self.fitness_vals = {b: fitness(b, WEIGHTS) - fitness_fix for b in self.pboards}
                    self.best_idx = max(range(len(self.outcomes)),
                                        key=lambda x: self.fitness_vals[self.pboards[x]])
                    self.best_outcome = self.outcomes[self.best_idx]
                    dct = {(out["start_pos"], out["rotation"]): self.fitness_vals[board]
                           for out, board in zip(self.outcomes, self.pboards)}
                    print("New")
                    for k, v in sorted(dct.items(), key=lambda x: x[1]):
                        print(k, v)
                    if AI_CONTROL:
                        print("Best move fitness:", max(self.fitness_vals.values()))
                        self.fpos = (self.best_outcome["start_pos"][0], self.fpos[1])
                        self.ftetrimino.rotate(self.best_outcome["rotation"])

            #Rotate
            if self.ftetrimino is not None:
                if do_rotate:
                    do_rotate = False
                    self.f_rotate()

            #Moving
            if moving["left"] and qclocks["left"].passed(MSECS):
                qclocks["left"].tick()
                if self.ftetrimino is not None:
                    self.f_moveleft()

            if moving["right"] and qclocks["right"].passed(MSECS):
                qclocks["right"].tick()
                if self.ftetrimino is not None:
                    self.f_moveright()
                    
            #Gravity
            gseconds = GSECS if not moving["down"] else GSECS_DOWN
            if qclocks["gravity"].passed(gseconds):
                qclocks["gravity"].tick()
                if self.ftetrimino is not None:
                    try:
                        self.gravity_full()
                    except GameOver:
                        self.game_over()
                        break

            #Check for full lines
            self.check_for_full()

            #Reset the board
            if self.ftetrimino is not None:
                self.fboard = self.board.on_board(self.ftetrimino, self.fpos)
            else:
                self.fboard = self.board.copy()

            #Last falling tetrimino pos
            if self.ftetrimino is not None:
                self.set_last_fpos()
            
            ## Graphics ##
            self.draw_full()            

            ## End ##

            if qclocks["dbg"].passed(DBGSECS):
                qclocks["dbg"].tick()
            
            pygame.display.flip()
            clock.tick(FPS)

    def check_for_quit(self):
        keys = pygame.key.get_pressed()
        try:
            for event in pygame.event.get(pygame.QUIT):
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return True
            if keys[pygame.K_r]:
                self.resetting = True
                return True
            return False
        except:
            return True
        else:
            return False
    
    def game_over(self):
        midx = (WINDOW_SIZE[0] - self.gameovertext.get_width()) / 2
        self.screen.blit(self.gameovertext, (midx, 4))
        pygame.display.flip()
        if AI_CONTROL:
            time.sleep(1)
            self.resetting = True
            return
        else:
            while True:
                quitting = self.check_for_quit()
                if quitting:
                    return

    @staticmethod
    def draw_block_to(surface, block, x, y, alpha=None):
        color1 = block.color
        color2 = Color.BLACK
        if alpha is not None:
            color1 = color1 + (alpha, )
            color2 = color2 + (alpha, )
        #interior        
        draw_rect(surface, color1,
                  pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE))
        #edges
        draw_rect(surface, color2,
                  pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE), 2)

    @staticmethod
    def draw_outline(surface, x, y, color):
        draw_rect(surface, color,
                  pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_ghost(self):
        t = (None, "hit_already")
        if self.last_fpos not in t and self.ftetrimino is not None:
            block = self.ftetrimino.block
            for col, row in self.ftetrimino.blocks_on(self.last_fpos):
                x, y = col * BLOCK_SIZE, row * BLOCK_SIZE
                self.draw_outline(self.board_surface, x, y, Color.LBLUE)
                self.drawn_outlines.append(((col, row), Color.LBLUE))

    def draw_hint(self):
        t = Tetrimino(self.best_outcome["name"])
        t.rotate(self.best_outcome["rotation"])
        for col, row in t.blocks_on(self.best_outcome["fall_pos"]):
            x, y = col * BLOCK_SIZE, row * BLOCK_SIZE
            if ((col, row), Color.LBLUE) not in self.drawn_outlines:
                color = Color.RED
            else:
                color = Color.PURPLE
            self.draw_outline(self.board_surface, x, y, color)
            self.drawn_outlines.append(((col, row), color))
        
    
    def draw_board(self, board):
        for y, row in enumerate(board):
            for x, block in enumerate(row):
                fx, fy = x * BLOCK_SIZE, y * BLOCK_SIZE
                if block.empty:
                    if DRAWGRID:
                        self.draw_outline(self.board_surface, fx, fy,
                                          Color.EBLUE)
                else:
                    self.draw_block_to(self.board_surface, block, fx, fy)
        self.draw_ghost()
        if AI_HINTS:
            self.draw_hint()

    def draw_board_to_screen(self):
        self.screen.blit(self.board_surface, BOARD_POSFIX)

    def draw_nt_box(self):
        self.screen.blit(self.nt_box, NTBOX_POS)
        
    def draw_next_tetrimino(self):
        if self.r_next_tetrimino == self.next_tetrimino and \
                                    self.nt_box is not None:
            self.draw_nt_box()
            return
        nt = self.next_tetrimino
        ntbox_size = (4, 5)
        ntbox_size_px = (BLOCK_SIZE * ntbox_size[0], BLOCK_SIZE * ntbox_size[1])
        self.nt_box = pygame.Surface(ntbox_size_px)
        draw_rect(self.nt_box, Color.BLUE,
                  pygame.Rect((0, 0), ntbox_size_px), 2)

        bounds = nt.get_bounds()
        left, right, top, bottom = bounds
        awidth, aheight = nt.get_actsize(bounds)
        colfix = (ntbox_size[0] - awidth) / 2 - left
        rowfix = (ntbox_size[1] - aheight) / 2 - top
        nt_pos = (colfix * BLOCK_SIZE, rowfix * BLOCK_SIZE)
        for col, row in nt.blocks_on():
            this_pos = (nt_pos[0] + col * BLOCK_SIZE,
                        nt_pos[1] + row * BLOCK_SIZE)
            self.draw_block_to(self.nt_box, nt.block, *this_pos)
        self.r_next_tetrimino = self.next_tetrimino
        self.draw_nt_box()


    def draw_info(self):
        if self.rscore != self.score:
            self.rscore = self.score
            self.scoretext = self.font.render(str(self.rscore),
                                                   True, Color.WHITE)

        self.screen.blit(self.scoreheader, SCORE_POS)
        score_pos2 = (SCORE_POS[0],
                      SCORE_POS[1] + self.scoreheader.get_height() + 4)
        self.screen.blit(self.scoretext, score_pos2)

        self.draw_next_tetrimino()
        
    def draw_full(self):
        self.drawn_outlines = []
        
        self.screen.fill(Color.BLACK)
        self.board_surface.fill(Color.DBLUE)
            
        self.draw_board(self.fboard)
        self.draw_board_to_screen()

        self.draw_info()





if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SRCALPHA)
    hiscore = 0
    while True:
        screen.fill(Color.BLACK)
        app = App(screen)
        app.run()
        if app.score > hiscore:
            hiscore = app.score
            print("New high score:", hiscore)
        print("High score:", hiscore)
        if not app.resetting:
            break
    pygame.quit()
