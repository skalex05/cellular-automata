import pygame
from pygame.math import Vector2
from bitarray import bitarray

from Settings import settings

pygame.init()

clock = pygame.Clock()

screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)

draw_index = int(settings.camera_position.x + settings.grid_size.x * settings.camera_position.y)

cells = set()


def check_cell(x: int, y: int, isCell=True):
    count = 0
    for nx, ny in settings.neighbour_area:
        nx += x
        ny += y
        if nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
            continue
        if (nx, ny) in cells:
            count += 1
        if isCell:
            check_cell(nx, ny, False)


    birth = settings.birth_condition(count)
    if isCell and not (settings.live_condition(count) or birth):
        cells.remove((x, y))
    elif not isCell and birth:
        cells.add((x, y))


def update_cells():
    for c in cells.copy():
        check_cell(*c)


cells.add((int(20 + settings.camera_position.x), int(20 + settings.camera_position.y)))
cells.add((int(20 + settings.camera_position.x - 1), int(20 + settings.camera_position.y + 1)))
cells.add((int(20 + settings.camera_position.x + 1), int(20 + settings.camera_position.y + 1)))
cells.add((int(20 + settings.camera_position.x - 1), int(20 + settings.camera_position.y + 2)))
cells.add((int(20 + settings.camera_position.x + 1), int(20 + settings.camera_position.y + 2)))
cells.add((int(20 + settings.camera_position.x), int(20 + settings.camera_position.y + 3)))
cells.add((int(20 + settings.camera_position.x + 1), int(20 + settings.camera_position.y + 3)))

cells.add((int(50 + settings.camera_position.x), int(50 + settings.camera_position.y)))
cells.add((int(51 + settings.camera_position.x), int(50 + settings.camera_position.y)))
cells.add((int(52 + settings.camera_position.x), int(50 + settings.camera_position.y)))

print(settings)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and settings.fullscreen:
                screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)
                settings.fullscreen = False
            if event.key == pygame.K_F11:
                if settings.fullscreen:
                    screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                settings.fullscreen = not settings.fullscreen
        if event.type == pygame.WINDOWRESIZED:
            settings.screen_size = Vector2(event.x, event.y)

    screen.fill(settings.bg_color)

    for x, y in cells:
        pygame.draw.rect(screen, settings.cell_color,
                         ((x - settings.camera_position.x) * settings.cell_size,
                          (y - settings.camera_position.y) * settings.cell_size,
                          settings.cell_size, settings.cell_size))

    pygame.display.update()

    clock.tick(settings.speed)

    update_cells()
