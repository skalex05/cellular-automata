import pygame
import pygame_gui
from pygame.math import Vector2
import time
from Settings import settings
from Gui import UI

pygame.init()
pygame.display.set_caption("Cellular Automata")
icon = pygame.image.load("icon.ico")
pygame.display.set_icon(icon)

clock = pygame.Clock()

screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)

ui = UI(settings)
settings.settings_panel = ui.settings_panel

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

    if settings.birth_condition(count) and (x, y):
        cells.add((x, y))
        add_cells_to_frontier(x, y)

def check_cell(old_cells: set, x: int, y: int):
    global cells, frontier

    count = 0
    if settings.symmetrical_area:
        for nx, ny in settings.neighbour_area:
            nx += x
            ny += y
            count += (nx, ny) in old_cells
            if (nx, ny) in old_cells or nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
                continue
            check_empty(old_cells, nx, ny)
    else:
        for nx, ny in settings.neighbour_area:
            nx += x
            ny += y
            if nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
                continue
            count += (nx, ny) in old_cells

    if not settings.live_condition(count):
        cells.remove((x, y))
        add_cells_to_frontier(x, y)

    if not settings.symmetrical_area:
        for nx, ny in [(-nx, -ny) for nx, ny in settings.neighbour_area]:
            nx += x
            ny += y
            if (nx, ny) in old_cells or nx < 0 or nx >= settings.grid_size.x or ny < 0 or ny >= settings.grid_size.y:
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
time_delta = 0

while 1:
    ft = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and settings.fullscreen:
                screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)
                settings.fullscreen = False
            if event.key == pygame.K_F11:
                if settings.fullscreen:
                    screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    settings.screen_update = True
                    size_x, size_y = screen.get_size()
                    settings.screen_size = Vector2(size_x, size_y)
                settings.fullscreen = not settings.fullscreen
        elif event.type == pygame.WINDOWRESIZED:
            ui.manager.set_window_resolution((event.x, event.y))
            settings.screen_size = Vector2(event.x, event.y)
            ui.settings_panel.set_dimensions((ui.panel_width, settings.screen_size.y))
            settings.screen_update = True
        elif event.type == pygame.WINDOWRESTORED:
            settings.screen_update = True
        elif event.type == pygame.MOUSEWHEEL:
            try:
                mouse_pos = Vector2(pygame.mouse.get_pos())
                old_cursor_pos = mouse_pos / settings.cell_size
                settings.cell_size *= 2 ** event.y
                new_cursor_pos = mouse_pos / settings.cell_size
                dif = old_cursor_pos - new_cursor_pos
                settings.camera_position = settings.camera_position + dif
                if not cam_moving:
                    settings.camera_position = Vector2(int(settings.camera_position.x), int(settings.camera_position.y))
                settings.screen_update = True
            except ValueError:
                pass
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            objectID = event.ui_element.object_ids[-1]
            if objectID == "#Minimise_Button":
                ui.panel_minimised = not ui.panel_minimised

        ui.manager.process_events(event)

    mouse_states = pygame.mouse.get_pressed()

    mouse_pos = Vector2(pygame.mouse.get_pos())

    if mouse_states[1]:
        settings.screen_update = True
        if not cam_moving:
            cam_moving = True
            cam_move_start = pygame.mouse.get_pos()
            cam_pos_on_move_start = settings.camera_position

        mouse_movement = mouse_pos - cam_move_start
        mouse_movement = Vector2(mouse_movement) / settings.cell_size

        settings.camera_position = cam_pos_on_move_start - mouse_movement
    elif cam_moving:
        settings.screen_update = True
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
        st = time.time()
        update_cells()
        #print(f"updt: {time.time()-st:.04f}", f"fnts: {len(frontier)}")
    st = time.time()

    draw_bound_x = (settings.camera_position.x - 1, settings.camera_far_pos.x)
    draw_bound_y = (settings.camera_position.y - 1, settings.camera_far_pos.y)

    if settings.screen_update:
        screen.fill(settings.bg_color)
        settings.screen_update = False

        for x, y in cells:

            if (x < draw_bound_x[0] or x > draw_bound_x[1]
                    or y < draw_bound_y[0] or y > draw_bound_y[1]):
                continue

            pygame.draw.rect(screen, settings.cell_color,
                             ((x - settings.camera_position.x) * settings.cell_size,
                              (y - settings.camera_position.y) * settings.cell_size,
                              settings.cell_size, settings.cell_size))

        pygame.display.update((0, 0, settings.settings_panel.get_abs_rect().x, settings.screen_size.y))

    else:
        for x, y in frontier:
            if (x < draw_bound_x[0] or x > draw_bound_x[1]
                                       or y < draw_bound_y[0] or y > draw_bound_y[1]):
                continue
            col = settings.cell_color
            if (x, y) not in cells:
                col = settings.bg_color

            r = ((x - settings.camera_position.x) * settings.cell_size,
                              (y - settings.camera_position.y) * settings.cell_size,
                              settings.cell_size, settings.cell_size)
            pygame.draw.rect(screen, col, r)
            pygame.display.update(r)

    ui.manager.draw_ui(screen)
    ui.manager.update(time_delta)
    pygame.display.update(ui.settings_panel.get_abs_rect())
    print(settings.screen_size_in_cells)
    t = time.time()
    #print(f"draw: {t - st:.4f}", f"frame: {t - ft:.4f}")

    time_delta = clock.tick(settings.speed)
