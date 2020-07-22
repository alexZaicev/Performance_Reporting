import logging
from abc import ABC

from common.constants import LEGEND, OFSTED, RISK_MAP, WORKFORCE_EXPENDITURE, SCHOOLS_IN_DEFICIT, FINAL_AUDIT_REPORT
from reporter_tool.dao.dao_base import RGDaoBase
from common.models.errors import RGError
from common.models.utilities import RGFile, RGFileContainer
from common.utils import try_parse, get_cfy_prefix


class FileDao(RGDaoBase, ABC):

    def __init__(self, year=None, month=None, path=None):
        RGDaoBase.__init__(self, year=year, month=month)
        self.path = path

    def get_entities(self):
        return None

    @staticmethod
    def get_fym_from_name(name):
        tokens = name.split('_')
        year = try_parse(tokens[0].split('-')[0], is_int=True)
        month = try_parse(tokens[1], is_int=True)
        if year is not None and month is not None:
            return try_parse('{}{:02d}'.format(get_cfy_prefix(cfy=year).replace('-', ''), month), is_int=True)
        return None

    def create_file(self, f_type, f_path, name):
        if f_type is None or f_path is None or name is None:
            raise RGError(
                'One of the file fields does not contain valid information. Type: [{}] Path [{}] Name [{}]'.format(
                    f_type, f_path, name))
        return RGFile(f_type=f_type, name=name, path=f_path, fym=self.get_fym_from_name(name))


class ImageFileDao(FileDao):

    def __init__(self, year=None, month=None, path=None):
        FileDao.__init__(self, year=year, month=month, path=path)

    def get_files(self):
        if self.path is None:
            raise RGError('Invalid image file root directory provided [{}]'.format(self.path))
        images = list()
        ff_paths = self.search_in_root(path=self.path, pattern='*.png')
        ff_paths.sort(key=lambda x: (x.parent.name, x.name.upper().replace(' ', '_')))
        for ff in ff_paths:
            name = ff.name.upper().replace(' ', '_')
            f_type = self.__get_image_type(name)
            if f_type is not None:
                images.append(self.create_file(f_type, str(ff), name))
            else:
                logging.getLogger(__name__).error('Could not get image file type from name [{}]'.format(name))

        return RGFileContainer(images)

    @staticmethod
    def __get_image_type(name):
        f_type = None
        if LEGEND in name:
            f_type = LEGEND
        elif OFSTED in name:
            f_type = OFSTED
        elif RISK_MAP in name:
            f_type = RISK_MAP
        elif WORKFORCE_EXPENDITURE in name:
            f_type = WORKFORCE_EXPENDITURE
        elif SCHOOLS_IN_DEFICIT in name:
            f_type = SCHOOLS_IN_DEFICIT
        elif FINAL_AUDIT_REPORT in name:
            f_type = FINAL_AUDIT_REPORT
        return f_type
