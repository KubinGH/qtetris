import time

import pygame

import qclock
from colors import Color
from gamecls import TetriminoOverlap
from game import Game
from extdraw import draw_rect

from qgenes import agg_height, complete_lines, count_holes, bumpiness

BOARD_SIZE = (10, 20)
WINDOW_SIZE = (500, 660)
BLOCK_SIZE = 30

BOARD_SIZE_PX = (300, 600)
BOARD_POSFIX = (30, 30)

SCORE_POS = (360, 90)
NTBOX_POS = (360, 220)

NODELAY = False

def set_nodelay(boolean):
    global NODELAY, FPS, GSECS, GSECS_DOWN, MSECS
    NODELAY = boolean
    if NODELAY:
        FPS = GSECS = GSECS_DOWN = MSECS = 0
    else:
        FPS = 120
        GSECS = 0.3
        GSECS_DOWN = 0.1
        MSECS = 0.1
    
def toggle_delay(forced_value=None):
    global NODELAY
    NODELAY = not NODELAY
    set_nodelay(NODELAY)

DBGSECS = 0.1

set_nodelay(NODELAY)


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
                    

            while pausing:
                quitting = self.check_for_quit()
                if quitting: return
                for event in pygame.event.get(pygame.KEYDOWN):
                    if event.key == pygame.K_p:
                        pausing = False
                        break
                        

            moving["down"]  = pressed_keys[pygame.K_DOWN]
            moving["left"]  = pressed_keys[pygame.K_LEFT]
            moving["right"] = pressed_keys[pygame.K_RIGHT]
            
            ## Logic ##
            #Randomize if empty
            if self.ftetrimino is None:
                rand = self.random_valid_tetrimino()
                if rand is None:
                    self.game_over()
                    break
                else:
                    self.ftetrimino, self.fpos = rand

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
                    self.gravity_full()

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
        except pygame.error:
            return True
    
    def game_over(self):
        midx = (WINDOW_SIZE[0] - self.gameovertext.get_width()) / 2
        self.screen.blit(self.gameovertext, (midx, 4))
        pygame.display.flip()
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

    def draw_ghost(self):
        t = (None, "hit_already")
        if self.last_fpos not in t and self.ftetrimino is not None:
            block = self.ftetrimino.block
            for col, row in self.ftetrimino.blocks_on(self.last_fpos):
                x, y = col * BLOCK_SIZE, row * BLOCK_SIZE
                draw_rect(self.board_surface, Color.LBLUE,
                          pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def draw_board(self, board):
        for y, row in enumerate(board):
            for x, block in enumerate(row):
                if block.empty:
                    continue
                fx, fy = x * BLOCK_SIZE, y * BLOCK_SIZE
                self.draw_block_to(self.board_surface, block, fx, fy)
        self.draw_ghost()

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
        self.screen.fill(Color.BLACK)
        self.board_surface.fill(Color.DBLUE)
            
        self.draw_board(self.fboard)
        self.draw_board_to_screen()

        self.draw_info()





if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.SRCALPHA)
    while True:
        screen.fill(Color.BLACK)
        app = App(screen)
        app.run()
        if not app.resetting:
            break
    pygame.quit()
