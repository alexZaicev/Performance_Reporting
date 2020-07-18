from common.models.utilities import RGConfig
from common.utility_base import RGUtilityBase


class RGConfigReader(RGUtilityBase):

    @staticmethod
    def read_config():
        return RGConfig()
