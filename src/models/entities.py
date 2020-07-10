from abc import ABC

from constants import CPM, SDM, SSG, UNKNOWN


class RGEntityBase(ABC):

    def __init__(self, m_type=None, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        self.m_type = m_type
        self.data_cfy = data_cfy
        self.data_lfy = data_lfy
        self.measure_cfy = measure_cfy
        self.measure_lfy = measure_lfy

    def data(self):
        return self.data_lfy + self.data_cfy

    def get_measure(self, data):
        if data is not None:
            if data.m_type == self.measure_cfy.m_type and data.f_year == self.measure_cfy.f_year and \
                    data.m_id == self.measure_cfy.m_id and data.m_ref_no == self.measure_cfy.m_ref_no:
                return self.measure_cfy
            else:
                return self.measure_lfy
        return None


class CpmEntity(RGEntityBase):

    def __init__(self, m_type=CPM, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class SdmEntity(RGEntityBase):

    def __init__(self, m_type=SDM, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class SsgEntity(RGEntityBase):

    def __init__(self, m_type=SSG, data_cfy=None, data_lfy=None, measure_cfy=None, measure_lfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_cfy=data_cfy, data_lfy=data_lfy, measure_cfy=measure_cfy,
                              measure_lfy=measure_lfy)


class UnknownEntity(RGEntityBase):

    def __init__(self, m_type=UNKNOWN, data_lfy=None, data_cfy=None):
        RGEntityBase.__init__(self, m_type=m_type, data_lfy=data_lfy, data_cfy=data_cfy)