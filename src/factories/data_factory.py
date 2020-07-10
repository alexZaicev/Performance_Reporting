from constants import CPM, SDM, SSG, UNKNOWN
from models.datas import CpmData, SdmData, SsgData, UnknownData
from models.errors import RGError


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
