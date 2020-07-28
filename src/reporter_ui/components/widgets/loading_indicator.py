from itertools import count
from os.path import join

from PIL import ImageTk, Image

from common.constants import RESOURCES, DIM_WHITE
from common.utils import get_dir_path
from reporter_ui.components.widgets.label import RGLabel
from reporter_ui.components.widgets.widget_base import RGWidgetBase


class RGLoadingIndicator(RGWidgetBase):

    def __init__(self, **kwargs):
        RGWidgetBase.__init__(self, **kwargs)
        self.__loc = 0
        self.__frames = []
        self.__delay = 100

    def build(self):
        super().build()
        self.widget = RGLabel(window=self.window, config=self.config, color=DIM_WHITE, custom_pack=True,
                              rel_x=self.rel_xy[0], rel_y=self.rel_xy[1])
        self.widget.build()
        self.__load(join(get_dir_path(RESOURCES), 'loading_indicator.gif'))

    def unload(self):
        self.widget.widget.config(image="")
        self.__frames = None

    def __load(self, img_path):
        img = Image.open(img_path)
        self.__loc = 0
        self.__frames = []

        try:
            for i in count(1):
                self.__frames.append(ImageTk.PhotoImage(img.copy()))
                img.seek(i)
        except EOFError:
            pass

        try:
            self.__delay = img.info['duration']
        except KeyError:
            pass

        if len(self.__frames) == 1:
            self.widget.widget.config(image=self.__frames[0])
        else:
            self.__next_frame()

    def __next_frame(self):
        if self.__frames:
            self.__loc += 1
            self.__loc %= len(self.__frames)
            self.widget.widget.configure(image=self.__frames[self.__loc])
            self.widget.widget.after(self.__delay, self.__next_frame)
