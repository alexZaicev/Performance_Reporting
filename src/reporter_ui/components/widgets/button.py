from tkinter import Button

from common.constants import WHITE, BLACK
from common.utils import get_color
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGButton(RGWidgetBase):

    def __init__(self, text=None, callback=None, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.text = text
        self.callback = callback

    def build(self):
        super().build()
        self.widget = Button(master=self.window, text=self.text, command=self.callback)
        self.widget.configure(font=self.font, width=self.dimensions[0], height=self.dimensions[1],
                              bg=str(get_color(self.color)))
        if self.custom_pack:
            self.pack()
        else:
            self.widget.place(x=self.xy[0], y=self.xy[1])
