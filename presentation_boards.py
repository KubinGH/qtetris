import time
import pygame
import app_player
from colors import Color
from qclock import Clock

"""
Presentation:
Acquiring possible boards by the AI.

Controls:
Q - Quit
F - Fast mode
P - Pause
"""

# Config
start_delay = 0.4
fast_delay = 0.0001
#min_delay = 0.00001
#delay_acc = 0.0008
fullscreen = True

pygame.init()

info = pygame.display.Info()
mwidth, mheight = info.current_w, info.current_h

# Initialize constants
app_player.set_constants((10, 20), 20)
app_player.WINDOW_SIZE = (app_player.BOARD_SIZE_PX[0] * 2 + app_player.BLOCK_SIZE,
                          app_player.BOARD_SIZE_PX[1] * 2 + app_player.BLOCK_SIZE)
app_player.BOARD_POSFIX = (0, 0)

if mheight < app_player.WINDOW_SIZE[1]:
    print("WARNING: Screen is too small!")
    app_player.set_constants((10, 20), 18)
    app_player.WINDOW_SIZE = (app_player.BOARD_SIZE_PX[0] * 2 + app_player.BLOCK_SIZE,
                              app_player.BOARD_SIZE_PX[1] * 2 + app_player.BLOCK_SIZE)
    app_player.BOARD_POSFIX = (0, 0)
print("Actual window size:", app_player.WINDOW_SIZE)

# Initialize screen
if fullscreen:
    # Top-left
    fix = ((mwidth  - app_player.WINDOW_SIZE[0]) // 2,
           (mheight - app_player.WINDOW_SIZE[1]) // 2)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

else:
    fix = (0, 0)
    screen = pygame.display.set_mode(app_player.WINDOW_SIZE)

pygame.display.set_caption("qTetris - Possible Boards Presentation")
app = app_player.App(screen)

# Get the boards to be shown
app.handle_new_falling_tetrimino()
app.ai_compute_outcomes(app_player.WEIGHTS)
boards = app.cpboards

# Initialize fonts & text surfaces
msfont = pygame.font.SysFont("monospace", 15)
textpos = (2, 2)


# Initialize surfaces
app.screen.fill(Color.BLACK)
app.board_surface.fill(Color.BLACK)

delay = start_delay

clock = Clock()

def zipadd(first, second):
    return tuple(a + b for a, b in zip(first, second))

def groups_iter(iterable, group_size):
    group = []
    for item in iterable:
        group.append(item)
        if len(group) == group_size:
            yield group
            group = []
    if group: yield group

# Main loop
# Iterate in sets of four
groups = list(groups_iter(boards, 4))
for i, quadboard in enumerate(groups):
    # Render new progress-text
    text_progress = msfont.render("{} / {}".format(i + 1, len(groups)),
                                  False, Color.RED)
    
    # Waiting for the next tick    
    quitting = False
    pausing = False
    first_tick = True
    while first_tick or not clock.passed(delay) or pausing:
        first_tick = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                quitting = True; break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                delay = fast_delay if delay == start_delay else start_delay
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pausing = not pausing
        if quitting: break
    if quitting: break
    clock.tick()

    for i, board in enumerate(quadboard):
        # Place different boards in different parts of the screen
        # In this manner:
        # 0 1
        # 2 3
        if   i == 0: posfix = (0, 0)
        elif i == 1: posfix = (app_player.BOARD_SIZE_PX[0] + app_player.BLOCK_SIZE, 0)
        elif i == 2: posfix = (0, app_player.BOARD_SIZE_PX[1] + app_player.BLOCK_SIZE)
        elif i == 3: posfix = zipadd(app_player.BOARD_SIZE_PX, (app_player.BLOCK_SIZE,) * 2)
        # App.draw_board draws to App.board_surface attribute
        app.draw_board(board)
        app.screen.blit(app.board_surface, zipadd(fix, posfix))
        app.board_surface.fill(Color.BLACK)
        app.screen.blit(text_progress, zipadd(fix, textpos))
    pygame.display.flip()
    # Do not clear the screen if this is the last one
    # Somewhat slow comparison, but whatever
    if i != len(groups) - 1: app.screen.fill(Color.BLACK)

while True and not quitting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            break
    else:
        continue
    break

pygame.quit()
