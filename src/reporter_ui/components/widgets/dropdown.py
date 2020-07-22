from tkinter import OptionMenu

from common.utils import get_color
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGDropdown(RGWidgetBase):

    def __init__(self, text_var=None, options=None, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.options = options
        self.text_var = text_var
        self.text_var.set(options[0])

    def build(self):
        super().build()
        self.widget = OptionMenu(self.window, self.text_var, *self.options)
        self.widget.configure(font=self.font, width=int(self.dimensions[0] * 0.105),
                              height=int(self.dimensions[0] * 0.005),
                              bg=str(get_color(self.color)))
        if self.custom_pack:
            self.pack()
        else:
            self.widget.place(x=self.xy[0], y=self.xy[1])
