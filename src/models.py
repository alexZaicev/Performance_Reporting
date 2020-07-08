import logging
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from constants import *
from utils import get_val, get_dir_path


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


class RGReporterOptions(object):

    def __init__(self, entities=None, exclusions=None, out_dir=None, images=None):
        object.__init__(self)
        self.entities = entities
        self.exclusions = exclusions
        self.out_dir = out_dir
        self.images = images


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

    def generate(self, options=None):
        if options is None or not isinstance(options, RGReporterOptions):
            raise RGError('Invalid report options provided')
        logging.info('Generating report...')
        self.do_init()
        self.do_compose(options=options)
        self.do_prepare_export(out_dir=options.out_dir)
        self.do_export(out_dir=options.out_dir)
        self.do_clean()
        logging.info('Report successfully generated! [{}]'.format(options.out_dir))

    @abstractmethod
    def do_compose(self, options=None):
        if self.report is None:
            raise RGError('PDF document has not been initialized')
        if options.entities is None or len(options.entities) < 1:
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

    @staticmethod
    def do_clean():
        tmp_dir = get_dir_path(TEMP)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)


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
            CPM: RGEntityFactory.__create_cpm_entity,
            SDM: RGEntityFactory.__create_sdm_entity,
            SSG: RGEntityFactory.__create_ssg_entity,
            UNKNOWN: RGEntityFactory.__create_unknown_entity
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

    @staticmethod
    def __create_unknown_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return UnknownEntity(data_lfy=data_lfy, data_cfy=data_cfy)


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
            CPM: RGDataFactory.__create_cpm_data,
            SDM: RGDataFactory.__create_sdm_data,
            SSG: RGDataFactory.__create_ssg_data,
            UNKNOWN: RGDataFactory.__create_unknown_data
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

    @staticmethod
    def __create_unknown_data(df=None):
        return UnknownData(df=df)


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

    def __init__(self, m_type=CPM, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class SdmEntity(RGEntityBase):

    def __init__(self, m_type=SDM, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class SsgEntity(RGEntityBase):

    def __init__(self, m_type=SSG, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class UnknownEntity(RGEntityBase):

    def __init__(self, m_type=UNKNOWN, data_lfy=None, data_cfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_lfy=data_lfy, data_cfy=data_cfy)


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


class SdmData(RGDataBase):

    def __init__(self, m_type=SDM, df=None):
        RGDataBase.__init__(self, m_type=m_type, df=df)


class SsgData(RGDataBase):

    def __init__(self, m_type=SSG, df=None):
        RGDataBase.__init__(self, m_type=m_type, df=df)


class UnknownData(RGDataBase):
    def __init__(self, m_type=UNKNOWN, df=None):
        RGDataBase.__init__(self, m_type=m_type, df=df)
        self.measureTextColumn1 = get_val(df, MEASURE_TEXT_COLUMN_1)
        self.measureTextColumn2 = get_val(df, MEASURE_TEXT_COLUMN_2)
