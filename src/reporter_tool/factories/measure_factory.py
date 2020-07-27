from common.constants import CPM, SDM, SSG
from common.models.errors import RGError
from common.utility_base import RGUtilityBase
from common.models.measures import CpmMeasure, SdmMeasure, SsgMeasure


class RGMeasureFactory(RGUtilityBase):
    """
    RG measure factory
    """

    @staticmethod
    def create_measure(m_type=None, df=None):
        """
        Create measure by measure type

        :param m_type: Measure type
        :param df: Year Measure
        :return:
        """
        __TYPE_CREATION_MAP = {
            CPM: RGMeasureFactory.__create_cpm_measure,
            SDM: RGMeasureFactory.__create_sdm_measure,
            SSG: RGMeasureFactory.__create_ssg_measure
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
