from abc import ABC, abstractmethod
from constants import *
from datetime import datetime
import logging
import os
import shutil

from utils import get_val, get_lfy_prefix, get_cfy_prefix, get_dir_path


class RGError(Exception):
    """
    RG custom error
    """
    pass


class RGColor(object):

    def __init__(self, r=0, g=0, b=0):
        object.__init__(self)
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return '#{}{}{}'.format(
            self.__ff(self.r),
            self.__ff(self.g),
            self.__ff(self.b)
        )

    # return 'rgb({}, {}, {})'.format(self.r, self.g, self.b)
    # return '#{}{}{}'.format(
    #     hex(self.r)[2:],
    #     hex(self.g)[2:],
    #     hex(self.b)[2:]
    # )

    @staticmethod
    def __ff(val):
        h = hex(val)[2:]
        if len(h) == 1:
            h = '0{}'.format(h)
        return h


class RGModel(ABC):

    def __init__(self, m_type=None, df=None):
        if m_type is None or df is None:
            raise RGError('Invalid measure type [{}] or data frame [{}] provided'.format(m_type, df))
        self.m_type = m_type
        self.f_year = get_val(df, FISCAL_YEAR)
        self.m_id = get_val(df, MEASURE_ID)
        self.m_ref_no = get_val(df, MEASURE_REF_NO)
        self.m_title = get_val(df, MEASURE_TITLE)


class RGEntityBase(ABC):

    def __init__(self, m_type=None, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        self.m_type = m_type
        self.data_cfy = data_cfy
        self.data_lfy = data_lfy
        self.measure_cfy = measure_cfy
        self.measure_lfy = measure_lfy

    def data(self):
        return self.data_lfy + self.data_cfy

    def get_measure(self, data):
        if data is not None:
            if data.m_type == self.measure_cfy.m_type and data.f_year == self.measure_cfy.f_year and \
                    data.m_id == self.measure_cfy.m_id and data.m_ref_no == self.measure_cfy.m_ref_no:
                return self.measure_cfy
            else:
                return self.measure_lfy
        return None


class RGMeasureBase(RGModel):
    """
    RG measure base class
    """

    def __init__(self, m_type=None, df=None):
        RGModel.__init__(self, m_type=m_type, df=df)
        self.m_desc = get_val(df, MEASURE_DESCRIPTION)
        self.frequency = get_val(df, FREQUENCY_MONTHLY_QUARTERLY_1_2_YEARLY_ANNUAL)
        self.outcome = get_val(df, OUTCOME)
        self.outcome_no = get_val(df, OUTCOME_NO)
        self.outcome_priority_no = get_val(df, OUTCOME_PRIORITY_NO)
        self.priority = get_val(df, PRIORITY)
        self.additional_kpi_information = get_val(df, ADDITIONAL_KPI_INFO)
        self.new_existing = get_val(df, NEW_EXISTING)
        self.pref_dot = get_val(df, PREFERRED_DOT)
        self.aim = get_val(df, AIM)
        self.data_format = get_val(df, DATA_FORMAT)
        self.data_presented = get_val(df, DATA_PRESENTED)
        self.baseline = get_val(df, BASELINE)
        self.tolerance = get_val(df, TOLERANCES)
        self.directorate = get_val(df, DIRECTORATE)
        self.cabinet_member_portfolio = get_val(df, CABINET_MEMBER_PORTFOLIO)
        self.corporate_director = get_val(df, CORPORATE_DIRECTOR)
        self.responsible_officer = get_val(df, RESPONSIBLE_OFFICER)
        self.measure_owner = get_val(df, MEASURE_OWNER)
        self.data_source = get_val(df, DATA_SOURCE)
        self.expected_availability = get_val(df, EXPECTED_AVAILABILITY)
        self.final_dqaf_received = get_val(df, FINAL_DQAF_RECEIVED)
        self.theme = get_val(df, THEME)
        self.theme_priority_no = get_val(df, THEME_PRIORITY_NO)


class RGDataBase(RGModel):
    """
    RG data base class
    """

    def __init__(self, m_type=None, df=None):
        RGModel.__init__(self, m_type=m_type, df=df)
        self.frequency = get_val(df, FREQUENCY)
        self.quarter = get_val(df, QUARTER)
        self.month = get_val(df, MONTH)
        self.result = get_val(df, RESULT)
        self.target = get_val(df, TARGET)
        self.performance = get_val(df, PERFORMANCE)
        self.varianceFromTarget = get_val(df, VARIANCE_FROM_TARGET)
        self.dotFromPreviousMonth = get_val(df, DOT_FROM_PREVIOUS_MONTH)
        self.dotFromPreviousQuarter = get_val(df, DOT_FROM_PREVIOUS_QUARTER)
        self.dotFromSamePeriodLastYear = get_val(df, DOT_FROM_SAME_PERIOD_LAST_YEAR)
        self.status = get_val(df, STATUS_PROVISIONAL_CONFIRMED)
        self.directorateComments = get_val(df, DIRECTORATE_COMMENTARY)
        self.reportComments = get_val(df, REPORT_COMMENTARY)
        self.benchmarkableNationally = get_val(df, BENCHMARKABLE_NATIONALLY)
        self.benchmarkResult = get_val(df, BENCHMARK_RESULT)
        self.benchmarkGroup = get_val(df, BENCHMARK_GROUP_FOR_REPORTING_PURPOSES)
        self.birmResultAtBenchmark = get_val(df, BIRMINGHAM_RESULT_AT_TIME_OF_BENCHMARK)
        self.birmQuartilePosition = get_val(df, BIRMINGHAM_QUARTILE_POSITION)
        self.yearOfBenchmarkData = get_val(df, YEAR_OF_BENCHMARK_DATA)
        self.reasonOfNonNationalBenchmark = get_val(df, REASON_FOR_NON_NATIONAL_BENCHMARK_IF_RELEVANT)
        self.quartileProjection = get_val(df, QUARTILE_PROJECTION)
        self.assistantDirectorSignOff = get_val(df, ASSISTANT_DIRECTOR_SIGN_OFF)
        self.dmtSignOffDate = get_val(df, DMT_SIGN_OFF_DATE)
        self.cabinetMembersSignOffDate = get_val(df, CABINET_MEMBERS_SIGN_OFF_DATE)
        self.year = get_val(df, YEAR)
        self.yearMonth = get_val(df, YEAR_MONTH)
        self.yearQuarter = get_val(df, YEAR_QUARTER)


class RGReporterBase(ABC):
    """
    RG reporter base class
    """

    def __init__(self):
        self.report = None
        self.report_name = REPORT_NAME

    def do_init(self):
        tmp_dir = get_dir_path(TEMP)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)

    def generate(self, entities=None, exclusions=None, out_dir=None):
        logging.info('Generating report...')
        self.do_init()
        self.do_compose(entities=entities, exclusions=exclusions)
        self.do_prepare_export(out_dir=out_dir)
        self.do_export(out_dir=out_dir)
        self.do_clean()
        logging.info('Report successfully generated! [{}]'.format(out_dir))

    @abstractmethod
    def do_compose(self, entities=None, exclusions=None):
        if self.report is None:
            raise RGError('PDF document has not been initialized')
        if entities is None or len(entities) < 1:
            raise RGError('No measures provided to PDF report generator')

    def do_prepare_export(self, out_dir=None):
        if self.report is None:
            raise RGError('Report document has not been initialized')
        if out_dir is None:
            raise RGError('Invalid report output directory provided [{}]'.format(out_dir))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    @abstractmethod
    def do_export(self, out_dir=None):
        with open(os.path.join(out_dir, self.report_name), 'w') as ff:
            ff.write(self.report)

    def do_clean(self):
        tmp_dir = get_dir_path(TEMP)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)


class RGDaoBase(ABC):

    def __init__(self, year=None):
        if year is None:
            year = datetime.now().year
        self.year = year
        self.__entities = None

    @abstractmethod
    def get_data_frames(self):
        raise RGError('Unimplemented method RGDaoBase.get_data_frame')

    def get_entities(self):
        if self.__entities is not None:
            return self.__entities
        self.__create_measures()
        return self.__entities

    def __create_measures(self):
        df_cym, df_cyd = self.get_data_frames()
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

        logging.debug('[{}] entities has been parsed'.format(len(self.__entities)))

    @staticmethod
    def __get_data_for_measure(measure, data_list):
        result = list()
        for data in data_list:
            if measure.m_type == data.m_type and measure.m_id == data.m_id and \
                    measure.f_year == data.f_year and measure.m_ref_no == data.m_ref_no:
                result.append(data)
        result.sort(key=lambda x: '{} {}'.format(x.f_year, x.month))
        return result


class RGEntityFactory(object):
    """
    RG entity factory
    """

    def __init__(self):
        raise RGError('Factory classes cannot be initialized')

    def __new__(cls):
        raise RGError('Factory classes cannot be initialized')

    @staticmethod
    def create_entity(m_type=None, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        """
        Create measure by measure type

        :param m_type: Measure type
        :param data_cfy: Current fiscal year data list
        :param data_lfy: Last fiscal year data list
        :param measure_cfy: Current fiscal year measure object
        :param measure_lfy: Last fiscal year measure object
        :return:
        """
        __TYPE_CREATION_MAP = {
            'CPM': RGEntityFactory.__create_cpm_entity,
            'SDM': RGEntityFactory.__create_sdm_entity,
            'SSG': RGEntityFactory.__create_ssg_entity
        }
        try:
            fun = __TYPE_CREATION_MAP[m_type]
            return fun(data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy, measure_lfy=measure_lfy)
        except AttributeError:
            raise RGError("Unknown measure type {}".format(m_type))

    @staticmethod
    def __create_cpm_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return CpmEntity(data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy, measure_lfy=measure_lfy)

    @staticmethod
    def __create_sdm_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return SdmEntity(data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy, measure_lfy=measure_lfy)

    @staticmethod
    def __create_ssg_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return SsgEntity(data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy, measure_lfy=measure_lfy)


class RGDataFactory(object):
    """
    RG data factory
    """

    def __init__(self):
        raise RGError('Factory classes cannot be initialized')

    def __new__(cls):
        raise RGError('Factory classes cannot be initialized')

    @staticmethod
    def create_data(m_type=None, df=None):
        """
        Create measure by measure type

        :param m_type: Measure type
        :param df: Year data
        :return:
        """
        __TYPE_CREATION_MAP = {
            'CPM': RGDataFactory.__create_cpm_data,
            'SDM': RGDataFactory.__create_sdm_data,
            'SSG': RGDataFactory.__create_ssg_data
        }
        try:
            fun = __TYPE_CREATION_MAP[m_type]
            return fun(df=df)
        except AttributeError:
            raise RGError("Unknown measure type {}".format(m_type))

    @staticmethod
    def __create_cpm_data(df=None):
        return CpmData(df=df)

    @staticmethod
    def __create_sdm_data(df=None):
        return SdmData(df=df)

    @staticmethod
    def __create_ssg_data(df=None):
        return SsgData(df=df)


class RGMeasureFactory(object):
    """
    RG measure factory
    """

    def __init__(self):
        raise RGError('Factory classes cannot be initialized')

    def __new__(cls):
        raise RGError('Factory classes cannot be initialized')

    @staticmethod
    def create_measure(m_type=None, df=None):
        """
        Create measure by measure type

        :param m_type: Measure type
        :param df: Year Measure
        :return:
        """
        __TYPE_CREATION_MAP = {
            'CPM': RGMeasureFactory.__create_cpm_measure,
            'SDM': RGMeasureFactory.__create_sdm_measure,
            'SSG': RGMeasureFactory.__create_ssg_measure
        }
        try:
            fun = __TYPE_CREATION_MAP[m_type]
            return fun(df=df)
        except AttributeError:
            raise RGError("Unknown measure type {}".format(m_type))

    @staticmethod
    def __create_cpm_measure(df=None):
        return CpmMeasure(df=df)

    @staticmethod
    def __create_sdm_measure(df=None):
        return SdmMeasure(df=df)

    @staticmethod
    def __create_ssg_measure(df=None):
        return SsgMeasure(df=df)


#####################################################################################
# Entity Models
#####################################################################################

class CpmEntity(RGEntityBase):

    def __init__(self, m_type=None, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=CPM, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class SdmEntity(RGEntityBase):

    def __init__(self, m_type=None, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=SDM, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class SsgEntity(RGEntityBase):

    def __init__(self, m_type=None, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=SSG, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


#####################################################################################
# Measure Models
#####################################################################################

class CpmMeasure(RGMeasureBase):

    def __init__(self, m_type=CPM, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)


class SdmMeasure(RGMeasureBase):

    def __init__(self, m_type=SDM, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)


class SsgMeasure(RGMeasureBase):

    def __init__(self, m_type=SSG, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)


#####################################################################################
# Data Models
#####################################################################################

class CpmData(RGDataBase):

    def __init__(self, m_type=CPM, df=None):
        RGDataBase.__init__(self, m_type=m_type, df=df)

    def load_df(self, df=None):
        pass


class SdmData(RGDataBase):

    def __init__(self, m_type=SDM, df=None):
        RGDataBase.__init__(self, m_type=m_type, df=df)

    def load_df(self, df=None):
        pass


class SsgData(RGDataBase):

    def __init__(self, m_type=SSG, df=None):
        RGDataBase.__init__(self, m_type=m_type, df=df)

    def load_df(self, df=None):
        pass
