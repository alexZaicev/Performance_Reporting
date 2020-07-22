import logging
from tkinter import Label, LEFT

from common.models.errors import RGError
from common.utils import get_color
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGLabel(RGWidgetBase):

    def __init__(self, text=None, text_var=None, border_width=None, relief=None, justify=LEFT, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.text = text
        self.text_var = text_var
        self.justify = justify
        self.border_width = border_width
        self.relief = relief

    def build(self):
        super().build()
        if self.text is not None:
            self.widget = Label(master=self.window, text=self.text)
        elif self.text_var is not None:
            self.widget = Label(master=self.window, textvariable=self.text_var)
        else:
            logging.getLogger(__name__).warning('RGLabel does not have any text values provided')
            self.widget = Label(master=self.window)

        if self.widget is None:
            raise RGError('Label text values cannot be None')
        self.widget.configure(font=self.font, width=self.dimensions[0], height=self.dimensions[1],
                              bg=str(get_color(self.color)), justify=self.justify, borderwidth=self.border_width,
                              relief=self.relief)
        if self.custom_pack:
            self.pack()
        else:
            self.widget.place(x=self.xy[0], y=self.xy[1])
