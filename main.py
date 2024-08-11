import pygame
from pygame.math import Vector2
import time

from Settings import settings

pygame.init()

clock = pygame.Clock()

screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)

cells = set()
frontier = set()


def add_cells_to_frontier(x, y):
    if settings.symmetrical_area:
        neighbours = settings.neighbour_area
    else:
        neighbours = settings.neighbour_area + [(-nx, -ny) for nx, ny in settings.neighbour_area]
    for nx, ny in neighbours:
        nx += x
        ny += y
        if (nx, ny) in cells:
            frontier.add((nx, ny))
    frontier.add((x, y))


def check_empty(old_cells: set, x: int, y: int):
    count = 0
    for nx, ny in settings.neighbour_area:
        nx += x
        ny += y
        if nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
            continue
        count += (nx, ny) in old_cells

    if settings.birth_condition(count):
        cells.add((x, y))
        add_cells_to_frontier(x, y)


def check_cell(old_cells: set, x: int, y: int):
    global cells, frontier

    count = 0
    for nx, ny in settings.neighbour_area:
        nx += x
        ny += y
        if nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
            continue
        count += (nx, ny) in old_cells

        if settings.symmetrical_area and (nx, ny) not in cells:
            check_empty(old_cells, nx, ny)

    if not settings.live_condition(count):
        cells.remove((x, y))
        add_cells_to_frontier(x, y)

    if not settings.symmetrical_area:
        for nx, ny in [(-nx, -ny) for nx, ny in settings.neighbour_area]:
            nx += x
            ny += y
            if nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
                continue
            check_empty(old_cells, nx, ny)


def update_cells():
    global frontier
    old_cells = cells.copy()
    old_frontier = frontier.copy()
    frontier = set()
    for x, y in old_frontier:
        if (x, y) in old_cells:
            check_cell(old_cells, x, y)
        else:
            check_empty(old_cells, x, y)


cam_moving = False
cam_move_start = None
cam_pos_on_move_start = None
screen_update = True

while 1:
    ft = time.time()
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
                    screen_update = True
                    size_x, size_y = screen.get_size()
                    settings.screen_size = Vector2(size_x, size_y)
                settings.fullscreen = not settings.fullscreen
        if event.type == pygame.WINDOWRESIZED:
            settings.screen_size = Vector2(event.x, event.y)
            screen_update = True
        if event.type == pygame.MOUSEWHEEL:
            try:
                mouse_pos = Vector2(pygame.mouse.get_pos())
                old_cursor_pos = mouse_pos / settings.cell_size
                settings.cell_size *= 2 ** event.y
                new_cursor_pos = mouse_pos / settings.cell_size
                dif = old_cursor_pos - new_cursor_pos
                settings.camera_position = settings.camera_position + dif
                if not cam_moving:
                    settings.camera_position = Vector2(int(settings.camera_position.x), int(settings.camera_position.y))
                screen_update = True
            except ValueError:
                pass

    mouse_states = pygame.mouse.get_pressed()

    mouse_pos = Vector2(pygame.mouse.get_pos())

    if mouse_states[1]:
        screen_update = True
        if not cam_moving:
            cam_moving = True
            cam_move_start = pygame.mouse.get_pos()
            cam_pos_on_move_start = settings.camera_position

        mouse_movement = mouse_pos - cam_move_start
        mouse_movement = Vector2(mouse_movement) / settings.cell_size

        settings.camera_position = cam_pos_on_move_start - mouse_movement
    elif cam_moving:
        screen_update = True
        cam_moving = False
        settings.camera_position = Vector2(int(settings.camera_position.x), int(settings.camera_position.y))

    cursor_pos = settings.camera_position + mouse_pos / settings.cell_size
    cursor_pos = Vector2(int(cursor_pos.x), int(cursor_pos.y))
    if mouse_states[0]:
        cells.add(tuple(cursor_pos))
        add_cells_to_frontier(cursor_pos.x, cursor_pos.y)
    elif mouse_states[2]:
        cell = tuple(cursor_pos)
        if cell in cells:
            cells.remove(cell)
            add_cells_to_frontier(*cell)
    else:
        update_cells()
    st = time.time()

    draw_bound_x = (settings.camera_position.x - 1, settings.camera_far_pos.x)
    draw_bound_y = (settings.camera_position.y - 1, settings.camera_far_pos.y)

    if screen_update:
        screen.fill(settings.bg_color)
        screen_update = False

        for x, y in cells:

            if (x < draw_bound_x[0] or x > draw_bound_x[1]
                    or y < draw_bound_y[0] or y > draw_bound_y[1]):
                continue

            pygame.draw.rect(screen, settings.cell_color,
                             ((x - settings.camera_position.x) * settings.cell_size,
                              (y - settings.camera_position.y) * settings.cell_size,
                              settings.cell_size, settings.cell_size))
    else:
        for x, y in frontier:
            if (x < draw_bound_x[0] or x > draw_bound_x[1]
                                       or y < draw_bound_y[0] or y > draw_bound_y[1]):
                continue
            col = settings.cell_color
            if (x, y) not in cells:
                col = settings.bg_color
            pygame.draw.rect(screen, col,
                             ((x - settings.camera_position.x) * settings.cell_size,
                              (y - settings.camera_position.y) * settings.cell_size,
                              settings.cell_size, settings.cell_size))

    pygame.display.update()
    t = time.time()
    print(f"draw: {t - st:.4f}", f"frame: {t - ft:.4f}")

    clock.tick(settings.speed)
