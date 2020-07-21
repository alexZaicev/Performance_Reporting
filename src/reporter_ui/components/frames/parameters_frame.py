import logging
from os.path import sep
from tkinter import Frame, RAISED, StringVar, filedialog

import common.constants as cons
from common.models.errors import RGError
from common.text import *
from common.utils import get_color, get_cfy, get_cfy_prefix
from reporter_ui.components.component_base import RGComponentBase
from reporter_ui.components.widgets.button import RGButton
from reporter_ui.components.widgets.dropdown import RGDropdown
from reporter_ui.components.widgets.label import RGLabel


class ParametersFrame(RGComponentBase):

    def __init__(self, config=None, window=None):
        RGComponentBase.__init__(self, config=config, window=window)
        self.fy = StringVar()
        self.fm = StringVar()
        self.temp_dir = StringVar()
        self.temp_dir.set(self.config.template_dir)
        self.out_dir = StringVar()
        self.out_dir.set(self.config.out_dir)
        self.size = (int(self.window.size[0] * self.off_set), 175)

    def build(self):
        super().build()
        frame = Frame(master=self.window.app(), width=self.size[0], height=self.size[1],
                      relief=RAISED, bg=str(get_color(cons.WHITE)))
        f_xy = (int((self.window.size[0] - self.size[0]) / 2), int(self.window.size[0] * 0.015))
        frame.place(x=f_xy[0], y=f_xy[1])

        child_xy = [5, 25]
        self.__build_left_column(frame, child_xy)

        child_xy = [child_xy[0] + int(self.size[0] / 2), 25]
        self.__build_right_column(frame, child_xy)

    def __build_left_column(self, frame, child_xy):
        lbl_fy = RGLabel(window=frame, config=self.config, text='{}:'.format(FISCAL_YEAR), x=child_xy[0], y=child_xy[1])
        lbl_fy.build()

        child_xy[1] += lbl_fy.size()[1]
        fy_om = RGDropdown(window=frame, config=self.config, text_var=self.fy, options=self.__fy_options(self.config),
                           width=self.window.size[0] * 0.045, height=self.window.size[0] * 0.001,
                           x=child_xy[0], y=child_xy[1])
        fy_om.build()

        child_xy[1] += fy_om.size()[1]

        lbl_fm = RGLabel(window=frame, config=self.config, text='{}:'.format(MONTH), x=child_xy[0], y=child_xy[1])
        lbl_fm.build()

        child_xy[1] += lbl_fm.size()[1]
        fm_om = RGDropdown(window=frame, config=self.config, text_var=self.fm, options=self.__fm_options(),
                           width=self.window.size[0] * 0.045, height=self.window.size[0] * 0.001,
                           x=child_xy[0], y=child_xy[1])
        fm_om.build()

    def __build_right_column(self, frame, child_xy):
        lbl_td = RGLabel(window=frame, config=self.config, text='{}:'.format(TEMPLATE_DIRECTORY), x=child_xy[0],
                         y=child_xy[1])
        lbl_td.build()

        child_xy[1] += lbl_td.size()[1]
        td = RGLabel(window=frame, config=self.config, text_var=self.temp_dir, color=cons.DIM_WHITE, border_width=1,
                     relief='groove', x=child_xy[0], y=child_xy[1], width=self.window.size[0] * 0.045,
                     height=self.window.size[0] * 0.002)
        td.build()

        btn_tb = RGButton(window=frame, config=self.config, text=BROWSE, callback=self.__browse_template_dir,
                          height=self.window.size[0] * 0.001,
                          x=child_xy[0] + td.size()[0] + 2,
                          y=child_xy[1] + 3
                          )
        btn_tb.build()

        child_xy[1] += td.size()[1]
        lbl_od = RGLabel(window=frame, config=self.config, text='{}:'.format(OUTPUT_DIRECTORY), x=child_xy[0],
                         y=child_xy[1])
        lbl_od.build()

        child_xy[1] += lbl_od.size()[1]
        od = RGLabel(window=frame, config=self.config, text_var=self.out_dir, color=cons.DIM_WHITE, border_width=1,
                     relief='groove', x=child_xy[0], y=child_xy[1], width=self.window.size[0] * 0.045,
                     height=self.window.size[0] * 0.002)
        od.build()

        btn_ob = RGButton(window=frame, config=self.config, text=BROWSE, callback=self.__browse_out_dir,
                          height=self.window.size[0] * 0.001,
                          x=child_xy[0] + od.size()[0] + 2,
                          y=child_xy[1] + 3
                          )
        btn_ob.build()

    @staticmethod
    def __fm_options():
        return (
            SELECT_AN_OPTION,
            APRIL,
            MAY,
            JUNE,
            JULY,
            AUGUST,
            SEPTEMBER,
            OCTOBER,
            NOVEMBER,
            DECEMBER,
            JANUARY,
            FEBRUARY,
            MARCH
        )

    @staticmethod
    def __fy_options(config):
        fy_opts = [SELECT_AN_OPTION]
        c_year = get_cfy()
        for i in range(0, config.fy_band, 1):
            fy_opts.append(get_cfy_prefix(cfy=c_year))
            c_year -= 1
        return fy_opts

    def __browse_template_dir(self):
        d_path = self.__browse_directory(self.temp_dir)
        if d_path is not None:
            self.temp_dir.set(d_path)
            self.config.template_dir = d_path
        else:
            logging.error('Failed to retrieve new template directory')

    def __browse_out_dir(self):
        d_path = self.__browse_directory(self.out_dir)
        if d_path is not None:
            self.out_dir.set(d_path)
            self.config.out_dir = d_path
        else:
            logging.error('Failed to retrieve new output directory')

    @staticmethod
    def __browse_directory(var):
        if not isinstance(var, StringVar):
            raise RGError('StringVar expected actual [{}]'.format(type(var)))
        filename = filedialog.askdirectory()
        if filename is not None and len(filename) > 0:
            filename = str(filename).replace('/', sep)
            return filename
        return None
