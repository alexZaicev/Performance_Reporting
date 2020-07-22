from abc import ABC

from common.constants import WHITE
from common.models.errors import RGError
from reporter_ui.components.component_base import RGComponentBase


class RGWidgetBase(RGComponentBase, ABC):

    def __init__(self, color=WHITE, x=0.0, y=0.0, width=None, height=None,
                 font_family='Arial', font_size=11, font_weight='normal', **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.widget = None
        self.color = color
        self.xy = (int(x), int(y))
        if width is not None:
            width = int(width)
        if height is not None:
            height = int(height)
        self.dimensions = (width, height)
        self.font = (font_family, font_size, font_weight)

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
