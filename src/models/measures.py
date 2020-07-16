from constants import *
from models.model_base import RGModelBase
from utils import get_val


class RGMeasureBase(RGModelBase):
    """
    RG measure base class
    """

    def __init__(self, m_type=None, df=None):
        RGModelBase.__init__(self, m_type=m_type, df=df)
        self.m_desc = get_val(df, MEASURE_DESCRIPTION)
        self.frequency = get_val(df, FREQUENCY_MONTHLY_QUARTERLY_1_2_YEARLY_ANNUAL, is_str=True)
        self.outcome = get_val(df, OUTCOME, is_str=True)
        self.outcome_no = get_val(df, OUTCOME_NO, is_int=True)
        self.outcome_priority_no = get_val(df, OUTCOME_PRIORITY_NO, is_int=True)
        self.priority = get_val(df, PRIORITY)
        self.additional_kpi_information = get_val(df, ADDITIONAL_KPI_INFO)
        self.new_existing = get_val(df, NEW_EXISTING)
        self.pref_dot = get_val(df, PREFERRED_DOT)
        self.aim = get_val(df, AIM)
        self.data_format = get_val(df, DATA_FORMAT, is_str=True)
        self.data_presented = get_val(df, DATA_PRESENTED)
        self.baseline = get_val(df, BASELINE, is_float=True)
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


class CpmMeasure(RGMeasureBase):

    def __init__(self, m_type=CPM, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)


class SdmMeasure(RGMeasureBase):

    def __init__(self, m_type=SDM, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)


class SsgMeasure(RGMeasureBase):

    def __init__(self, m_type=SSG, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)
