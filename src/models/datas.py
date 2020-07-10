from constants import *
from models.model_base import RGModelBase
from utils import get_val


class RGDataModel(RGModelBase):
    """
    RG data base class
    """

    def __init__(self, m_type=None, df=None):
        RGModelBase.__init__(self, m_type=m_type, df=df)
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


class CpmData(RGDataModel):

    def __init__(self, m_type=CPM, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class SdmData(RGDataModel):

    def __init__(self, m_type=SDM, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class SsgData(RGDataModel):

    def __init__(self, m_type=SSG, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class UnknownData(RGDataModel):
    def __init__(self, m_type=UNKNOWN, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)
        self.measureTextColumn1 = get_val(df, MEASURE_TEXT_COLUMN_1)
        self.measureTextColumn2 = get_val(df, MEASURE_TEXT_COLUMN_2)
