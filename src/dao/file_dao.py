from abc import ABC

from constants import LEGEND, OFSTED, RISK_MAP, WORKFORCE_EXPENDITURE, SCHOOLS_IN_DEFICIT, FINAL_AUDIT_REPORT
from dao.dao_base import RGDaoBase
from models.errors import RGError
from utils import try_parse, get_cfy_prefix


class FileDao(RGDaoBase, ABC):

    def __init__(self, year=None, month=None, path=None):
        RGDaoBase.__init__(self, year=year, month=month)
        self.path = path

    def get_entities(self):
        return None


class ImageFileDao(FileDao):

    def __init__(self, year=None, month=None, path=None):
        FileDao.__init__(self, year=year, month=month, path=path)

    def get_files(self):
        if self.path is None:
            raise RGError('Invalid image file root directory provided [{}]'.format(self.path))
        images = dict()
        ff_paths = self.search_in_root(path=self.path, pattern='*.png')
        ff_paths.sort(key=lambda x: (x.parent.name, x.name.upper().replace(' ', '_')))
        for ff in ff_paths:
            name = ff.name.upper().replace(' ', '_')

            if self.__is_valid_date(name):
                f_path = str(ff)
                if LEGEND in name:
                    images[LEGEND] = f_path
                elif OFSTED in name:
                    images[OFSTED] = f_path
                elif RISK_MAP in name:
                    images[RISK_MAP] = f_path
                elif WORKFORCE_EXPENDITURE in name:
                    images[WORKFORCE_EXPENDITURE] = f_path
                elif SCHOOLS_IN_DEFICIT in name:
                    images[SCHOOLS_IN_DEFICIT] = f_path
                elif FINAL_AUDIT_REPORT in name:
                    images[FINAL_AUDIT_REPORT] = f_path
        return images

    def __is_valid_date(self, name):
        tokens = name.split('_')
        year = try_parse(tokens[0].split('-')[0], is_int=True)
        month = try_parse(tokens[1], is_int=True)

        if year is not None and month is not None:
            stamp = try_parse('{}{:02d}'.format(get_cfy_prefix(cfy=year).replace('-', ''), month), is_int=True)
            conf_stamp = try_parse('{}{:02d}'.format(get_cfy_prefix(cfy=self.year).replace('-', ''), self.month), is_int=True)
            return conf_stamp >= stamp
        return False
