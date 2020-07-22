from tkinter import RAISED, Frame

import common.constants as cons
from common.text import *
from common.utils import get_color
from reporter_ui.components.component_base import RGComponentBase
from reporter_ui.components.widgets.label import RGLabel


class ExclusionFrame(RGComponentBase):

    def __init__(self, **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.size = (int(self.window.size[0] * self.off_set), 480)

    def build(self):
        super().build()
        frame = Frame(master=self.window.app(), width=self.size[0], height=self.size[1],
                      relief=RAISED, bg=str(get_color(cons.WHITE)))
        f_xy = (int((self.window.size[0] - self.size[0]) / 2), 260 + int(self.window.size[0] * 0.015 * 2))
        frame.place(x=f_xy[0], y=f_xy[1])

        child_xy = [5, 5]

        lbl_name = RGLabel(window=frame, config=self.config, text=CPM_MEASURES_TO_EXCLUDE, font_size=14,
                           font_weight='bold',
                           x=child_xy[0], y=child_xy[1])
        lbl_name.build()
        child_xy[1] += lbl_name.size()[1] + 5
