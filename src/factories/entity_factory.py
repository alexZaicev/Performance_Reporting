from constants import SSG, UNKNOWN, CPM, SDM
from models.entities import CpmEntity, SdmEntity, SsgEntity, UnknownEntity
from models.errors import RGError


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
