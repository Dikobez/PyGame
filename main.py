import pygame

try:
    a, b = map(int, input().split())
    if __name__ == '__main__':
        pygame.init()
        pygame.display.set_caption('Rectangle')
        size = width, height = a, b
        screen = pygame.display.set_mode(size)
        while pygame.event.wait().type != pygame.QUIT:
            pygame.draw.rect(screen, pygame.Color('red'), (a + 1, b + 1, a - 2, b - 2), width=0)
            pygame.display.flip()
        pygame.quit()
except:
    print('Неправильный формат ввода')
