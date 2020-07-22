from tkinter import Tk, messagebox

from common.constants import APPLICATION_NAME, VERSION, DIM_WHITE
from common.models.errors import RGUIError
from common.text import *
from common.utils import get_color
from reporter_ui.config_manager import RGConfigManager
from reporter_ui.components.frames.buttons_frame import ButtonsFrame
from reporter_ui.components.component_base import RGApplicationBase
from reporter_ui.components.frames.exclusion_frame import ExclusionFrame
from reporter_ui.components.frames.parameters_frame import ParametersFrame


class RGApplication(RGApplicationBase):

    def __init__(self, config=None):
        RGApplicationBase.__init__(self, config=config)
        self.__window = Tk()
        self.__init_app()

    def app(self):
        return self.__window

    def build(self):
        super().build()
        try:
            ParametersFrame(window=self, config=self.config).build()
            ExclusionFrame(window=self, config=self.config).build()
            ButtonsFrame(window=self, config=self.config).build()
        except RGUIError as ex:
            # TODO show error dialog to the user
            pass
        self.__window.mainloop()

    def pre_destroy(self):
        RGConfigManager.save_config(self.config)

    def __init_app(self):
        self.__window.protocol('WM_DELETE_WINDOW', self.close_app)
        self.__window.resizable(0, 0)
        self.__window.minsize(width=self.size[0], height=self.size[1])
        self.__window.geometry('{}x{}+0+0'.format(self.size[0], self.size[1]))
        self.__window.title(APPLICATION_NAME.format(VERSION))
        self.__window.configure(background=str(get_color(DIM_WHITE)))

    def close_app(self):
        if messagebox.askokcancel(CLOSE, ARE_YOU_SURE_YOU_WANT_TO_CLOSE_REPORTING_TOOL):
            self.pre_destroy()
            self.__window.destroy()
            exit()
