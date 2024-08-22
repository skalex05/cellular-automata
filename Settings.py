from pygame.color import Color
from pygame.math import Vector2

class Settings:
    def __init__(self, speed=60,
                 #live_condition=(lambda x: x > 2), birth_condition=(lambda x: x == 3),
                 live_condition=(lambda x: 2 <= x <= 3), birth_condition=(lambda x: x == 3),
                 neighbour_area=None,
                 bg_color=("#726f5f",),
                 cell_color=("#8EDB57",),
                 camera_position=None,
                 cell_size=8,

                 grid_size=Vector2(10000, 10000),
                 screen_size=Vector2(500, 500),
                 fullscreen=False):
        self.initialising = True

        if not neighbour_area:
            neighbour_area = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1)
            ]

        # User Settings
        self.speed = speed  # CONNECTED TO: frame_time
        self.live_condition = live_condition
        self.birth_condition = birth_condition
        self.bg_color = Color(*bg_color)
        self.cell_color = Color(*cell_color)
        self.cell_size = cell_size  # DEPENDENTS: screen_size_in_cells
        self.neighbour_area = neighbour_area
        self.symmetrical_area = True
        if camera_position:
            self.camera_position = camera_position # CONNECTED TO: camera_far_pos
        else:
            self.camera_position = grid_size // 2

        for nx, ny in neighbour_area:
            if (-nx,-ny) not in neighbour_area:
                self.symmetrical_area = False

        # Internal Settings
        self.frame_time = 1 / speed  # CONNECTED TO: speed
        self.grid_size = grid_size.copy()  # CONNECTED TO: camera_position DEPENDENT ON screen_size_in_cells
        self.screen_size = screen_size  # DEPENDENTS: screen_size_in_cells
        self.screen_size_in_cells = None  # DEPENDENCIES: cell_size, screen_size
        self.settings_panel = None
        self.initialising = False

        # \/ DEPENDENCIES: screen_size_in_cells CONNECTED TO: camera_position
        self.camera_far_pos = None

        self.screen_update = True
        self.fullscreen = fullscreen


    def __setattr__(self, name, value):
        if name in self.__dict__ and self.__dict__[name] == value:
            return

        if name == "initialising":
            self.__dict__[name] = value

        if self.initialising:
            self.__dict__[name] = value
            return

        if name == "speed":
            if value <= 0:
                raise ValueError("Speed must be > 0")
            self.__dict__[name] = value
            self.frame_time = 1 / value
        elif name == "frame_time":
            if value <= 0:
                raise ValueError("Frame Time cannot be 0")
            self.__dict__[name] = value
            self.speed = 1 / value

        elif name == "cell_size":
            if value < 1:
                raise ValueError("Cell Size must be a positive integer")
            if value > 128:
                raise ValueError("Cell Size may not exceed 128")
            value = int(value)
            self.__dict__[name] = value

            if self.settings_panel:
                size = Vector2(self.settings_panel.get_abs_rect().x, self.screen_size.y)
                self.screen_size_in_cells = size // value

        elif name == "screen_size":
            self.__dict__[name] = value
            if self.settings_panel:
                size = Vector2(self.settings_panel.get_abs_rect().x, value.y)
                self.screen_size_in_cells = size // self.cell_size

        elif name == "screen_size_in_cells":
            self.__dict__[name] = value
            self.camera_far_pos = self.camera_position + self.screen_size_in_cells

        elif name == "camera_far_pos":
            self.__dict__[name] = value
            if not value:
                return
            if value.x > self.grid_size.x > self.screen_size_in_cells.x:
                value.x = self.grid_size.x
            if self.grid_size.x < self.screen_size_in_cells.x:
                value.x = self.screen_size_in_cells.x
            if value.y > self.grid_size.y:
                value.y = self.grid_size.y
            if self.grid_size.y < self.screen_size_in_cells.y:
                value.y = self.screen_size_in_cells.y
            self.camera_position = value - self.screen_size_in_cells

        elif name == "camera_position":
            self.__dict__[name] = value
            if not value:
                return
            if value.x < 0:
                value.x = 0
            if value.y < 0:
                value.y = 0
            self.camera_far_pos = self.camera_position + self.screen_size_in_cells

        elif name == "neighbour_area":
            self.__dict__[name] = value
            sym = True
            for nx, ny in value:
                if (-nx, -ny) not in value:
                    sym = False
            self.symmetrical_area = sym
        elif name == "settings_panel":
            self.__dict__[name] = value
            temp = self.screen_size
            self.screen_size = Vector2(0, 0)
            self.screen_size = temp

        else:
            self.__dict__[name] = value

    def __repr__(self):
        return f"""User:
Speed: {self.speed}
BG Color: {self.bg_color}
Cell Color: {self.cell_color}
Cell Size: {self.cell_size}

Internal:
Frame time: {self.frame_time} s
Grid Size: {self.grid_size}
Screen Size: {self.screen_size} | {self.screen_size_in_cells} cells
Camera Positions Top Left: {self.camera_position}
Camera Position Bottom Right: {self.camera_far_pos}
"""

settings = Settings()