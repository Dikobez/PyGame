import pygame


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Rectangle')
    size = width, height = 800,
    screen = pygame.display.set_mode(size)
    while pygame.event.wait().type != pygame.QUIT:
        screen.fill((0, 255, 0))
        screen.fill(pygame.Color('red'), pygame.Rect(10, 10, 60, 60))
        pygame.display.flip()
    pygame.quit()


