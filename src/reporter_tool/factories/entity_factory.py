from common.models.errors import RGError
from common.utility_base import RGUtilityBase
from common.models.entities import *


class RGEntityFactory(RGUtilityBase):
    """
    RG entity factory
    """

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
            PMT_ADDITIONAL: RGEntityFactory.__create_pmt_additional_entity,
            HR_SCORECARD: RGEntityFactory.__create_hr_scorecard_entity,
            HR_ABSENCES: RGEntityFactory.__create_hr_absences_entity,
            HR_SICKNESS: RGEntityFactory.__create_hr_sickness_entity,
            HR_TRAINING: RGEntityFactory.__create_hr_training_entity,
            DCS_COMPLAINTS: RGEntityFactory.__create_dcs_complaints_entity
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
    def __create_pmt_additional_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return PmtAdditionalEntity(data_lfy=data_lfy, data_cfy=data_cfy)

    @staticmethod
    def __create_hr_scorecard_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return HrScorecardEntity(data_lfy=data_lfy, data_cfy=data_cfy)

    @staticmethod
    def __create_hr_absences_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return HrAbsencesEntity(data_lfy=data_lfy, data_cfy=data_cfy)

    @staticmethod
    def __create_hr_sickness_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return HrSicknessEntity(data_lfy=data_lfy, data_cfy=data_cfy)

    @staticmethod
    def __create_hr_training_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return HrTrainingEntity(data_lfy=data_lfy, data_cfy=data_cfy)

    @staticmethod
    def __create_dcs_complaints_entity(data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        return DcsComplaintsEntity(data_lfy=data_lfy, data_cfy=data_cfy)
