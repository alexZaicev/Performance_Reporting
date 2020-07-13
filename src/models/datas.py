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


class HrDataModel(RGModelBase):

    def __init__(self, m_type=None, df=None):
        RGModelBase.__init__(self, m_type=m_type, df=df)
        self.dataFormat = get_val(df, DATA_FORMAT)
        self.year = get_val(df, YEAR)
        self.yearMonth = get_val(df, YEAR_MONTH)


class CpmData(RGDataModel):

    def __init__(self, m_type=CPM, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class SdmData(RGDataModel):

    def __init__(self, m_type=SDM, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class SsgData(RGDataModel):

    def __init__(self, m_type=SSG, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class PmtAdditionalData(RGDataModel):

    def __init__(self, m_type=PMT_ADDITIONAL, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)
        self.measureTextColumn1 = get_val(df, MEASURE_TEXT_COLUMN_1)
        self.measureTextColumn2 = get_val(df, MEASURE_TEXT_COLUMN_2)


class HrScorecardData(HrDataModel):

    def __init__(self, m_type=HR_SCORECARD, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.adultSocialCare = get_val(df, ADULTS_SOCIAL_CARE)
        self.educationAndSkills = get_val(df, EDUCATION_AND_SKILLS)
        self.inclusiveGrowth = get_val(df, INCLUSIVE_GROWTH)
        self.financeAndGovernance = get_val(df, FINANCE_AND_GOVERNANCE)
        self.neighbourhoods = get_val(df, NEIGHBOURHOODS)
        self.partnershipsInsightAndPrevention = get_val(df, PARTNERSHIPS_INSIGHT_AND_PREVENTION)
        self.digitalAndCustomerServices = get_val(df, DIGITAL_AND_CUSTOMER_SERVICES)
        self.hrAndOrganizationDevelopment = get_val(df, HR_AND_ORGANISATION_DEVELOPMENT)
        self.bcc = get_val(df, BIRMINGHAM_CITY_COUNCIL)


class HrAbsencesData(HrDataModel):

    def __init__(self, m_type=HR_ABSENCES, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.adultSocialCare = get_val(df, ADULTS_SOCIAL_CARE)
        self.educationAndSkills = get_val(df, EDUCATION_AND_SKILLS)
        self.inclusiveGrowth = get_val(df, INCLUSIVE_GROWTH)
        self.financeAndGovernance = get_val(df, FINANCE_AND_GOVERNANCE)
        self.neighbourhoods = get_val(df, NEIGHBOURHOODS)
        self.partnershipsInsightAndPrevention = get_val(df, PARTNERSHIPS_INSIGHT_AND_PREVENTION)
        self.digitalAndCustomerServices = get_val(df, DIGITAL_AND_CUSTOMER_SERVICES)
        self.hrAndOrganizationDevelopment = get_val(df, HR_AND_ORGANISATION_DEVELOPMENT)
        self.bcc = get_val(df, BIRMINGHAM_CITY_COUNCIL)
        self.commonwealthGames = get_val(df, COMMONWEALTH_GAMES)


class HrSicknessData(HrDataModel):

    def __init__(self, m_type=HR_SICKNESS, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.total = get_val(df, TOTAL)
        self.percentage = get_val(df, PERCENTAGE)


class HrTrainingData(HrDataModel):

    def __init__(self, m_type=HR_TRAINING, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.adultSocialCare = get_val(df, ADULTS_SOCIAL_CARE)
        self.educationAndSkills = get_val(df, EDUCATION_AND_SKILLS)
        self.inclusiveGrowth = get_val(df, INCLUSIVE_GROWTH)
        self.financeAndGovernance = get_val(df, FINANCE_AND_GOVERNANCE)
        self.neighbourhoods = get_val(df, NEIGHBOURHOODS)
        self.partnershipsInsightAndPrevention = get_val(df, PARTNERSHIPS_INSIGHT_AND_PREVENTION)
        self.digitalAndCustomerServices = get_val(df, DIGITAL_AND_CUSTOMER_SERVICES)
        self.hrAndOrganizationDevelopment = get_val(df, HR_AND_ORGANISATION_DEVELOPMENT)
        self.bcc = get_val(df, BIRMINGHAM_CITY_COUNCIL)
        self.dateOfData = get_val(df, DATE_OF_DATA)
        self.commonwealthGames = get_val(df, COMMONWEALTH_GAMES)
