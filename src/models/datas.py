from constants import *
from models.model_base import RGModelBase
from utils import get_val


class RGDataModel(RGModelBase):
    """
    RG data base class
    """

    def __init__(self, m_type=None, df=None):
        RGModelBase.__init__(self, m_type=m_type, df=df)
        self.frequency = get_val(df, FREQUENCY, is_str=True)
        self.quarter = get_val(df, QUARTER)
        self.result = get_val(df, RESULT)
        self.target = get_val(df, TARGET)
        self.performance = get_val(df, PERFORMANCE)
        self.variance_from_target = get_val(df, VARIANCE_FROM_TARGET)
        self.dot_from_previous_month = get_val(df, DOT_FROM_PREVIOUS_MONTH, is_str=True)
        self.dot_from_previous_quarter = get_val(df, DOT_FROM_PREVIOUS_QUARTER, is_str=True)
        self.dot_from_same_period_last_year = get_val(df, DOT_FROM_SAME_PERIOD_LAST_YEAR, is_str=True)
        self.status = get_val(df, STATUS_PROVISIONAL_CONFIRMED, is_str=True)
        self.d_comments = get_val(df, DIRECTORATE_COMMENTARY, is_str=True)
        self.r_comments = get_val(df, REPORT_COMMENTARY, is_str=True)
        self.bck_nationally = get_val(df, BENCHMARKABLE_NATIONALLY, is_str=True)
        self.bck_result = get_val(df, BENCHMARK_RESULT, is_float=True)
        self.bck_group = get_val(df, BENCHMARK_GROUP_FOR_REPORTING_PURPOSES, is_str=True)
        self.brum_result_at_bck = get_val(df, BIRMINGHAM_RESULT_AT_TIME_OF_BENCHMARK, is_float=True)
        self.brum_quartile_pos = get_val(df, BIRMINGHAM_QUARTILE_POSITION, is_str=True)
        self.year_of_bck_data = get_val(df, YEAR_OF_BENCHMARK_DATA, is_str=True)
        self.reason_of_no_national_bck = get_val(df, REASON_FOR_NON_NATIONAL_BENCHMARK_IF_RELEVANT, is_str=True)
        self.quartile_projection = get_val(df, QUARTILE_PROJECTION)
        self.assistant_director_sign_off = get_val(df, ASSISTANT_DIRECTOR_SIGN_OFF)
        self.dmt_sign_off_date = get_val(df, DMT_SIGN_OFF_DATE)
        self.cabinet_mem_sign_off_date = get_val(df, CABINET_MEMBERS_SIGN_OFF_DATE)
        self.year = get_val(df, YEAR)
        self.year_month = get_val(df, YEAR_MONTH)
        self.year_quarter = get_val(df, YEAR_QUARTER)


class HrDataModel(RGModelBase):

    def __init__(self, m_type=None, df=None):
        RGModelBase.__init__(self, m_type=m_type, df=df)
        self.data_format = get_val(df, DATA_FORMAT)
        self.year = get_val(df, YEAR)
        self.year_month = get_val(df, YEAR_MONTH)


class CpmData(RGDataModel):

    def __init__(self, m_type=CPM, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class SdmData(RGDataModel):

    def __init__(self, m_type=SDM, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class SsgData(RGDataModel):

    def __init__(self, m_type=SSG, df=None):
        RGDataModel.__init__(self, m_type=m_type, df=df)


class PmtAdditionalData(RGModelBase):

    def __init__(self, m_type=PMT_ADDITIONAL, df=None):
        RGModelBase.__init__(self, m_type=m_type, df=df)
        self.frequency = get_val(df, FREQUENCY, is_str=True)
        self.quarter = get_val(df, QUARTER, is_str=True)
        self.measure_text_column_1 = get_val(df, MEASURE_TEXT_COLUMN_1, is_str=True)
        self.measure_text_column_2 = get_val(df, MEASURE_TEXT_COLUMN_2, is_str=True)
        self.dmt_sign_off_date = get_val(df, DMT_SIGN_OFF_DATE, is_date=True)
        self.cabinet_members_sign_off_date = get_val(df, CABINET_MEMBERS_SIGN_OFF_DATE, is_date=True)


class HrScorecardData(HrDataModel):

    def __init__(self, m_type=HR_SCORECARD, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.adult_social_care = get_val(df, ADULTS_SOCIAL_CARE, is_int=True)
        self.education_and_skills = get_val(df, EDUCATION_AND_SKILLS, is_int=True)
        self.inclusive_growth = get_val(df, INCLUSIVE_GROWTH, is_int=True)
        self.finance_and_governance = get_val(df, FINANCE_AND_GOVERNANCE, is_int=True)
        self.neighbourhoods = get_val(df, NEIGHBOURHOODS, is_int=True)
        self.pip = get_val(df, PARTNERSHIPS_INSIGHT_AND_PREVENTION, is_int=True)
        self.digital_and_customer_services = get_val(df, DIGITAL_AND_CUSTOMER_SERVICES, is_int=True)
        self.hr_and_od = get_val(df, HR_AND_ORGANISATION_DEVELOPMENT, is_int=True)
        self.bcc = get_val(df, BIRMINGHAM_CITY_COUNCIL, is_int=True)


class HrAbsencesData(HrDataModel):

    def __init__(self, m_type=HR_ABSENCES, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.adult_social_care = get_val(df, ADULTS_SOCIAL_CARE, is_float=True)
        self.education_and_skills = get_val(df, EDUCATION_AND_SKILLS, is_float=True)
        self.inclusive_growth = get_val(df, INCLUSIVE_GROWTH, is_float=True)
        self.finance_and_governance = get_val(df, FINANCE_AND_GOVERNANCE, is_float=True)
        self.neighbourhoods = get_val(df, NEIGHBOURHOODS, is_float=True)
        self.pip = get_val(df, PARTNERSHIPS_INSIGHT_AND_PREVENTION, is_float=True)
        self.digital_and_customer_services = get_val(df, DIGITAL_AND_CUSTOMER_SERVICES, is_float=True)
        self.hr_and_od = get_val(df, HR_AND_ORGANISATION_DEVELOPMENT, is_float=True)
        self.bcc = get_val(df, BIRMINGHAM_CITY_COUNCIL, is_float=True)
        self.cwg = get_val(df, COMMONWEALTH_GAMES, is_float=True)


class HrSicknessData(HrDataModel):

    def __init__(self, m_type=HR_SICKNESS, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.total = get_val(df, TOTAL, is_int=True)
        self.percentage = get_val(df, PERCENTAGE, is_float=True)


class HrTrainingData(HrDataModel):

    def __init__(self, m_type=HR_TRAINING, df=None):
        HrDataModel.__init__(self, m_type=m_type, df=df)
        self.adult_social_care = get_val(df, ADULTS_SOCIAL_CARE, is_float=True)
        self.education_and_skills = get_val(df, EDUCATION_AND_SKILLS, is_float=True)
        self.inclusive_growth = get_val(df, INCLUSIVE_GROWTH, is_float=True)
        self.finance_and_governance = get_val(df, FINANCE_AND_GOVERNANCE, is_float=True)
        self.neighbourhoods = get_val(df, NEIGHBOURHOODS, is_float=True)
        self.pip = get_val(df, PARTNERSHIPS_INSIGHT_AND_PREVENTION, is_float=True)
        self.digital_and_customer_services = get_val(df, DIGITAL_AND_CUSTOMER_SERVICES, is_float=True)
        self.hr_and_od = get_val(df, HR_AND_ORGANISATION_DEVELOPMENT, is_float=True)
        self.bcc = get_val(df, BIRMINGHAM_CITY_COUNCIL, is_float=True)
        self.date = get_val(df, DATE_OF_DATA, is_date=True)
        self.cwg = get_val(df, COMMONWEALTH_GAMES, is_float=True)
