import re
from pathlib import Path

import pandas as pd

from models import *


class TemplateDao(RGDaoBase):

    def __init__(self, year=None, path=None):
        RGDaoBase.__init__(self, year=year)
        self.path = path
        now = datetime.now()
        self.current_prefix = '%04d-%s' % (now.year - 1, str(now.year)[2:])
        self.last_prefix = '%04d-%s' % (now.year - 2, str(now.year - 1)[2:])

    @abstractmethod
    def get_templates(self):
        pass

    def get_data_frames(self):
        df_cym = pd.DataFrame()
        df_cyd = pd.DataFrame()
        templates = self.get_templates()
        for name in templates.keys():
            logging.debug('Reading [{}] templates....'.format(name))
            for template in templates[name]:
                dict_template = pd.read_excel(template, sheet_name=["CurrentYearData", "CurrentYearMeasures"])
                # IMPORTANT: reassign data frame value after append
                # otherwise data will not be saved
                temp = dict_template["CurrentYearMeasures"]
                temp.columns = map(self.parse_columns, temp.columns)
                df_cym = df_cym.append(temp)

                temp = dict_template["CurrentYearData"]
                temp.columns = map(self.parse_columns, temp.columns)
                df_cyd = df_cyd.append(temp)
        return tuple([df_cym, df_cyd])

    def parse_columns(self, column):
        val = str(column).upper().replace('\n', ' ').replace('\r', ' ').replace('\\', ' ').replace('/', ' ').replace(
            '-', ' ').replace('(', ' ').replace(')', ' ')
        val = re.sub(' +', '_', val)
        if val.endswith('_'):
            val = val[:-1]
        if val.startswith('_'):
            val = val[1:]
        return val

    def search_in_root(self, pattern=None):
        return list(Path(self.path).rglob(pattern))

    def validate_and_clean_templates(self, templates=None):
        if templates is None:
            raise RGError('Templates could not be found under provided path [{}]'.format(self.path))
        to_remove = list()
        for name in templates.keys():
            if len(templates[name]) < 2:
                to_remove.append(name)
        for name in to_remove:
            del templates[name]
            logging.debug(
                'Template file [{}] has been removed, because current or last fiscal year report is not present'.format(
                    name))
        return templates


class ExcelTemplateDao(TemplateDao):
    def __init__(self, year, path):
        TemplateDao.__init__(self, year=year, path=path)

    def get_templates(self):
        if self.path is None:
            raise RGError('Invalid template root directory provided [{}]'.format(self.path))
        templates = dict()
        for ff in self.search_in_root(pattern='*.xlsx'):
            if ff.name.startswith(self.current_prefix) or ff.name.startswith(self.last_prefix):
                t_name = ff.name.replace('{}_'.format(self.current_prefix), '').replace('{}_'.format(self.last_prefix),
                                                                                        '').replace('.xlsx', '')
                if t_name not in templates.keys():
                    templates[t_name] = list()
                templates[t_name].append(ff)

        return self.validate_and_clean_templates(templates=templates)
