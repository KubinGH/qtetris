class Color:
    BLACK =     (  0,   0,   0)
    WHITE =     (255, 255, 255)

    LGRAY =     (215, 215, 215)
    GRAY =      (170, 170, 170)
    DGRAY =     (115, 115, 115)

    RED =       (255,   0,   0)
    GREEN =     (  0, 255,   0)
    BLUE =      (  0,   0, 255)

    YELLOW =    (255, 255,   0)
    CYAN =      (  0, 255, 255)
    PURPLE =    (255,   0, 255)

    MAGENTA =   (255,   0, 144)

    LBLUE =     (100, 100, 255)
    DBLUE =     (  0,   0, 125)

    COLORS = ["BLACK", "WHITE",
              "LGRAY", "GRAY", "DGRAY",
              "RED", "GREEN", "BLUE",
              "YELLOW", "CYAN", "PURPLE",
              "MAGENTA",
              "LBLUE", "DBLUE"]
    
    @classmethod
    def with_alpha(self, alpha):
        return _ColorWithAlpha(alpha)

    def by_name(self, name):
        return getattr(self, name.upper())

_DUMMY = Color()

class _ColorWithAlpha:
    def __init__(self, alpha):
        self.alpha = alpha
    
    def __getattr__(self, name):
        return _DUMMY.by_name(name) + (self.alpha, )
        
