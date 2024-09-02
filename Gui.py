import pygame
from pygame import Vector2
from pygame.color import Color
import pygame_gui
from pygame_gui.elements import (UIPanel, UIButton, UITextEntryLine, UIHorizontalSlider, UILabel, UIScrollingContainer)
from pygame_gui.windows.ui_colour_picker_dialog import UIColourPickerDialog
from pygame_gui.core import ObjectID
from string import hexdigits


def create_ui_element(manager, element, position, size, anchor, **kwargs):
    # Default anchors for top-left
    anchors = {"left": "left",
               "right": "left",
               "top": "top",
               "bottom": "top"}
    # Changes to anchors are applied
    for k in anchor[0]:
        anchors[k] = anchor[0][k]
    # The Rect object that represents the positon and size of the element is defined
    rect = pygame.Rect(0, 0, *size)
    setattr(rect, anchor[1], position)  # Adjust the rect's position to match the anchored corner
    # Create the element object with all required properties as well as parsing any additional properties (text/ visible/ objectId etc. )
    element = element(relative_rect=rect, manager=manager, anchors=anchors, **kwargs)

    return element


TOP_RIGHT = [{"right": "right", "left": "right"}, "topright"]
TOP_LEFT = [{"right": "left", "left": "left"}, "topleft"]
BOTTOM_RIGHT = [{"right": "right", "left": "right", "top": "bottom", "bottom": "bottom"}, "bottomright"]
BOTTOM_LEFT = [{"right": "left", "left": "left", "top": "bottom", "bottom": "bottom"}, "bottomleft"]


class UI:
    def __setattr__(self, name, value):
        if (name in self.__dict__ and self.__dict__[name] == value):
            return

        if name not in self.__dict__:
            self.__dict__[name] = value
            return

        if name == "panel_minimised":
            self.__dict__[name] = value
            if self.panel_minimised:
                pos = (-self.panel_min_width, 0)
            else:
                pos = (-self.panel_width, 0)

            self.settings_panel.set_relative_position(pos)
            size = Vector2(self.settings_panel.get_abs_rect().x, self.settings.screen_size.y)
            self.settings.screen_size_in_cells = size // self.settings.cell_size
            self.settings.screen_update = True
        else:
            self.__dict__[name] = value

    def __init__(self, settings,
                 panel_minimised=False,
                 panel_width=400,
                 panel_min_width=20,
                 scroll_area_height=750,
                 padding=20,
                 field_label_width=80,
                 field_label_height=30,
                 slider_length=150,
                 slider_height=20,
                 color_picker_height=400
                 ):

        self.settings = settings
        self.settings.ui = self
        self.panel_minimised = panel_minimised
        self.panel_width = panel_width
        self.panel_min_width = panel_min_width
        self.scroll_area_height = scroll_area_height
        self.padding = padding
        self.field_label_width = field_label_width
        self.field_label_height = field_label_height
        self.slider_length = slider_length
        self.slider_height = slider_height
        self.color_picker_height = color_picker_height

        self.manager = None
        self.speed_label = None
        self.settings_list = None
        self.title = None
        self.minimise_button = None
        self.settings_panel = None
        self.cell_size = None
        self.cell_color = None
        self.bg_color = None
        self.edit_neighbour_button = None
        self.cell_size_value = None
        self.cell_size_slider = None
        self.cell_size_label = None
        self.cell_color_demo = None
        self.cell_color_value = None
        self.cell_color_label = None
        self.bg_color_demo = None
        self.bg_color_value = None
        self.bg_color_label = None
        self.cond_birth_value = None
        self.cond_birth_label = None
        self.cond_live_value = None
        self.cond_live_label = None
        self.speed_value = None
        self.speed_slider = None
        self.color_picker_window = None
        self.color_picker_color_attr = None

    def color_to_hex(self, color):
        out = "#"
        for i in [color.r, color.g, color.b]:
            out += hexdigits[i // 16]
            i %= 16
            out += hexdigits[i]
        return out.upper()

    def create_colour_picker(self, color_attr, title):
        if self.color_picker_window:
            self.color_picker_window.kill()
        size = Vector2(self.panel_width - self.padding - self.panel_minimised, self.color_picker_height)
        pos = self.settings.screen_size - size
        self.color_picker_window = UIColourPickerDialog(
            pygame.Rect(pos.x - self.padding - self.panel_minimised, pos.y, size.x, size.y),
            self.manager, initial_colour=Color(self.settings.__getattribute__(color_attr)),
            window_title=title)
        self.color_picker_window.draggable = False
        self.color_picker_window.resizable = False
        self.color_picker_color_attr = color_attr

    def draw(self):
        self.manager = pygame_gui.UIManager(self.settings.screen_size, "theme.json", True)

        bg_color = Color(self.settings.bg_color)
        self.manager.get_theme().ui_element_colours["#BGColorDemo"] = {"normal_bg": bg_color,
                                                                       "hovered_bg": bg_color,
                                                                       "disabled_bg": bg_color,
                                                                       "selected_bg": bg_color}
        cell_color = Color(self.settings.cell_color)
        self.manager.get_theme().ui_element_colours["#CellColorDemo"] = {"normal_bg": cell_color,
                                                                         "hovered_bg": cell_color,
                                                                         "disabled_bg": cell_color,
                                                                         "selected_bg": cell_color}
        if self.panel_minimised:
            pos = (self.panel_width - self.panel_min_width, 0)
        else:
            pos = (0, 0)
        self.settings_panel = create_ui_element(self.manager, UIPanel, pos,
                                                (self.panel_width, self.settings.screen_size.y), TOP_RIGHT,
                                                object_id=ObjectID("#Settings", "@Panel"))

        self.minimise_button = create_ui_element(self.manager, UIButton, (0, 0),
                                                 (self.panel_min_width, self.panel_min_width), TOP_LEFT,
                                                 object_id=ObjectID("#Minimise_Button", "@Button"),
                                                 container=self.settings_panel, text=">", )

        self.title = create_ui_element(self.manager, UILabel, (self.panel_min_width + self.padding, 0),
                                       (self.panel_width - self.panel_min_width - self.padding * 2,
                                        self.panel_min_width),
                                       TOP_LEFT, container=self.settings_panel, text="Settings")

        self.settings_list = create_ui_element(self.manager, UIScrollingContainer,
                                               (self.panel_min_width, self.padding),
                                               (self.panel_width - self.panel_min_width - 5,
                                                self.settings.screen_size.y - self.padding),
                                               TOP_LEFT, container=self.settings_panel)
        self.settings_list.allow_scroll_x = False
        self.settings_list.set_scrollable_area_dimensions(
            (self.panel_width - self.panel_min_width - self.padding * 2, self.scroll_area_height))

        self.speed_label = create_ui_element(self.manager, UILabel,
                                             (0, self.padding * 3),
                                             (self.field_label_width, self.field_label_height), TOP_LEFT,
                                             container=self.settings_list, text=f"Speed")

        self.speed_slider = create_ui_element(self.manager, UIHorizontalSlider,
                                              (self.padding + self.field_label_width,
                                               self.padding * 3 + (self.field_label_height - self.slider_height) / 2),
                                              (self.slider_length, self.slider_height), TOP_LEFT,
                                              container=self.settings_list, start_value=self.settings.speed,
                                              value_range=(0, self.settings.speed_max),
                                              object_id=ObjectID("#SpeedSlider", "@Slider"))

        self.speed_value = create_ui_element(self.manager, UITextEntryLine,
                                             (self.padding * 2 + self.field_label_width + self.slider_length,
                                              self.padding * 3),
                                             (self.field_label_height + 10, self.field_label_height), TOP_LEFT,
                                             container=self.settings_list,
                                             object_id=ObjectID("#SpeedValue", "@IntValue"))
        self.speed_value.set_text(str(self.settings.speed))
        self.speed_value.set_text_length_limit(3)
        self.speed_value.set_allowed_characters("numbers")

        self.fps_label = create_ui_element(self.manager, UILabel,
               (self.padding * 2 + self.field_label_width + self.slider_length + self.field_label_height + 10,
                       self.padding * 3),
                  (self.field_label_height + 10, self.field_label_height), TOP_LEFT,
                       container=self.settings_list, text=f"0")

        self.cond_live_label = create_ui_element(self.manager, UILabel,
                                                 (0, self.padding * 5),
                                                 (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                 container=self.settings_list, text=f"Live If")

        self.cond_live_value = create_ui_element(self.manager, UITextEntryLine,
                                                 (self.padding + self.field_label_width, self.padding * 5),
                                                 (int(self.field_label_width * 1.5), self.field_label_height), TOP_LEFT,
                                                 container=self.settings_list,
                                                 object_id=ObjectID("#CondLiveValue", "@CondValue"))
        self.cond_live_value.set_text(self.settings.live_condition)
        self.cond_live_value.set_text_length_limit(15)
        self.cond_live_value.set_allowed_characters(
            [" ", "<", ">", "=", "x", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

        self.cond_birth_label = create_ui_element(self.manager, UILabel,
                                                  (0, self.padding * 7),
                                                  (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                  container=self.settings_list, text=f"Birth If")

        self.cond_birth_value = create_ui_element(self.manager, UITextEntryLine,
                                                  (self.padding + self.field_label_width, self.padding * 7),
                                                  (int(self.field_label_width * 1.5), self.field_label_height),
                                                  TOP_LEFT,
                                                  container=self.settings_list,
                                                  object_id=ObjectID("#CondBirthValue", "@CondValue"))
        self.cond_birth_value.set_text(self.settings.birth_condition)
        self.cond_birth_value.set_text_length_limit(15)

        self.bg_color_label = create_ui_element(self.manager, UILabel,
                                                (0, self.padding * 9),
                                                (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                container=self.settings_list, text=f"BG Color")

        self.bg_color_value = create_ui_element(self.manager, UITextEntryLine,
                                                (self.padding + self.field_label_width, self.padding * 9),
                                                (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                container=self.settings_list,
                                                object_id=ObjectID("#BGColorValue", "@ColorValue"))
        self.bg_color_value.set_text(self.color_to_hex(self.settings.bg_color))
        self.bg_color_value.set_text_length_limit(7)
        self.bg_color_value.set_allowed_characters([c for c in "#" + hexdigits])

        self.bg_color_demo = create_ui_element(self.manager, UIButton,
                                               (self.padding * 2 + self.field_label_width * 2, self.padding * 9),
                                               (self.field_label_height, self.field_label_height), TOP_LEFT,
                                               container=self.settings_list, text="",
                                               object_id=ObjectID("#BGColorDemo", "@ColorDemo"))

        self.cell_color_label = create_ui_element(self.manager, UILabel,
                                                  (0, self.padding * 11),
                                                  (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                  container=self.settings_list, text=f"Cell Color")

        self.cell_color_value = create_ui_element(self.manager, UITextEntryLine,
                                                  (self.padding + self.field_label_width, self.padding * 11),
                                                  (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                  container=self.settings_list,
                                                  object_id=ObjectID("#CellColorValue", "@ColorValue"))
        self.cell_color_value.set_text(self.color_to_hex(self.settings.cell_color))
        self.cell_color_value.set_text_length_limit(7)
        self.cell_color_value.set_allowed_characters([c for c in "#" + hexdigits])

        self.cell_color_demo = create_ui_element(self.manager, UIButton,
                                                 (self.padding * 2 + self.field_label_width * 2, self.padding * 11),
                                                 (self.field_label_height, self.field_label_height), TOP_LEFT,
                                                 container=self.settings_list, text="",
                                                 object_id=ObjectID("#CellColorDemo", "@ColorDemo"))

        self.cell_size_label = create_ui_element(self.manager, UILabel,
                                                 (0, self.padding * 13),
                                                 (self.field_label_width, self.field_label_height), TOP_LEFT,
                                                 container=self.settings_list, text=f"Cell Size")

        self.cell_size_slider = create_ui_element(self.manager, UIHorizontalSlider,
                                                  (self.padding + self.field_label_width,
                                                   self.padding * 13 + (
                                                           self.field_label_height - self.slider_height) / 2),
                                                  (self.slider_length, self.slider_height), TOP_LEFT,
                                                  container=self.settings_list, start_value=self.settings.cell_size,
                                                  value_range=(1, self.settings.cell_size_max),
                                                  object_id=ObjectID("#CellSizeSlider", "@Slider"))

        self.cell_size_value = create_ui_element(self.manager, UITextEntryLine,
                                                 (self.padding * 2 + self.field_label_width + self.slider_length,
                                                  self.padding * 13),
                                                 (self.field_label_height + 10, self.field_label_height), TOP_LEFT,
                                                 container=self.settings_list,
                                                 object_id=ObjectID("#CellSizeValue", "@IntValue"))
        self.cell_size_value.set_text(str(self.settings.cell_size))
        self.cell_size_value.set_text_length_limit(3)
        self.cell_size_value.set_allowed_characters("numbers")

        self.edit_neighbour_button = create_ui_element(self.manager, UIButton,
                                                       (self.padding, self.padding * 16),
                                                       (self.panel_width - self.panel_min_width * 2 - self.padding * 2,
                                                        self.field_label_height), TOP_LEFT,
                                                       container=self.settings_list, text="Edit Neighbours",
                                                       object_id=ObjectID("#NeighbourButton", "@Button"))

        self.pause_button = create_ui_element(self.manager, UIButton,
                                                       (self.padding, self.padding * 18),
                                                       (self.panel_width - self.panel_min_width * 2 - self.padding * 2,
                                                        self.field_label_height), TOP_LEFT,
                                                       container=self.settings_list, text="Pause",
                                                       object_id=ObjectID("#PauseButton", "@Button"))

        self.reset_board_button = create_ui_element(self.manager, UIButton,
                                       (self.padding, self.padding * 20),
                                       (self.panel_width - self.panel_min_width * 2 - self.padding * 2,
                                        self.field_label_height), TOP_LEFT,
                                       container=self.settings_list, text="Reset Board",
                                       object_id=ObjectID("#ResetButton", "@Button"))

        self.save_button = create_ui_element(self.manager, UIButton,
                                                    (self.padding, self.padding * 22),
                                                    (self.panel_width - self.panel_min_width * 2 - self.padding * 2,
                                                     self.field_label_height), TOP_LEFT,
                                                    container=self.settings_list, text="Save",
                                                    object_id=ObjectID("#SaveButton", "@Button"))

        self.load_button = create_ui_element(self.manager, UIButton,
                                                    (self.padding, self.padding * 24),
                                                    (self.panel_width - self.panel_min_width * 2 - self.padding * 2,
                                                     self.field_label_height), TOP_LEFT,
                                                    container=self.settings_list, text="Load",
                                                    object_id=ObjectID("#LoadButton", "@Button"))

        size = Vector2(self.settings_panel.get_abs_rect().x, self.settings.screen_size.y)
        self.settings.screen_size_in_cells = size // self.settings.cell_size
