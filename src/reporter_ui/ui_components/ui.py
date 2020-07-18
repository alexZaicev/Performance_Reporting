from tkinter import Tk, messagebox

from common.models.errors import RGUIError
from common.text import *
from reporter_ui.ui_components.component_base import RGComponentBase


class RGUI(Tk, RGComponentBase):

    def __init__(self, config=None, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        if config is None:
            raise RGUIError('Cannot render reporting tool with invalid configuration')
        self.protocol('WM_DELETE_WINDOW', self.close_app)

    def close_app(self):
        if messagebox.askokcancel(CLOSE, ARE_YOU_SURE_YOU_WANT_TO_CLOSE_REPORTING_TOOL):
            self.destroy()
            exit()

    def build(self):
        self.mainloop()
