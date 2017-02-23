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
    PURPLEW =    (255,   0, 255)

    MAGENTA =   (255,   0, 144)
    PINK =      (255,  51,  80)
    PURPLE =    (180,   0, 180)

    LBLUE =     (100, 100, 255)
    DBLUE =     (  0,   0, 125)
    EBLUE =     (  0,   0, 100)

    COLORS = ["BLACK", "WHITE",
              "LGRAY", "GRAY", "DGRAY",
              "RED", "GREEN", "BLUE",
              "YELLOW", "CYAN", "PURPLEW",
              "MAGENTA", "PINK", "PURPLE",
              "LBLUE", "DBLUE", "EBLUE"]
    
    @classmethod
    def with_alpha(self, alpha):
        return _ColorWithAlpha(alpha)

    def by_name(self, name):
        name_upper = name.upper()
        assert name_upper in self.COLORS
        return getattr(self, name_upper)

_DUMMY = Color()

class _ColorWithAlpha:
    def __init__(self, alpha):
        self.alpha = alpha
    
    def __getattr__(self, name):
        return _DUMMY.by_name(name) + (self.alpha, )
        
