from common.utility_base import RGUtilityBase
from common.models.datas import *
from common.models.errors import RGError


class RGDataFactory(RGUtilityBase):
    """
    RG data factory
    """

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
            PMT_ADDITIONAL: RGDataFactory.__create_pmt_additional_data,
            HR_SCORECARD: RGDataFactory.__create_hr_scorecard_data,
            HR_ABSENCES: RGDataFactory.__create_hr_absences_data,
            HR_SICKNESS: RGDataFactory.__create_hr_sickness_data,
            HR_TRAINING: RGDataFactory.__create_hr_training_data,
            DCS_COMPLAINTS: RGDataFactory.__create_dcs_complaints_data
        }
        try:
            fun = __TYPE_CREATION_MAP[m_type]
            return fun(df=df)
        except AttributeError:
            raise RGError("Unknown data type {}".format(m_type))

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
    def __create_pmt_additional_data(df=None):
        return PmtAdditionalData(df=df)

    @staticmethod
    def __create_hr_scorecard_data(df=None):
        return HrScorecardData(df=df)

    @staticmethod
    def __create_hr_absences_data(df=None):
        return HrAbsencesData(df=df)

    @staticmethod
    def __create_hr_sickness_data(df=None):
        return HrSicknessData(df=df)

    @staticmethod
    def __create_hr_training_data(df=None):
        return HrTrainingData(df=df)

    @staticmethod
    def __create_dcs_complaints_data(df=None):
        return DcsComplaintsData(df=df)
