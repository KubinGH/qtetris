import pygame
import app_player


pygame.init()

info = pygame.display.Info()
mwidth, mheight = info.current_w, info.current_h

# App config
app_player.AI_CONTROL = True
app_player.AI_CONTROL_VISIBLE = True
app_player.BOARD_SIZE = (10, 20)
app_player.BLOCK_SIZE = 45
if (app_player.BOARD_SIZE[1] + 2) * app_player.BLOCK_SIZE > mheight:
    print("WARNING: Screen is too small!")
    app_player.BLOCK_SIZE = 35
app_player.FULLSCREEN_WINDOW = True
app_player.set_slowmode(True)

# Initialize

screen = app_player.get_screen(fullscreen=app_player.FULLSCREEN_WINDOW)
screen.fill((0, 0, 0))
app = app_player.App(screen, board_size=app_player.BOARD_SIZE)

# Main
app.run()
pygame.quit()
