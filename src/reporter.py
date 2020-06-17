import logging
import os

from fpdf import FPDF
from models import RGReporterBase


class PDFReporter(RGReporterBase):

    def __init__(self):
        RGReporterBase.__init__(self)
        # starting coordinates for each page
        self.left_top = (10, 30)
        # size of a small chart
        self.graph_size = (135, 118)
        # grid mapping for small charts
        self.grid_size = (2, 3)

    def do_init(self):
        self.report = FPDF('L', 'mm', (297, 420))
        self.report.set_doc_option("core_fonts_encoding", "windows-1252")
        self.report.set_auto_page_break(auto=False)

    def do_compose(self, entities=None, exclusions=None):
        graphs = 0
        coords = list(self.left_top)
        for entity in entities:
            # check if entity should be excluded from the report
            if exclusions is not None and entity.measure_cfy.m_id in exclusions:
                logging.debug('Ignoring entity [{}]'.format(entity.measure_cfy.m_id))
                continue
            graphs += 1
            # check if coords are equal to initial left-top
            # then create new page
            if coords[0] == self.left_top[0] and coords[1] == self.left_top[1]:
                self.report.add_page()

            # check if number of graphs on grid row has exceeded the allowed amount
            if graphs % self.grid_size[1] == 0:
                coords = (self.left_top[0], self.left_top[1] + self.graph_size[1])
            else:
                coords = (self.left_top[0] + self.graph_size[0], self.left_top[1])
            # check if number of graphs on page has exceeded the allowed amount
            # then create setup properties for new page to be added
            if graphs % (self.grid_size[0] * self.grid_size[1]) == 0:
                self.__create_grid()
                coords = list(self.left_top)

        self.__create_grid()

    def do_export(self, out_dir=None):
        self.report.output(name=os.path.join(out_dir, '{}.pdf'.format(self.report_name)), dest='F')

    def __create_grid(self):
        self.report.set_xy(10, 30)
        self.report.set_font('Arial', 'B', 8)
        self.report.cell(135, 118, '', 1, 0, '')
        self.report.cell(135, 118, '', 1, 0, '')
        self.report.cell(135, 118, '', 1, 2, '')
        self.report.cell(-270)
        self.report.cell(135, 118, '', 1, 0, '')
        self.report.cell(135, 118, '', 1, 0, '')
        self.report.cell(135, 118, '', 1, 2, '')
