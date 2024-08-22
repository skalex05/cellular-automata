import pygame
from pygame import Vector2
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UITextEntryLine, UIHorizontalSlider, UILabel, UIImage, UITextBox, \
    UISelectionList
from pygame_gui.core import ObjectID, UIContainer
from pygame_gui.windows import UIConfirmationDialog


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
    def __init__(self, settings,
                 panel_minimised=False,
                 panel_width=300,
                 panel_min_width=20
                 ):
        self.settings = settings
        self.panel_minimised = panel_minimised
        self.panel_width = panel_width
        self.panel_min_width = panel_min_width


        self.manager = pygame_gui.UIManager(settings.screen_size, "theme.json", True)
        if panel_minimised:
            pos = (panel_width-panel_min_width, 0)
        else:
            pos = (0, 0)
        self.settings_panel = create_ui_element(self.manager, UIPanel, pos,
                                           (panel_width, settings.screen_size.y), TOP_RIGHT,
                                            object_id=ObjectID("#Settings", "@Panel"))

        self.minimise_button = create_ui_element(self.manager, UIButton, (0, 0),
                                                 (panel_min_width, panel_min_width), TOP_LEFT,
                                                 object_id=ObjectID("#Minimise_Button", "@Button"),
                                                 container=self.settings_panel, text=">",)
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



