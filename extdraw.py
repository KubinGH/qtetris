import pygame

def draw_rect_alpha(surface, color, rect, thickness):
    assert len(color) == 4, "color needs to be in RGBA format"
    temp_surface = pygame.Surface((rect.width, rect.height))
    rgb, alpha = color[:3], color[3]
    temp_surface.set_alpha(alpha)
    pygame.draw.rect(temp_surface, rgb,
                     pygame.Rect(0, 0, rect.width, rect.height), thickness)  
    surface.blit(temp_surface, (rect.left, rect.top))


def draw_rect(surface, color, rect, thickness=0):
    if len(color) == 3:
        return pygame.draw.rect(surface, color, rect, thickness)
    elif len(color) == 4:
        return draw_rect_alpha(surface, color, rect, thickness)
    else:
        msg = "Unknwon color format of length {0}. ".format(len(color)) + \
              "Use RGB(A)"
        raise ValueError("Unknown color format of length " + str(len(color)))
