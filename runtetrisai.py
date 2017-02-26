import argparse
import pygame

import sys; sys.path.append(r"C:\Users\Admin\Desktop\qTetris")
import app_player

parser = argparse.ArgumentParser()
parser.add_argument("-width", dest="width", type=int, nargs="?", default=10,
                    help="Width of the tetris board")
parser.add_argument("-height", dest="height", type=int, nargs="?", default=20,
                    help="Height of the tetris board")
parser.add_argument("-blocksize", type=int, dest="blocksize", default=30,
                    help="Size (in pixels) of drawn blocks")
parser.add_argument("-fullscreen", type=bool, dest="fullscreen", default=False,
                    help="Set the window to fullscreen")

args = parser.parse_args()

app_player.AI_CONTROL = True
app_player.AI_CONTROL_VISIBLE = True
app_player.BOARD_SIZE = (args.width, args.height)
app_player.BLOCK_SIZE = args.blocksize
app_player.FULLSCREEN_WINDOW = args.fullscreen

pygame.init()
screen = app_player.get_screen(fullscreen=args.fullscreen)
screen.fill((0, 0, 0))
app = app_player.App(screen, board_size=app_player.BOARD_SIZE)
app.run()
