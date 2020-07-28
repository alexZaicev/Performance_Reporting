from reporter_ui.components.widgets.dialog_base import RGDialogBase
from reporter_ui.components.widgets.label import RGLabel
from reporter_ui.components.widgets.loading_indicator import RGLoadingIndicator


class RGLoadingDialog(RGDialogBase):

    def __init__(self, message=None, **kwargs):
        RGDialogBase.__init__(self, **kwargs)
        self.dialog.protocol('WM_DELETE_WINDOW', self.__dialog_no_close)
        self.dialog.resizable(0, 0)
        self.dimensions = (int(self.window.size[0] * 0.45), int(self.window.size[1] * 0.15))
        self.widgets = [
            RGLabel(config=self.config, text=message, custom_pack=True, rel_x=0.5, rel_y=0.2),
            RGLoadingIndicator(config=self.config, custom_pack=True,
                               rel_x=0.5, rel_y=0.6)
        ]

    def __dialog_no_close(self):
        pass

    def dismiss(self):
        self.widgets[1].unload()
        super().dismiss()
