import logging
from tkinter import Frame, RAISED, StringVar

import common.constants as cons
from common.text import *
from common.utils import get_color, get_cfy, get_cfy_prefix, try_parse, get_fiscal_month_id
from reporter_ui.components.component_base import RGComponentBase
from reporter_ui.components.widgets.dropdown import RGDropdown
from reporter_ui.components.widgets.label import RGLabel
from reporter_ui.components.widgets.path_selector import RGPathSelector


class ParametersFrame(RGComponentBase):

    def __init__(self, **kwargs):
        RGComponentBase.__init__(self, **kwargs)
        self.size = (int(self.window.size[0] * self.off_set), 260)
        self.fy = StringVar()
        self.fy.trace('w', self.__year_changed)
        self.fm = StringVar()
        self.fm.trace('w', self.__month_changed)
        self.temp_dir = StringVar()
        self.temp_dir.set(self.config.template_dir)
        self.out_dir = StringVar()
        self.out_dir.set(self.config.out_dir)
        self.orca_path = StringVar()
        self.orca_path.set(self.config.orca_path)

    def build(self):
        super().build()
        frame = Frame(master=self.window.app(), width=self.size[0], height=self.size[1],
                      relief=RAISED, bg=str(get_color(cons.WHITE)))
        f_xy = (int((self.window.size[0] - self.size[0]) / 2), int(self.window.size[0] * 0.015))
        frame.place(x=f_xy[0], y=f_xy[1])

        child_xy = [5, 5]

        lbl_name = RGLabel(window=frame, config=self.config, text=PARAMETERS, font_size=14, font_weight='bold',
                           x=child_xy[0], y=child_xy[1])
        lbl_name.build()
        child_xy[1] += lbl_name.size()[1] + 5
        self.__build_left_column(frame, child_xy)

        child_xy = [child_xy[0] + int(self.size[0] / 2), lbl_name.size()[1] + 10]
        self.__build_right_column(frame, child_xy)

    def __build_left_column(self, frame, child_xy):
        lbl_fy = RGLabel(window=frame, config=self.config, text='{}:'.format(FISCAL_YEAR), x=child_xy[0], y=child_xy[1],
                         font_size=10, font_weight='bold')
        lbl_fy.build()

        child_xy[1] += lbl_fy.size()[1]
        fy_om = RGDropdown(window=frame, config=self.config, text_var=self.fy, options=self.__fy_options(self.config),
                           width=self.size[0] / 2, x=child_xy[0], y=child_xy[1])
        fy_om.build()

        child_xy[1] += fy_om.size()[1]

        lbl_fm = RGLabel(window=frame, config=self.config, text='{}:'.format(MONTH), x=child_xy[0], y=child_xy[1],
                         font_size=10, font_weight='bold')
        lbl_fm.build()

        child_xy[1] += lbl_fm.size()[1]
        fm_om = RGDropdown(window=frame, config=self.config, text_var=self.fm, options=self.__fm_options(),
                           width=self.size[0] / 2, x=child_xy[0], y=child_xy[1])
        fm_om.build()

    def __build_right_column(self, frame, child_xy):
        w_temp = RGPathSelector(window=frame, config=self.config, text=TEMPLATE_DIRECTORY, text_var=self.temp_dir,
                                x=child_xy[0], y=child_xy[1], width=self.size[0] / 2,
                                callback=self.__browse_template_dir)
        w_temp.build()
        child_xy[1] += w_temp.size(winfo=False)[1] + self.size[0] * 0.005
        w_out = RGPathSelector(window=frame, config=self.config, text=OUTPUT_DIRECTORY, text_var=self.out_dir,
                               x=child_xy[0], y=child_xy[1], width=self.size[0] / 2, callback=self.__browse_out_dir)
        w_out.build()
        child_xy[1] += w_out.size(winfo=False)[1] + self.size[0] * 0.005
        w_orca = RGPathSelector(window=frame, config=self.config, text=ORCA_PATH, text_var=self.orca_path,
                                x=child_xy[0], y=child_xy[1], width=self.size[0] / 2, callback=self.__browse_orca_dir)
        w_orca.build()

    def __browse_template_dir(self):
        d_path = RGPathSelector.browse(self.temp_dir, is_dir=True)
        if d_path is not None:
            self.temp_dir.set(d_path)
            self.config.template_dir = d_path
        else:
            logging.getLogger(__name__).warning('Failed to retrieve new template directory')

    def __browse_out_dir(self):
        d_path = RGPathSelector.browse(self.out_dir, is_dir=True)
        if d_path is not None:
            self.out_dir.set(d_path)
            self.config.out_dir = d_path
        else:
            logging.getLogger(__name__).warning('Failed to retrieve new output directory')

    def __browse_orca_dir(self):
        d_path = RGPathSelector.browse(self.orca_path)
        if d_path is not None:
            self.orca_path.set(d_path)
            self.config.orca_path = d_path
        else:
            logging.getLogger(__name__).warning('Failed to retrieve new Orca tool directory')

    def __year_changed(self, *args):
        f_year = self.fy.get()
        if f_year == SELECT_AN_OPTION:
            self.config.f_year = None
        else:
            self.config.f_year = try_parse(f_year[:4], is_int=True)

    def __month_changed(self, *args):
        f_month = self.fm.get()
        if f_month == SELECT_AN_OPTION:
            self.config.f_month = None
        else:
            f_month = f_month.upper()[:3]
            self.config.f_month = get_fiscal_month_id(f_month)

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
