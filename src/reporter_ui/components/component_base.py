from abc import ABC, abstractmethod

from common.models.errors import RGError


class RGComponentBase(ABC):

    def __init__(self, config=None, window=None, is_window=False, off_set=0.97, **kwargs):
        ABC.__init__(self)
        self.config = config
        self.window = window
        self.is_window = is_window
        self.off_set = off_set

    @abstractmethod
    def build(self):
        if self.config is None:
            raise RGError('Cannot render reporting tool with invalid configuration')
        if self.window is None and not self.is_window:
            raise RGError('Component cannot be rendered on an undefined application window')


class RGApplicationBase(RGComponentBase, ABC):

    def __init__(self, config=None, width=1024, height=860):
        RGComponentBase.__init__(self, config=config, is_window=True)
        self.size = (width, height)

    @abstractmethod
    def pre_destroy(self):
        raise RGError('Unimplemented method RGMainUIBase.pre_destroy')
