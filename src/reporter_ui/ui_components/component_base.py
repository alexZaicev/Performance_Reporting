from abc import ABC, abstractmethod

from common.models.errors import RGUIError


class RGComponentBase(ABC):

    @abstractmethod
    def build(self):
        raise RGUIError('Unimplemented method RGComponentBase.build')
