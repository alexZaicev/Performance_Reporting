from reporter_ui.components.component_base import RGComponentBase


class ButtonsFrame(RGComponentBase):

    def __init__(self, config=None, window=None):
        RGComponentBase.__init__(self, config=config, window=window)

    def build(self):
        super().build()
