from tkinter import RAISED, Frame

import common.constants as cons
from common.text import *
from common.utils import get_color
from reporter_ui.components.component_base import RGComponentBase
from reporter_ui.components.widgets.button import RGButton
from reporter_ui.tool_manager import RGToolManager


class ButtonsFrame(RGComponentBase):

    def __init__(self, **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.size = (int(self.window.size[0] * self.off_set), 65)

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
        RGToolManager.execute(self.config)

    def __cancel_report(self):
        self.window.close_app()
