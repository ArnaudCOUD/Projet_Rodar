import pygame
import math

BLACK = (0, 0, 0, 255)
BLUE = (0, 0, 255, 255)

def distance(point, angle, DISPLAYSURF):
    x, y = point[0],point[1]
    step_size = 1  # Ajustez la taille du pas selon votre besoin

    try:
        while math.hypot(point[0]-x, point[1]-y) < 400:
            x += step_size * math.cos(math.radians(angle))
            y += step_size * math.sin(math.radians(-angle))

            pixel_color = DISPLAYSURF.get_at((round(x), round(y)))
            if pixel_color ==BLACK : #in ((0, 0, 0, 255), (128, 0, 128, 255)):
                pygame.draw.circle(DISPLAYSURF, BLUE, (round(x), round(y)), 3)
                pygame.draw.line(DISPLAYSURF,(0,0,255),point,(x,y))
                return (math.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2))*12/400
                break
        
        return 0
    
    except IndexError:
        return 0
