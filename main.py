import pygame

try:
    a, b = map(int, input().split())
    if __name__ == '__main__':
        pygame.init()
        pygame.display.set_caption('Rectangle')
        size = width, height = a, b
        screen = pygame.display.set_mode(size)
        while pygame.event.wait().type != pygame.QUIT:
            screen.fill((0, 0, 0))
            screen.fill(pygame.Color('red'), (1, 1, width - 2, height - 2))
            pygame.display.flip()
        pygame.quit()
except:
    print('Неправильный формат ввода')
