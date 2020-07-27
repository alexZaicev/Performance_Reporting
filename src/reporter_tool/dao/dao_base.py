from abc import ABC, abstractmethod
from pathlib import Path

from common.models.errors import RGError


class RGDaoBase(ABC):

    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month

    @abstractmethod
    def get_entities(self):
        raise RGError('Unimplemented method RGDaoBase.get_entities')

    @abstractmethod
    def get_files(self):
        raise RGError('Unimplemented method RGDaoBase.get_files')

    @staticmethod
    def search_in_root(path=None, pattern=None):
        return list(Path(path).rglob(pattern))
