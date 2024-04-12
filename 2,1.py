import pygame

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Желтые круги')
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    running = True
    pr = 0
    rel = 1
    clock = pygame.time.Clock()
    while running:
        screen.fill((0, 0, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                pr = rel = 0
        while rel != 1:
            pygame.draw.circle(screen, (255, 255, 0), pos, pr)
            pygame.display.flip()
            pr += 10
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    rel = 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    screen.fill((0, 0, 255))
                    pygame.display.flip()
                    pos = event.pos
                    pr = 0
    pygame.quit()