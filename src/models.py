from abc import ABC, abstractmethod
from constants import *


class RGError(Exception):
    """
    RG custom error
    """
    pass


class RGMeasureBase(ABC):
    """
    RG measure base class
    """

    def __init__(self, m_type=None, df=None):
        if m_type is None or df is None:
            raise RGError('Invalid measure type [{}] or data frame [{}] provided'.format(m_type, df))
        self.load_df(df=df)

    @abstractmethod
    def load_df(self, df):
        raise RGError('Unimplemented method RGMeasureBase.load_df')


class RGReporterBase(ABC):
    """
    RG reporter base class
    """

    @abstractmethod
    def generate(self):
        raise RGError('Unimplemented method RGBase.generate')


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
        :param df: Template data frame
        :return:
        """
        __MEASURE_TYPE_CREATION_MAP = {
            'CPM': RGMeasureFactory.__create_cpm_measure,
            'SDM': RGMeasureFactory.__create_sdm_measure,
            'SSG': RGMeasureFactory.__create_ssg_measure
        }
        try:
            fun = __MEASURE_TYPE_CREATION_MAP[m_type]
            fun(df)
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


class CpmMeasure(RGMeasureBase):

    def __init__(self, m_type=CPM, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)

    def load_df(self, df=None):
        pass


class SdmMeasure(RGMeasureBase):

    def __init__(self, m_type=SDM, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)

    def load_df(self, df):
        pass


class SsgMeasure(RGMeasureBase):

    def __init__(self, m_type=SSG, df=None):
        RGMeasureBase.__init__(self, m_type=m_type, df=df)

    def load_df(self, df):
        pass
