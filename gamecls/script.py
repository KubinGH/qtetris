from shapedata import *
import gamecls

for name in shape_names:
    t = gamecls.Tetrimino(name)
    print('    "{}": '.format(name) + "{")
    for i in range(4):
        print("        {}: {},".format(i, t.lowest_block_pos()))
        t.rotate()
    print("    },")
