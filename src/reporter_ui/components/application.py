import logging
import os
from tkinter import Tk, messagebox

from common.constants import APPLICATION_NAME, VERSION, DIM_WHITE
from common.models.errors import RGUIError
from common.text import *
from common.utils import get_color
from reporter_ui.components.component_base import RGApplicationBase
from reporter_ui.components.frames.buttons_frame import RGButtonsFrame
from reporter_ui.components.frames.exclusion_frame import ExclusionFrame
from reporter_ui.components.frames.parameters_frame import ParametersFrame
from reporter_ui.components.widgets.confirm_dialog import RGConfirmDialog
from reporter_ui.config_manager import RGConfigManager


class RGApplication(RGApplicationBase):
    PARAM_FRAME = 'PF'
    EXCLUSION_FRAME = 'EF'
    BUTTON_FRAME = 'BF'

    def __init__(self, config=None):
        RGApplicationBase.__init__(self, config=config)
        self.__window = Tk()
        self.__init_app()
        self.__blocked = False
        self.__widgets = None

    def app(self):
        return self.__window

    def build(self):
        super().build()
        self.__widgets = {
            RGApplication.PARAM_FRAME: ParametersFrame(window=self, config=self.config),
            RGApplication.EXCLUSION_FRAME: ExclusionFrame(window=self, config=self.config),
            RGApplication.BUTTON_FRAME: RGButtonsFrame(window=self, config=self.config)
        }
        try:
            for widget in self.__widgets.values():
                widget.build()
        except RGUIError as ex:
            self.show_error_dialog(message=str(ex))
        self.__window.mainloop()

    def close_app(self):
        if not self.__blocked:
            if messagebox.askokcancel(CLOSE, ARE_YOU_SURE_YOU_WANT_TO_CLOSE_REPORTING_TOOL):
                self.pre_destroy()
                self.__window.destroy()
                exit()
        else:
            logging.getLogger(__name__).debug('Cannot close application as it is waiting for reporting tool to finish')

    def pre_destroy(self):
        RGConfigManager.save_config(self.config)

    def __init_app(self):
        self.__window.protocol('WM_DELETE_WINDOW', self.close_app)
        self.__window.resizable(0, 0)
        self.__window.minsize(width=self.size[0], height=self.size[1])
        self.__window.geometry('{}x{}+0+0'.format(self.size[0], self.size[1]))
        self.__window.title(APPLICATION_NAME.format(VERSION))
        self.__window.configure(background=str(get_color(DIM_WHITE)))

    @staticmethod
    def show_error_dialog(message=None, exit_on_ok=False):
        if messagebox.showerror(title=ERROR, message=message) and exit_on_ok:
            exit()

    def block_ui(self):
        if not self.__blocked:
            self.__blocked = True

    def release_ui(self):
        if self.__blocked:
            self.__blocked = False

    def is_blocked(self):
        return self.__blocked

    def show_generation_completed_dialog(self, report_name):
        dialog = RGConfirmDialog(window=self, config=self.config, title=APPLICATION_NAME,
                                 message=REPORTING_TOOL_FINISHED_GENERATING_THE_REPORT_WOULD_YOU_LIKE_TO_OPEN_THE_FILE,
                                 p_text=YES, p_callback=lambda: self.__open_report(report_name, dialog), n_text=NO,
                                 rel_nx=0.4,
                                 rel_px=0.6)
        dialog.build()

    def __open_report(self, report_name, dialog):
        dialog.dismiss()
        ff_path = os.path.join(self.config.out_dir, report_name)
        os.startfile(ff_path)
