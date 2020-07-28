from abc import ABC
from tkinter import CENTER

from common.constants import WHITE
from common.models.errors import RGError
from reporter_ui.components.component_base import RGComponentBase


class RGWidgetBase(RGComponentBase, ABC):

    def __init__(self, color=WHITE, x=0.0, y=0.0, width=None, height=None,
                 font_family='Arial', font_size=11, font_weight='normal', custom_pack=False, rel_x=0.0, rel_y=0.0,
                 anchor=CENTER, **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.widget = None
        self.color = color
        self.xy = (int(x), int(y))
        self.rel_xy = (rel_x, rel_y)
        self.anchor = anchor
        if width is not None:
            width = int(width)
        if height is not None:
            height = int(height)
        self.dimensions = (width, height)
        self.font = (font_family, font_size, font_weight)
        self.custom_pack = custom_pack

    def size(self, winfo=True):
        if winfo:
            self.check_widget()
            self.window.master.update()
            return self.widget.winfo_width(), self.widget.winfo_height()
        else:
            return self.dimensions

    def check_widget(self):
        if self.widget is None:
            raise RGError('Component widget is undefined')

    def pack(self):
        if self.rel_xy[0] is not None and self.rel_xy[1] is not None:
            self.widget.place(relx=self.rel_xy[0], rely=self.rel_xy[1], anchor=self.anchor)
        else:
            self.widget.place(x=self.xy[0], y=self.xy[1], anchor=self.anchor)
