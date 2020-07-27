from tkinter import CENTER

from reporter_ui.components.widgets.button import RGButton
from reporter_ui.components.widgets.dialog_base import RGDialogBase
from reporter_ui.components.widgets.label import RGLabel


class RGConfirmDialog(RGDialogBase):

    def __init__(self, message=None, p_text=None, n_text=None, p_callback=None, n_callback=None, rel_px=0.7, rel_nx=0.3,
                 **kwargs):
        RGDialogBase.__init__(self, **kwargs)
        self.dimensions = (int(self.window.size[0] * 0.45), int(self.window.size[1] * 0.15))

        if n_callback is None:
            n_callback = self.dismiss
        if p_callback is None:
            p_callback = self.dismiss

        self.widgets = [
            RGLabel(config=self.config, text=message, custom_pack=True, rel_x=0.5, rel_y=0.2,
                    wrap_width=int(self.dimensions[0] * 0.95), justify=CENTER),
            RGButton(config=self.config, text=n_text, custom_pack=True, callback=n_callback,
                     width=self.dimensions[0] * 0.02, height=self.dimensions[1] * 0.005, rel_x=rel_nx, rel_y=0.8),
            RGButton(config=self.config, text=p_text, custom_pack=True, callback=p_callback,
                     width=self.dimensions[0] * 0.02, height=self.dimensions[1] * 0.005, rel_x=rel_px, rel_y=0.8)
        ]
