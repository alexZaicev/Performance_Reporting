import logging
from abc import abstractmethod
from pathlib import Path

import pandas as pd

from constants import *
from models import RGDaoBase, RGError
from utils import get_cfy_prefix, get_lfy_prefix, parse_columns
from xlrd.biffh import XLRDError


class TemplateDao(RGDaoBase):

    def __init__(self, year=None, path=None):
        RGDaoBase.__init__(self, year=year)
        self.path = path
        self.current_prefix = get_cfy_prefix()
        self.last_prefix = get_lfy_prefix()

    @abstractmethod
    def get_templates(self):
        pass

    def get_data_frames(self):
        df_cym = pd.DataFrame()
        df_cyd = pd.DataFrame()
        df_unknown = pd.DataFrame()
        templates = self.get_templates()
        for name in templates.keys():
            logging.debug('Reading [{}] templates....'.format(name))
            for template in templates[name]:
                try:
                    dict_template = pd.read_excel(template, sheet_name=[CURRENT_YEAR_DATA, CURRENT_YEAR_MEASURES],
                                                  encoding='utf-8')
                    # IMPORTANT: reassign data frame value after append
                    # otherwise data will not be saved
                    temp = dict_template[CURRENT_YEAR_MEASURES]
                    temp.columns = map(parse_columns, temp.columns)
                    df_cym = df_cym.append(temp)

                    temp = dict_template[CURRENT_YEAR_DATA]
                    temp.columns = map(parse_columns, temp.columns)
                    df_cyd = df_cyd.append(temp)

                    df_cyd.loc[:, YEAR_MONTH] = df_cyd.loc[:, FISCAL_YEAR].str.replace("-", "").str.cat(
                        df_cyd.loc[:, MONTH].str[1:3])
                    df_cyd.loc[:, YEAR_QUARTER] = df_cyd.loc[:, FISCAL_YEAR].str.replace("-", "").str.cat(
                        df_cyd.loc[:, QUARTER].str[1:2])
                    df_cyd.loc[:, YEAR] = df_cyd.loc[:, FISCAL_YEAR].str.replace("-", "")
                except XLRDError as e:
                    logging.warning('Failed to read template [{}] as measure data source [{}]'.format(template, str(e)))

                    dict_template = pd.read_excel(template, sheet_name=[PMT_ADDITIONAL_DATA], encoding='utf-8')
                    temp = dict_template[PMT_ADDITIONAL_DATA]
                    temp.columns = map(parse_columns, temp.columns)
                    df_unknown = df_unknown.append(temp)

        return tuple([df_cym, df_cyd, df_unknown])

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
