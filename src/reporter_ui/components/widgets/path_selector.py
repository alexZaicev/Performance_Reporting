from os.path import sep
from tkinter import Frame, StringVar, filedialog

from common.models.errors import RGError
from common.utils import get_color, DIM_WHITE
from reporter_ui.components.widgets.button import RGButton
from reporter_ui.components.widgets.label import RGLabel
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGPathSelector(RGWidgetBase):

    def __init__(self, text=None, text_var=None, is_dir=False, callback=None, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.text = text
        self.text_var = text_var
        self.is_dir = is_dir
        self.callback = callback

    def build(self):
        super().build()
        xy = list(self.xy)
        lbl = RGLabel(window=self.window, config=self.config, text='{}:'.format(self.text), x=xy[0],
                      y=xy[1], font_size=10, font_weight='bold')
        lbl.build()
        xy[1] += lbl.size()[1]
        frame = Frame(master=self.window, width=int(self.dimensions[0] - 10), height=int(self.dimensions[0] * 0.08))
        frame.configure(bg=str(get_color(DIM_WHITE)), borderwidth=1, relief='groove')
        frame.place(x=xy[0], y=xy[1])

        lbl_path = RGLabel(window=frame, config=self.config, text_var=self.text_var, color=DIM_WHITE,
                           width=self.dimensions[0] * 0.095, height=self.dimensions[0] * 0.004,
                           x=self.dimensions[0] * 0.01, y=self.dimensions[0] * 0.012)
        lbl_path.build()

        button = RGButton(window=frame, config=self.config, text='...', callback=self.callback,
                          height=self.dimensions[0] / 2 * 0.008, width=self.dimensions[0] / 2 * 0.01,
                          x=self.dimensions[0] * 0.91, y=self.dimensions[0] * 0.01
                          )
        button.build()

        self.window.master.update()
        self.dimensions = (frame.winfo_width(), frame.winfo_height() + lbl.size()[1])

    @staticmethod
    def browse(var, is_dir=False):
        if not isinstance(var, StringVar):
            raise RGError('StringVar expected actual [{}]'.format(type(var)))

        if is_dir:
            filename = filedialog.askdirectory()
        else:
            filename = filedialog.askopenfilename()

        if filename is not None and len(filename) > 0:
            filename = str(filename).replace('/', sep)
            return filename
        return None
