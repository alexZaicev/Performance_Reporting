import logging
from tkinter import Canvas, GROOVE, Frame, TOP, X, BOTTOM, LEFT, BOTH, Scrollbar, VERTICAL, RIGHT, Y, UNITS

from common.constants import GREY, WHITE, BLACK, DIM_WHITE
from common.models.errors import RGError
from common.utils import get_color
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGTableModel(object):

    def __init__(self, headers=None, data=None):
        object.__init__(self)
        if headers is None:
            raise RGError('Table cannot be drawn without table headers')

        if data is None:
            raise RGError('Table data is not provided')

        self.headers = headers
        self.data = data


class RGTableHeader(RGWidgetBase):

    def __init__(self, headers=None, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.headers = headers

    def build(self):
        super().build()
        self.widget = Canvas(master=self.window.widget)
        self.widget.configure(bg=str(get_color(self.color)), relief=GROOVE, width=self.dimensions[0],
                              height=self.dimensions[1])
        self.widget.pack(side=TOP, fill=X)

        for i in range(0, len(self.headers) + 1, 1):
            if i == 0:
                txt = '#'
            else:
                txt = self.headers[i - 1]
            self.window.create_cell(self.widget, i, txt, is_header=True)


class RGTableData(RGWidgetBase):

    def __init__(self, data=None, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.data = data
        self.entry_y_lims = list()
        self.canvas = None
        self.__y_off_set = 0

    def build(self):
        super().build()
        self.widget = Frame(master=self.window.widget)
        self.widget.configure(width=self.dimensions[0], height=self.dimensions[1], bg=str(get_color(self.color)))
        self.widget.pack(side=BOTTOM, fill=X)

        self.canvas = Canvas(master=self.widget)
        self.__canvas_binding()
        self.canvas.configure(width=self.dimensions[0] - (self.dimensions[0] * 0.02), height=self.dimensions[1],
                              bg=str(get_color(self.color)), relief=GROOVE)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

        # create scrollbar
        y_scroll = Scrollbar(master=self.widget, orient=VERTICAL, width=self.dimensions[0] * 0.02)
        y_scroll.configure(command=self.canvas.yview)
        y_scroll.pack(side=RIGHT, fill=Y)

        self.__populate_table()

        y_region = int(self.window.left_top[1] + self.dimensions[0] * 0.005)
        self.canvas.configure(yscrollcommand=y_scroll.set, scrollregion=(0, 0, 0, y_region))

    def __populate_table(self):
        self.window.left_top = [0, self.window.off_sets[1]]
        for row in range(0, len(self.data), 1):
            size = (0, 0)
            row_data = self.__convert_entry_to_row(self.data[row])
            for column in range(0, len(row_data) + 1, 1):
                if column == 0:
                    txt = row + 1
                else:
                    txt = row_data[column - 1]
                size = self.window.create_cell(self.canvas, column, txt)
            y_lim_1 = self.window.left_top[1]
            self.window.left_top = [0, self.window.left_top[1] + size[1]]
            y_lim_2 = self.window.left_top[1]

            if len(self.entry_y_lims) < len(self.data):
                self.entry_y_lims.append((y_lim_1, y_lim_2))

    def __canvas_binding(self):
        self.canvas.bind("<ButtonRelease-1>", self.__on_release)
        self.canvas.bind_all("<MouseWheel>", self.__on_mouse_wheel)

    def __on_release(self, event):
        x, y = event.x, (event.y + self.__y_off_set)
        if y < 0:
            y = 0

        for y_lim in self.entry_y_lims:
            if y_lim[0] < y < y_lim[1]:
                idx = self.entry_y_lims.index(y_lim)
                self.data[idx].selected = not self.data[idx].selected

                # redraw canvas
                self.__populate_table()
                break

    def __on_mouse_wheel(self, event):
        if isinstance(event.widget, Canvas):
            if event.num == 5 or event.delta == -120:
                event.widget.yview_scroll(3, UNITS)
            if event.num == 4 or event.delta == 120:
                event.widget.yview_scroll(-3, UNITS)
            self.__y_off_set = self.canvas.canvasy(0)

    @staticmethod
    def __convert_entry_to_row(entry):
        return entry.selected, entry.m_id, entry.m_ref_no, entry.m_title


class RGTable(RGWidgetBase):

    def __init__(self, model=None, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.model = model
        self.off_sets = (2, 2)
        self.left_top = list(self.off_sets)
        self.cell_widths = {'#': 0.035, 'M_CB': 0.1, 'M_ID_REF_NO': 0.1, 'M_TITLE': 0.635}
        self.cell_height = 0.035

    def build(self):
        super().build()

        self.widget = Frame(master=self.window)
        self.widget.configure(width=self.dimensions[0], height=self.dimensions[1], bg=str(get_color(self.color)))
        self.widget.place(x=self.xy[0], y=self.xy[1])

        width = int(self.dimensions[0] - self.off_sets[0] * 2)
        height = int(self.dimensions[1] - self.off_sets[1] * 2)

        t_header = RGTableHeader(window=self, config=self.config, headers=self.model.headers, width=width,
                                 height=int(width * self.cell_height))
        t_header.build()

        t_data = RGTableData(window=self, config=self.config, data=self.model.data, width=width,
                             height=int(height - width * self.cell_height))
        t_data.build()

    def create_cell(self, widget, column, txt='', is_header=False):
        size = self.__get_size(column)

        if is_header:
            bg, fg = get_color(GREY), get_color(WHITE)
            font = ('Arial', 12, 'bold')
        else:
            bg, fg = get_color(DIM_WHITE), get_color(BLACK)
            font = ('Arial', 10)

        widget.create_rectangle(self.left_top[0], self.left_top[1], self.left_top[0] + size[0],
                                self.left_top[1] + size[1], fill=str(bg))

        x, y = self.left_top[0] + int(size[0] * 0.5), self.left_top[1] + (size[1] * 0.5)
        # check if txt value is a boolean
        if isinstance(txt, bool):
            outer_rect = (int(size[0] * 0.2), int(size[0] * 0.2))
            x_o = int(x - outer_rect[0] * 0.5)
            y_o = int(y - outer_rect[1] * 0.5)
            widget.create_rectangle(x_o, y_o, x_o + outer_rect[0], y_o + outer_rect[1])

            if txt:
                inner_rect = (int(size[0] * 0.1), int(size[0] * 0.1))
                x_i = int(x - inner_rect[0] * 0.5)
                y_i = int(y - inner_rect[1] * 0.5)
                widget.create_rectangle(x_i, y_i, x_i + inner_rect[0], y_i + inner_rect[1],
                                        fill=str(get_color(BLACK)))
        else:
            txt = str(txt)
            if len(txt) >= 100:
                txt = '{}...'.format(txt[:97])
            widget.create_text(x, y, text=txt, font=font, fill=str(fg))
        self.left_top[0] += size[0]
        return size

    def __get_size(self, idx):
        if idx == 0:
            # create space for numbering
            key = '#'
        elif idx == 1:
            # measure selection checkbox
            key = 'M_CB'
        elif idx == 2 or idx == 3:
            # measure ID and ref no
            key = 'M_ID_REF_NO'
        else:
            # measure title
            key = 'M_TITLE'
        try:
            return int(self.cell_widths[key] * self.dimensions[0] + 1), int(self.cell_height * self.dimensions[0] + 1)
        except KeyError:
            raise RGError('Cell size with key [{}] do not exist'.format(key))
