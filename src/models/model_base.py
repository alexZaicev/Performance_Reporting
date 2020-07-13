from abc import ABC

from models.errors import RGError
from utils import get_val
from constants import FISCAL_YEAR, MEASURE_ID, MEASURE_REF_NO, MEASURE_TITLE, MEASURE, MONTH


class RGModelBase(ABC):

    def __init__(self, m_type=None, df=None):
        if m_type is None or df is None:
            raise RGError('Invalid measure type [{}] or data frame [{}] provided'.format(m_type, df))
        self.m_type = m_type
        self.f_year = get_val(df, FISCAL_YEAR)
        self.m_id = get_val(df, MEASURE_ID)
        self.m_ref_no = get_val(df, MEASURE_REF_NO)
        self.m_title = get_val(df, MEASURE_TITLE)
        self.month = get_val(df, MONTH)
        if self.m_title is None:
            self.m_title = get_val(df, MEASURE)
