from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from models.errors import RGError


class RGDaoBase(ABC):

    def __init__(self, year=None):
        if year is None:
            year = datetime.now().year
        self.year = year

    @abstractmethod
    def get_entities(self):
        raise RGError('Unimplemented method RGDaoBase.get_entities')

    @abstractmethod
    def get_files(self):
        raise RGError('Unimplemented method RGDaoBase.get_files')

    def search_in_root(self, path=None, pattern=None):
        return list(Path(path).rglob(pattern))
