import logging
from abc import abstractmethod, ABC

import pandas as pd
from xlrd.biffh import XLRDError

from constants import *
from models import RGDaoBase, RGError, RGEntityFactory, RGDataFactory, RGMeasureFactory
from utils import get_cfy_prefix, get_lfy_prefix, parse_columns, get_val


class TemplateDao(RGDaoBase, ABC):

    def __init__(self, year=None, path=None):
        RGDaoBase.__init__(self, year=year)
        self.path = path
        self.current_prefix = get_cfy_prefix()
        self.last_prefix = get_lfy_prefix()
        self.__entities = None

    @abstractmethod
    def get_templates(self):
        raise RGError('Unimplemented method TemplateDao.get_templates')

    def get_files(self):
        return None

    def get_entities(self):
        if self.__entities is not None:
            return self.__entities
        self.__create_measures()
        return self.__entities

    def get_data_frames(self):
        df_cym = pd.DataFrame()
        df_cyd = pd.DataFrame()
        df_unknown = pd.DataFrame()
        templates = self.__validate_and_clean_templates(self.get_templates())
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

    def __validate_and_clean_templates(self, templates=None):
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

    def __create_measures(self):
        df_cym, df_cyd, df_unknown = self.get_data_frames()
        if df_cym is None:
            raise RGError('Unable to create measures from invalid data frame object [{}]'.format(df_cym))
        self.__entities = list()

        d_list = list()
        m_list = list()
        m_ids = set()

        for idx, line in df_cym.iterrows():
            m = RGMeasureFactory.create_measure(m_type=get_val(line, MEASURE_TYPE).upper(), df=line)
            m_ids.add(m.m_id)
            m_list.append(m)
        for idx, line in df_cyd.iterrows():
            d_list.append(RGDataFactory.create_data(m_type=get_val(line, MEASURE_TYPE).upper(), df=line))

        m_ids = sorted(m_ids)
        m_list.sort(key=lambda x: x.m_id)
        d_list.sort(key=lambda x: x.m_id)

        for m_id in m_ids:
            m_cfy = None
            m_lfy = None
            d_cfy = None
            d_lfy = None
            for m in m_list:
                if m.m_id == m_id:
                    if m.f_year == get_cfy_prefix():
                        m_cfy = m
                        continue
                    if m.f_year == get_lfy_prefix():
                        m_lfy = m
                        continue
            if m_cfy is not None:
                d_cfy = self.__get_data_for_measure(m_cfy, d_list)
            if m_lfy is not None:
                d_lfy = self.__get_data_for_measure(m_lfy, d_list)
            if m_cfy is not None and m_lfy is not None and \
                    d_cfy is not None and len(d_cfy) > 0 and \
                    d_lfy is not None and len(d_lfy) > 0:
                self.__entities.append(
                    RGEntityFactory.create_entity(m_type=m_cfy.m_type, data_cfy=d_cfy, data_lfy=d_lfy,
                                                  measure_cfy=m_cfy, measure_lfy=m_lfy))
        # parse unknown data frame
        self.__parse_unknown_data(df_unknown)

        logging.debug('[{}] entities has been parsed'.format(len(self.__entities)))

    def __parse_unknown_data(self, df_unknown=None):
        if df_unknown is None or df_unknown.size == 0:
            return
        d_list = list()
        for idx, line in df_unknown.iterrows():
            d_list.append(RGDataFactory.create_data(m_type=UNKNOWN, df=line))

        values = sorted(set(map(lambda x: x.m_id, d_list)))
        d_list = [[y for y in d_list if y.m_id == x] for x in values]

        for d_group in d_list:
            d_cfy, d_lfy = list(), list()
            for d in d_group:
                if d.f_year == get_cfy_prefix():
                    d_cfy.append(d)
                elif d.f_year == get_lfy_prefix():
                    d_lfy.append(d)
            self.__entities.append(RGEntityFactory.create_entity(m_type=UNKNOWN, data_lfy=d_lfy, data_cfy=d_cfy))

    @staticmethod
    def __get_data_for_measure(measure, data_list):
        result = list()
        for data in data_list:
            if measure.m_type == data.m_type and measure.m_id == data.m_id and \
                    measure.f_year == data.f_year and measure.m_ref_no == data.m_ref_no:
                result.append(data)
        result.sort(key=lambda x: '{} {}'.format(x.f_year, x.month))
        return result


class FileDao(RGDaoBase, ABC):

    def __init__(self, path):
        RGDaoBase.__init__(self)
        self.path = path

    def get_entities(self):
        return None


class ExcelTemplateDao(TemplateDao):
    def __init__(self, year, path):
        TemplateDao.__init__(self, year=year, path=path)

    def get_templates(self):
        if self.path is None:
            raise RGError('Invalid template root directory provided [{}]'.format(self.path))
        templates = dict()
        for ff in self.search_in_root(path=self.path, pattern='*.xlsx'):
            if ff.name.startswith(self.current_prefix) or ff.name.startswith(self.last_prefix):
                t_name = ff.name.replace('{}_'.format(self.current_prefix), '').replace('{}_'.format(self.last_prefix),
                                                                                        '').replace('.xlsx', '')
                if t_name not in templates.keys():
                    templates[t_name] = list()
                templates[t_name].append(ff)

        return templates


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
