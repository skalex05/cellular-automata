import pygame
import pygame_gui
from pygame.math import Vector2
from pygame.color import Color
from Settings import settings
from Gui import UI

pygame.init()
pygame.display.set_caption("Cellular Automata")
icon = pygame.image.load("icon.ico")
pygame.display.set_icon(icon)

clock = pygame.Clock()

screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)

ui = UI(settings)
ui.draw()

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

    if settings.birth_truth_table[count]:
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

    if not settings.live_truth_table[count]:
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


def zoom(new_cell_size, zoom_toward):
    old_cursor_pos = zoom_toward // settings.cell_size
    settings.cell_size = new_cell_size
    new_cursor_pos = zoom_toward // settings.cell_size
    dif = old_cursor_pos - new_cursor_pos
    settings.camera_position = settings.camera_position + dif
    if not cam_moving:
        settings.camera_position = Vector2(settings.camera_position.x, settings.camera_position.y)
    settings.screen_update = True



cam_moving = False
cam_move_start = None
cam_pos_on_move_start = None
time_delta = 0

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and settings.fullscreen:
                screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)
                settings.fullscreen = False
            elif event.key == pygame.K_F11:
                if settings.fullscreen:
                    screen = pygame.display.set_mode(settings.screen_size, pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    settings.screen_update = True
                    size_x, size_y = screen.get_size()
                    settings.screen_size = Vector2(size_x, size_y)
                settings.fullscreen = not settings.fullscreen
            elif event.key == pygame.K_r and event.mod & pygame.KMOD_LCTRL:
                cells = set()
                frontier = set()
                settings.screen_update = True
            elif event.key == pygame.K_p:
                settings.paused = not settings.paused
        elif event.type == pygame.WINDOWRESIZED:
            ui.manager.set_window_resolution((event.x, event.y))
            settings.screen_size = Vector2(event.x, event.y)
            ui.draw()
            settings.screen_update = True
        elif event.type == pygame.WINDOWRESTORED:
            settings.screen_update = True
        elif event.type == pygame.MOUSEWHEEL and not settings.edit_neighbours:
            try:
                zoom(settings.cell_size * 2 ** event.y, Vector2(pygame.mouse.get_pos()))
                ui.cell_size_slider.set_current_value(settings.cell_size)
                ui.cell_size_value.set_text(str(settings.cell_size))
            except ValueError:
                pass
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            objectID = event.ui_element.object_ids[-1]
            if objectID == "#Minimise_Button":
                ui.panel_minimised = not ui.panel_minimised
            elif objectID == "#BGColorDemo":
                ui.create_colour_picker("bg_color", "Background Color")
            elif objectID == "#CellColorDemo":
                ui.create_colour_picker("cell_color", "Cell Color")
            elif objectID == "#ResetButton":
                cells = set()
                frontier = set()
                settings.screen_update = True
            elif objectID == "#PauseButton":
                settings.paused = not settings.paused
            elif objectID == "#NeighbourButton":
                settings.edit_neighbours = not settings.edit_neighbours
                settings.screen_update = True
            elif objectID == "#SaveButton":
                settings.save_settings_to_file()
            elif objectID == "#LoadButton":
                settings.load_settings_from_file()
                ui.draw()
                settings.screen_update = True
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            objectID = event.ui_element.object_ids[-1]
            if objectID == "#SpeedSlider":
                settings.speed = event.value
                ui.speed_value.set_text(str(event.value))
            elif objectID == "#CellSizeSlider":
                zoom(event.value, settings.screen_size_in_cells * settings.cell_size // 2)
                ui.cell_size_value.set_text(str(event.value))
                frontier = cells
                cells = set()
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            objectID = event.ui_element.object_ids[-1]
            if objectID == "#CellColorValue":
                if (len(event.text) != 7 or event.text[0] != "#"):
                    ui.cell_color_value.set_text(ui.color_to_hex(settings.cell_color))
                else:
                    settings.cell_color = Color(event.text)
                    settings.screen_update = True
                    ui.draw()
            elif objectID == "#BGColorValue":
                if (len(event.text) != 7 or event.text[0] != "#"):
                    ui.bg_color_value.set_text(ui.color_to_hex(settings.bg_color))
                else:
                    settings.bg_color = Color(event.text)
                    settings.screen_update = True
                    ui.draw()
            elif objectID == "#SpeedValue":
                value = int(event.text)
                if value > settings.speed_max:
                    value = settings.speed_max
                elif value < 1:
                    value = 1
                settings.speed = value
                ui.speed_slider.set_current_value(value)
                ui.speed_value.set_text(str(value))
            elif objectID == "#CellSizeValue":
                value = int(event.text)
                if value > settings.cell_size_max:
                    value = settings.cell_size_max
                elif value < 1:
                    value = 1
                settings.cell_size = value
                ui.cell_size_slider.set_current_value(value)
                ui.cell_size_value.set_text(str(value))
            elif objectID == "#CondLiveValue":
                try:
                    eval(event.text, {"x": 0})
                    if "x" not in event.text:
                        raise SyntaxError()
                    settings.live_condition = event.text
                    frontier = cells
                except (NameError, SyntaxError):
                    ui.cond_live_value.set_text(settings.live_condition)
            elif objectID == "#CondBirthValue":
                try:
                    eval(event.text, {"x": 0})
                    if "x" not in event.text:
                        raise SyntaxError()
                    settings.birth_condition = event.text
                    frontier = cells
                except (NameError, SyntaxError):
                    ui.cond_birth_value.set_text(settings.birth_condition)
        elif event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            settings.__setattr__(ui.color_picker_color_attr, event.colour)
            settings.screen_update = True
            ui.draw()

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


    if settings.edit_neighbours and not ui.manager.get_hovering_any_element():
        cursor_pos = mouse_pos / settings.cell_size - settings.screen_size_in_cells / 2
        cursor_pos //= 1
        if mouse_states[0]:
            settings.neighbour_area.add((*cursor_pos,))
            settings.update_neighbour_area()
            frontier = cells
        elif mouse_states[2] and (*cursor_pos,) in settings.neighbour_area:
            settings.neighbour_area.remove((*cursor_pos,))
            settings.update_neighbour_area()
            frontier = cells
    elif not settings.edit_neighbours:
        cursor_pos = settings.camera_position + mouse_pos // settings.cell_size
        cursor_pos = Vector2(cursor_pos.x, cursor_pos.y)
        if mouse_states[0] and not ui.manager.get_hovering_any_element():
            cells.add(tuple(cursor_pos))
            add_cells_to_frontier(cursor_pos.x, cursor_pos.y)
        elif mouse_states[2] and not ui.manager.get_hovering_any_element():
            cell = tuple(cursor_pos)
            if cell in cells:
                cells.remove(cell)
                add_cells_to_frontier(*cell)
        elif settings.speed > 0 and not settings.paused:
            update_cells()

    draw_bound_x = (settings.camera_position.x - 1, settings.camera_far_pos.x)
    draw_bound_y = (settings.camera_position.y - 1, settings.camera_far_pos.y)

    if settings.edit_neighbours:
        settings.cell_size = 64
        ui.cell_size_value.set_text("64")
        ui.cell_size_slider.set_current_value(64)
        screen.fill(settings.bg_color)
        centre = settings.screen_size_in_cells * settings.cell_size // 2
        for x, y in settings.neighbour_area:
            pygame.draw.rect(screen, Color("#57D4B0"),
                             (centre.x+x*settings.cell_size,centre.y+y*settings.cell_size,
                              settings.cell_size, settings.cell_size))
        pygame.draw.rect(screen, settings.cell_color, (centre.x, centre.y,
                                                       settings.cell_size, settings.cell_size))
        pygame.display.update((0, 0, ui.settings_panel.get_abs_rect().x, settings.screen_size.y))
    elif settings.screen_update:
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
        pygame.display.update((0, 0, ui.settings_panel.get_abs_rect().x, settings.screen_size.y))
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
        pygame.display.update((0, 0, *(settings.screen_size_in_cells * settings.cell_size)))

    ui.manager.draw_ui(screen)
    ui.manager.update(time_delta)
    pygame.display.update(ui.settings_panel.get_abs_rect())

    if settings.speed == 0 or any(mouse_states) or settings.paused:
        time_delta = clock.tick(60)
    else:
        time_delta = clock.tick(settings.speed)
    ui.fps_label.set_text(str(int(1000/time_delta)))
