from abc import ABC, abstractmethod
from constants import *
from datetime import datetime
import logging


def get_val(df, key):
    val = df[key]
    if val is None or (str(val) == 'nan'):
        return ''
    else:
        return val


class RGError(Exception):
    """
    RG custom error
    """
    pass


class RGEntityBase(ABC):

    def __init__(self, m_type=None, data=None, measures=None):
        self.m_type = m_type
        self.data = data
        self.measure = measures


class RGMeasureBase(ABC):
    """
    RG measure base class
    """

    def __init__(self, m_type=None, df=None):
        if m_type is None or df is None:
            raise RGError('Invalid measure type [{}] or data frame [{}] provided'.format(m_type, df))
        self.f_year = get_val(df, FISCAL_YEAR)
        self.m_type = m_type
        self.m_id = get_val(df, MEASURE_ID)
        self.m_ref_no = get_val(df, MEASURE_REF_NO)
        self.m_title = get_val(df, MEASURE_TITLE)
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


class RGDataBase(ABC):
    """
    RG data base class
    """

    def __init__(self, m_type=None, df=None):
        if m_type is None or df is None:
            raise RGError('Invalid measure type [{}] or data frame [{}] provided'.format(m_type, df))
        self.f_year = get_val(df, FISCAL_YEAR)
        self.m_type = m_type
        self.m_id = get_val(df, MEASURE_ID)
        self.m_ref_no = get_val(df, MEASURE_REF_NO)
        self.m_title = get_val(df, MEASURE_TITLE)
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


class RGReporterBase(ABC):
    """
    RG reporter base class
    """

    @abstractmethod
    def generate(self):
        raise RGError('Unimplemented method RGBase.generate')


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
        for idx, line in df_cyd.iterrows():
            d_list.append(RGDataFactory.create_data(m_type=get_val(line, MEASURE_TYPE).upper(), df=line))
        for idx, line in df_cym.iterrows():
            m_list.append(RGMeasureFactory.create_measure(m_type=get_val(line, MEASURE_TYPE).upper(), df=line))

        for data in d_list:
            d_measures = list()
            for measure in m_list:
                if measure.m_type == data.m_type and measure.m_id == data.m_id and \
                        measure.f_year == data.f_year and measure.m_ref_no == data.m_ref_no:
                    d_measures.append(measure)
            self.__entities.append(RGEntityFactory.create_entity(m_type=data.m_type, data=data, measures=d_measures))
        logging.debug('[{}] entities has been parsed'.format(len(self.__entities)))


class RGEntityFactory(object):
    """
    RG entity factory
    """

    def __init__(self):
        raise RGError('Factory classes cannot be initialized')

    def __new__(cls):
        raise RGError('Factory classes cannot be initialized')

    @staticmethod
    def create_entity(m_type=None, data=None, measures=None):
        """
        Create measure by measure type

        :param m_type: Measure type
        :param data: Year data object
        :param measures: Year measure list
        :return:
        """
        __TYPE_CREATION_MAP = {
            'CPM': RGEntityFactory.__create_cpm_entity,
            'SDM': RGEntityFactory.__create_sdm_entity,
            'SSG': RGEntityFactory.__create_ssg_entity
        }
        try:
            fun = __TYPE_CREATION_MAP[m_type]
            return fun(data=data, measures=measures)
        except AttributeError:
            raise RGError("Unknown measure type {}".format(m_type))

    @staticmethod
    def __create_cpm_entity(data=None, measures=None):
        return CpmEntity(data=data, measures=measures)

    @staticmethod
    def __create_sdm_entity(data=None, measures=None):
        return SdmEntity(data=data, measures=measures)

    @staticmethod
    def __create_ssg_entity(data=None, measures=None):
        return SsgEntity(data=data, measures=measures)


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

    def __init__(self, data=None, measures=None):
        RGEntityBase.__init__(self, m_type=CPM, data=data, measures=measures)


class SdmEntity(RGEntityBase):

    def __init__(self, data=None, measures=None):
        RGEntityBase.__init__(self, m_type=SDM, data=data, measures=measures)


class SsgEntity(RGEntityBase):

    def __init__(self, data=None, measures=None):
        RGEntityBase.__init__(self, m_type=SSG, data=data, measures=measures)


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
