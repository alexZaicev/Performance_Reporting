from tkinter import Toplevel

from common.constants import DIM_WHITE
from common.models.errors import RGError
from common.utils import get_color
from reporter_ui.components.component_base import RGComponentBase
from reporter_ui.components.widgets.label import RGLabel
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGDialogBase(RGComponentBase):

    def __init__(self, title=None, widgets=None, width=None, height=0, color=DIM_WHITE, resizable=False, **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.dialog = Toplevel(master=self.window.app())
        self.title = title
        self.widgets = widgets
        if width is None:
            width = 0
        if height is None:
            height = 0
        self.dimensions = (width, height)
        self.color = color
        self.resizable = resizable

    def build(self):
        super().build()
        self.dialog.title(self.title)
        self.dialog.geometry('{}x{}+0+0'.format(self.dimensions[0], self.dimensions[1]))
        self.dialog.configure(bg=str(get_color(self.color)))
        if not self.resizable:
            self.dialog.resizable(0, 0)
        if self.widgets is not None:
            for widget in self.widgets:
                if not isinstance(widget, RGWidgetBase):
                    raise RGError('Widget does not extends RGWidgetBase')
                if isinstance(widget, RGLabel):
                    widget.color = self.color
                widget.window = self.dialog
                widget.build()

    def dismiss(self):
        if self.dialog is not None:
            self.dialog.destroy()
