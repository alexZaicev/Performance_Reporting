from abc import ABC

from constants import LEGEND, OFSTED, RISK_MAP, WORKFORCE_EXPENDITURE
from dao.dao_base import RGDaoBase
from models.errors import RGError


class FileDao(RGDaoBase, ABC):

    def __init__(self, path):
        RGDaoBase.__init__(self)
        self.path = path

    def get_entities(self):
        return None


class ImageFileDao(FileDao):

    def __init__(self, path):
        FileDao.__init__(self, path)

    def get_files(self):
        if self.path is None:
            raise RGError('Invalid image file root directory provided [{}]'.format(self.path))
        images = dict()
        for ff in self.search_in_root(path=self.path, pattern='*.png'):
            name = ff.name.upper().replace(' ', '_')
            f_path = str(ff)
            if LEGEND in name:
                images[LEGEND] = f_path
            elif OFSTED in name:
                images[OFSTED] = f_path
            elif RISK_MAP in name:
                images[RISK_MAP] = f_path
            elif WORKFORCE_EXPENDITURE in name:
                images[WORKFORCE_EXPENDITURE] = f_path
        return images
