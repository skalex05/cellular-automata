import os
import pickle
from pygame.color import Color
from pygame.math import Vector2
from tkinter import filedialog, Tk

class SaveData:
    def __init__(self, settings):
        self.live_condition = settings.live_condition
        self.birth_condition = settings.birth_condition
        self.neighbour_area = settings.neighbour_area
        self.bg_color = settings.bg_color
        self.cell_color = settings.cell_color
    def load_to_settings(self, settings):
        settings.live_condition = self.live_condition
        settings.birth_condition = self.birth_condition
        settings.neighbour_area = self.neighbour_area
        settings.bg_color = self.bg_color
        settings.cell_color = self.cell_color

class Settings:
    def update_neighbour_area(self):
        sym = True
        for nx, ny in self.neighbour_area:
            if (-nx, -ny) not in self.neighbour_area:
                sym = False
        self.symmetrical_area = sym
        for i in range(len(self.neighbour_area) + 1):
            self.live_truth_table[i] = eval(self.live_condition, {"x": i})
        for i in range(len(self.neighbour_area) + 1):
            self.birth_truth_table[i] = eval(self.birth_condition, {"x": i})

    def save_settings_to_file(self):
        root = Tk()
        root.withdraw()
        file = filedialog.asksaveasfilename(filetypes=[("Cellular Automata SaveFile", "*.cas")], initialdir=os.getcwd())
        root.destroy()
        if file == "":
            return
        if not file.endswith(".cas"):
            file += ".cas"
        pickle.dump(SaveData(self), open(file, "wb"))
    def load_settings_from_file(self):
        root = Tk()
        root.withdraw()
        file = filedialog.askopenfilename(filetypes=[("Cellular Automata SaveFile", "*.cas")], initialdir=os.getcwd())
        root.destroy()
        if file == "":
            return
        if not file.endswith(".cas"):
            file += ".cas"
        save_data = pickle.load(open(file, "rb"))
        save_data.load_to_settings(self)

    def __init__(self, speed=60,
                 speed_max=60,
                 #live_condition=(lambda x: x > 2), birth_condition=(lambda x: x == 3),
                 live_condition="2 <= x <= 3",
                 birth_condition="x == 3",
                 neighbour_area=None,
                 bg_color=("#726f5f",),
                 cell_color=("#8EDB57",),
                 camera_position=None,
                 cell_size=8,
                 cell_size_max=128,
                 grid_size=Vector2(10000, 10000),
                 screen_size=Vector2(500, 500),
                 fullscreen=False):
        self.initialising = True

        if not neighbour_area:
            neighbour_area = {
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1)
            }

        # User Settings
        self.speed = speed
        self.speed_max = speed_max
        self.bg_color = Color(*bg_color)
        self.cell_color = Color(*cell_color)
        self.cell_size = cell_size  # DEPENDENTS: screen_size_in_cells
        self.cell_size_max = cell_size_max
        self.neighbour_area = neighbour_area
        self.symmetrical_area = True
        self.camera_position = None
        # \/ DEPENDENCIES: screen_size_in_cells CONNECTED TO: camera_position
        self.camera_far_pos = None

        for nx, ny in neighbour_area:
            if (-nx,-ny) not in neighbour_area:
                self.symmetrical_area = False

        # Internal Settings
        self.grid_size = grid_size.copy()  # CONNECTED TO: camera_position DEPENDENT ON screen_size_in_cells
        self.screen_size = screen_size  # DEPENDENTS: screen_size_in_cells
        self.screen_size_in_cells = screen_size // self.cell_size # DEPENDENCIES: cell_size, screen_size
        self.initialising = False
        self.live_condition = live_condition
        self.birth_condition = birth_condition

        if camera_position:
            self.camera_position = camera_position  # CONNECTED TO: camera_far_pos
        else:
            self.camera_position = grid_size // 2

        self.ui = None
        self.screen_update = True
        self.fullscreen = fullscreen
        self.paused = False
        self.edit_neighbours = False

    def __setattr__(self, name, value):
        if name in self.__dict__ and self.__dict__[name] == value:
            return

        if name == "initialising":
            self.__dict__[name] = value

        if self.initialising:
            self.__dict__[name] = value
            return

        if name == "speed":
            self.__dict__[name] = value
        elif name == "cell_size":
            if value < 1:
                raise ValueError("Cell Size must be a positive integer")
            if value > self.cell_size_max:
                raise ValueError("Cell Size may not exceed 128")
            value = int(value)
            self.__dict__[name] = value
            size = Vector2(self.ui.settings_panel.get_abs_rect().x, self.screen_size.y)
            settings.screen_size_in_cells = size // value

        elif name == "settings_panel":
            self.__dict__[name] = value
            temp = self.screen_size
            self.screen_size = Vector2(0, 0)
            self.screen_size = temp

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

        elif name == "live_condition":
            self.__dict__[name] = value
            self.live_truth_table = {}
            for i in range(len(self.neighbour_area)+1):
                self.live_truth_table[i] = eval(self.live_condition, {"x": i})
        elif name == "birth_condition":
            self.__dict__[name] = value
            self.birth_truth_table = {}
            for i in range(len(self.neighbour_area)+1):
                self.birth_truth_table[i] = eval(self.birth_condition, {"x": i})
        else:
            self.__dict__[name] = value

    def __repr__(self):
        return f"""User:
Speed: {self.speed}
BG Color: {self.bg_color}
Cell Color: {self.cell_color}
Cell Size: {self.cell_size}

Internal:
Grid Size: {self.grid_size}
Screen Size: {self.screen_size} | {self.screen_size_in_cells} cells
Camera Positions Top Left: {self.camera_position}
Camera Position Bottom Right: {self.camera_far_pos}
"""

settings = Settings()