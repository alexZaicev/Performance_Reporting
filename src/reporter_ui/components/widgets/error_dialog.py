from common.text import *
from reporter_ui.components.widgets.button import RGButton
from reporter_ui.components.widgets.dialog_base import RGDialogBase
from reporter_ui.components.widgets.label import RGLabel


class RGErrorDialog(RGDialogBase):

    def __init__(self, message=None, **kwargs):
        RGDialogBase.__init__(self, **kwargs)
        self.dimensions = (int(self.window.size[0] * 0.45), int(self.window.size[1] * 0.15))
        self.widgets = [
            RGLabel(config=self.config, text=message, custom_pack=True, rel_x=0.5, rel_y=0.2),
            RGButton(config=self.config, text=OK, custom_pack=True, callback=self.dismiss,
                     width=self.dimensions[0] * 0.02, height=self.dimensions[1] * 0.005, rel_x=0.5, rel_y=0.8)
        ]
