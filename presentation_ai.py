import pygame
import app_player

# App config
app_player.AI_CONTROL = True
app_player.AI_CONTROL_VISIBLE = True
app_player.BOARD_SIZE = (10, 20)
app_player.BLOCK_SIZE = 45
app_player.FULLSCREEN_WINDOW = True
app_player.set_slowmode(True)

# Initialize
pygame.init()
screen = app_player.get_screen(fullscreen=app_player.FULLSCREEN_WINDOW)
screen.fill((0, 0, 0))
app = app_player.App(screen, board_size=app_player.BOARD_SIZE)

# Main
app.run()
pygame.quit()
