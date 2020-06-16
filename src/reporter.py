from models import *


class PDFReporter(RGReporterBase):

    def __init__(self):
        RGReporterBase.__init__(self)

    def generate(self, entities=None):
        if entities is None or len(entities) < 1:
            raise RGError('No measures provided to PDF report generator')


