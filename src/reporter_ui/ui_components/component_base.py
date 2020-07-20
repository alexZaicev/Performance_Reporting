from abc import ABC, abstractmethod

from common.models.errors import RGUIError


class RGComponentBase(ABC):

    @abstractmethod
    def build(self):
        raise RGUIError('Unimplemented method RGComponentBase.build')


class RGApplicationBase(RGComponentBase, ABC):

    @abstractmethod
    def pre_destroy(self):
        raise RGUIError('Unimplemented method RGMainUIBase.pre_destroy')
