from time import sleep
from tkinter import RAISED, Frame

import common.constants as cons
from common.models.errors import RGUIError
from common.text import *
from common.utils import get_color, str_blank
from reporter_ui.components.component_base import RGComponentBase
from reporter_ui.components.widgets.button import RGButton
from reporter_ui.components.widgets.confirm_dialog import RGConfirmDialog
from reporter_ui.components.widgets.loading_dialog import RGLoadingDialog
from reporter_ui.tool_manager import RGToolManager


class ButtonsFrame(RGComponentBase):

    def __init__(self, **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.size = (int(self.window.size[0] * self.off_set), 65)
        self.__conf_dialog = None

    def build(self):
        super().build()
        frame = Frame(master=self.window.app(), width=self.size[0], height=self.size[1],
                      relief=RAISED, bg=str(get_color(cons.WHITE)))
        f_xy = (int((self.window.size[0] - self.size[0]) / 2), 260 + 480 + int(self.window.size[0] * 0.015 * 3))
        frame.place(x=f_xy[0], y=f_xy[1])

        btn_gen = RGButton(window=frame, config=self.config, text=GENERATE.upper(), callback=self.__generate_report,
                           width=self.size[0] * 0.02, height=self.size[1] * 0.04, font_weight='bold', color=cons.BLUE,
                           x=self.size[0] * 0.81, y=self.size[1] * 0.11)
        btn_gen.build()

        btn_cancel = RGButton(window=frame, config=self.config, text=CANCEL.upper(), callback=self.__cancel_report,
                              width=self.size[0] * 0.02, height=self.size[1] * 0.04, font_weight='bold',
                              color=cons.RED,
                              x=self.size[0] * 0.62, y=self.size[1] * 0.11)
        btn_cancel.build()

    def __generate_report(self):
        # check config
        err_msg = None
        if self.config.f_year is None:
            err_msg = CURRENT_FISCAL_YEAR_IS_NOT_SELECTED
        elif self.config.f_month is None:
            err_msg = CURRENT_FISCAL_MONTH_IS_NOT_SELECTED
        elif str_blank(self.config.template_dir):
            err_msg = TEMPLATE_ROOT_DIRECTORY_PATH_IS_NOT_PROVIDED
        elif str_blank(self.config.out_dir):
            err_msg = REPORT_OUTPUT_DIRECTORY_IS_NOT_PROVIDED

        if err_msg is not None:
            self.window.show_error_dialog(err_msg)
        else:
            # confirm user action
            msg = PLEASE_VERIFY_SELECTED_PARAMETERS_BEFORE_CONTINUING
            exclusions = [x for x in self.config.measure_entries if x.selected]
            if len(exclusions) > 0:
                msg = '{}. {}'.format(msg, NUMBER_OF_EXCLUSIONS_SELECTED.format(len(exclusions),
                                                                                len(self.config.measure_entries)))
            self.__conf_dialog = RGConfirmDialog(window=self.window, config=self.config, message=msg, p_text=CONTINUE,
                                                 p_callback=self.__run_report, n_text=ABORT)
            self.__conf_dialog.build()

    def __cancel_report(self):
        self.window.close_app()

    def __run_report(self):
        self.__conf_dialog.dismiss()
        loader = RGLoadingDialog(message=PLEASE_WAIT_WHILE_REPORT_IS_GENERATED, window=self.window, config=self.config)
        loader.build()
        try:
            # RGToolManager.execute(self.config)
            pass
        except RGUIError as ex:
            self.window.show_error_dialog(str(ex))
            loader.dismiss()
