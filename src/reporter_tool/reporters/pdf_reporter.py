import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import plotly.io.orca as orca
from fpdf import FPDF
from matplotlib import font_manager
from plotly import graph_objects

from common.models.entities import CpmEntity, SdmEntity
from common.utils import *
from reporter_tool.reporters.reporter_base import RGReporterBase


class PDFReporter(RGReporterBase):

    def __init__(self, options=None):
        RGReporterBase.__init__(self, options=options)
        # starting coordinates for each page
        self.left_top = (10, 30)
        # size of a small chart
        self.graph_size = (135, 118)
        # grid mapping for small charts
        self.grid_size = (2, 3)
        # set plotly.io.orca.config.executable
        if self.options.orca_path is not None:
            orca.config.executable = self.options.orca_path

    def do_init(self):
        super().do_init()
        self.report = FPDF('L', 'mm', (297, 420))
        self.report.add_font(DEJAVU_SANS, '', get_font(DEJAVU_SANS), uni=True)
        self.report.add_font(DEJAVU_SANS, 'B', get_font(DEJAVU_SANS_BOLD), uni=True)
        self.report.add_font(DEJAVU_SANS_MONO, '', get_font(DEJAVU_SANS_MONO), uni=True)
        self.report.add_font(DEJAVU_SANS_MONO, 'B', get_font(DEJAVU_SANS_MONO_BOLD), uni=True)
        self.report.add_font(DEJAVU_SERIF, '', get_font(DEJAVU_SERIF), uni=True)
        self.report.add_font(DEJAVU_SERIF, 'B', get_font(DEJAVU_SERIF_BOLD), uni=True)
        self.report.add_font(DEJAVU_SERIF_CONDENSED, '', get_font(DEJAVU_SERIF_CONDENSED), uni=True)
        self.report.add_font(DEJAVU_SERIF_CONDENSED, 'B', get_font(DEJAVU_SERIF_CONDENSED_BOLD), uni=True)
        self.report.add_font(LUCIDA_SANS, '', get_font(LUCIDA_SANS), uni=True)
        self.report.add_font(LUCIDA_SANS, 'B', get_font(LUCIDA_SANS), uni=True)

        self.report.set_doc_option("core_fonts_encoding", REPORT_ENCODING)

        self.report.set_auto_page_break(auto=False)

    def do_export(self, out_dir=None):
        f_year = try_parse(str(self.options.fym)[:4], is_int=True)
        f_month = try_parse(str(self.options.fym)[-2:], is_int=True)
        self.report_name = '{}_{}_{}_{}.{}'.format(get_cfy_prefix(cfy=f_year), get_month_name_from_id(f_month),
                                                   self.report_name, timestamp(), EXT_PDF)
        self.report.output(name=os.path.join(out_dir, self.report_name), dest='F')

    def do_compose(self, options=None):
        self.__do_compose_cpm_scorecard(options)
        self.__do_compose_grid_charts(options)
        self.__do_compose_sdm_scorecard(options)
        self.__do_compose_financial_hr_scorecard(options)
        self.__do_compose_relationship_effectiveness_scorecard(options)

    @staticmethod
    def __get_font_props(family=REPORT_FONT, bold=True, size=4):
        if bold:
            weight = 700
        else:
            weight = mpl.rcParams['font.weight']
        return font_manager.FontProperties(fname=get_font(family), size=size, weight=weight)

    def __add_image(self, options, f_type, fym=None, x=None, y=None, w=0.0, h=0.0):
        if fym is None:
            fym = options.fym
        f_image = options.images.find(f_type=f_type, fym=fym)
        if f_image is not None:
            self.report.image(f_image.path, x=x, y=y, w=w, h=h)
        else:
            logging.error(
                'Could not find image of type [{}] that would satisfy provided fiscal data [{}]'.format(f_type,
                                                                                                        options.fym))

    def __do_compose_relationship_effectiveness_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True, h=2.25, w=405,
                                        month_id=try_parse(str(options.fym)[-2:], is_int=True))
        self.report.cell(220, h=8.5, txt=text.CUSTOMER_RELATIONSHIPS, fill=1, align='C', border=1)
        self.report.cell(185, h=8.5, txt=text.SCHOOLS_IN_DEFICIT_REPORTED_QUARTERLY, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        h1 = self.__do_compose_effectiveness_and_compliance(7.5 + 220, h, options)
        h = self.__do_compose_customer_relationships(h, options)

        h1 = self.__create_scorecard_top(add_first=False, h=h1)
        self.report.set_xy(220 + 7.5, h1)
        self.report.cell(185, h=8.5, txt=text.DECISION_PLANNING_CABINET, fill=1, align='C', border=1)
        h1 += 8.5
        self.__reset_colors()
        self.__do_compose_decision_planning_cabinet(220 + 7.5, h1, options)

        h = self.__create_scorecard_top(add_first=False, h=h)
        self.report.cell(220, h=8.5, txt=text.CORPORATE_RISKS, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        self.__do_compose_corporate_risks(h, options)

    def __do_compose_decision_planning_cabinet(self, x, h, options):
        graph_size = (185, 42)
        self.__set_font(size=6)
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        data = get_data_by_m_id_and_date(options.entities, 'PMT_03', options.fym)
        column_1, column_2 = data.measure_text_column_1, data.measure_text_column_2

        self.report.set_xy(x + 1, h + 1)
        self.report.multi_cell(graph_size[0] / 2 - 2, h=2.5, txt=column_1, align='J')

        self.report.set_xy(x + graph_size[0] / 2, h)
        self.report.cell(graph_size[0] / 2, h=graph_size[1], border='L')

        self.report.set_xy(x + 1 + graph_size[0] / 2 + 4, h + 1)
        self.report.multi_cell(graph_size[0] / 2 - 2, h=2.5, txt=column_2, align='J')

    def __do_compose_effectiveness_and_compliance(self, x, h_orig, options):
        graph_size = (185, 224)
        h = h_orig
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.__add_image(options, OFSTED, x=x + 0.5, y=h + 0.5, w=graph_size[0] - 1)

        h = self.__do_compose_request_table(x, h + 111, graph_size[0] - 0.25, options)
        h = self.__do_compose_governance_table(x, h, graph_size[0] - 0.25, options)
        h = self.__do_compose_final_audit_report_table(x, h, graph_size[0] - 0.25, options)
        self.__do_compose_data_breaches_tables(x, h, graph_size[0] - 0.25, options)

        return h_orig + graph_size[1]

    def __do_compose_data_breaches_tables(self, x, h, w, options):
        h_line = 5

        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x, h=h)
        self.report.cell(w * 0.3, h=h_line, txt=text.DATA_BREACHES_INCIDENTS_AND_CONCERNS, fill=1)
        self.report.cell(w * 0.35, h=h_line, txt=text.BREACH, align='C', fill=1)
        self.report.cell(w * 0.35, h=h_line, txt=text.INVESTIGATION_ONGOING, align='C', fill=1)

        h += h_line + 2
        self.__do_compose_data_breaches_table_name(x, h, w * 0.3)
        self.__do_compose_breach_table(x + w * 0.3, h, w * 0.35, options)
        self.__do_compose_investigation_table(x + w * 0.65, h, w * 0.35, options)

    def __do_compose_breach_table(self, x, h, w, options):
        self.report.set_xy(x, h)
        h_line = 3
        self.__set_font(size=5, is_bold=True)
        d_prev, d_current = get_prev_and_current_month_data(options, '9_14')
        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C', border='R')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_15')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_20')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_18')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_19')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_21')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        # TODO PIP data is missing
        # d_prev, d_current = get_prev_and_current_month_data(options, '9_19')
        h = self.__create_breach_table_row(x, h, w, h_line, 0, 0, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_17')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_16')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, border='R')

        # TODO education & skills is missing
        # d_prev, d_current = get_prev_and_current_month_data(options, '9_22')
        h = self.__create_breach_table_row(x, h, w, h_line, 0, 0, border='R')

        d_prev, d_current = get_prev_and_current_month_data(options, '9_13')
        self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, is_total=True, border='R')

    def __create_breach_table_row(self, x, h, w, h_line, p_value, c_value, is_total=False, border=''):
        h = self.__set_table_row_xy(x, h, h_line)
        self.__set_font(size=5, is_bold=is_total)

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value)
        variance, dot = get_variance_and_dot(p_value, c_value)

        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(p_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(c_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(variance), align='C', border=border)
        return h

    def __do_compose_investigation_table(self, x, h, w, options):
        self.report.set_xy(x, h)
        h_line = 3
        self.__set_font(size=5, is_bold=True)
        d_prev, d_current = get_prev_and_current_month_data(options, '9_23')
        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_24')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_30')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_28')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_29')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        # TODO PIP data is missing
        # d_prev, d_current = get_prev_and_current_month_data(options, '9_29')
        h = self.__create_breach_table_row(x, h, w, h_line, 0, 0)

        # TODO PIP data is missing
        # d_prev, d_current = get_prev_and_current_month_data(options, '9_19')
        h = self.__create_breach_table_row(x, h, w, h_line, 0, 0)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_26')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_25')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_27')
        h = self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_22')
        self.__create_breach_table_row(x, h, w, h_line, d_prev.result, d_current.result, is_total=True)

    def __do_compose_data_breaches_table_name(self, x, h, w):
        self.report.set_xy(x, h)
        h_line = 3
        self.__set_font(size=5)
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.ADULT_SOCIAL_CARE, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.CHILDRENS_TRUST, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.INCLUSIVE_GROWTH, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.FINANCE_AND_GOVERNANCE, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.HUMAN_RESOURCES, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.NEIGHBOURHOODS, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.PARTNERSHIP_INSIGHT_AND_PREVENTION, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.DIGITAL_AND_CUSTOMER_SERVICES, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.COMMONWEALTH_GAMES, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.EDUCATION_AND_SKILLS, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.__set_font(size=5, is_bold=True)
        self.report.cell(w, h=h_line, txt='    {}'.format(text.TOTAL_INCIDENTS_AND_CONCERNS), align='L')

    def __do_compose_final_audit_report_table(self, x, h, w, options):
        h_line = 5

        d_prev, d_current = get_prev_and_current_month_data(options, '10_04')

        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x, h=h)
        self.report.cell(w * 0.15, h=h_line, fill=1)
        self.report.cell(w * 0.2, h=h_line, txt=d_prev.month[-3:].title(), align='C', fill=1)
        self.report.cell(w * 0.2, h=h_line, txt=d_current.month[-3:].title(), align='C', fill=1)
        self.report.cell(w * 0.45, h=h_line, txt=text.COMMENTARY, align='L', fill=1)
        h += h_line
        h_line = 15

        self.__set_font(size=5)
        self.report.set_xy(x, h + (h_line / 2 - 2.5))
        self.report.multi_cell(w * 0.15, h=2.5, txt=text.NUMBER_OF_FINAL_AUDIT_REPORTS_ISSUES_PER_MONTH, align='L')
        self.report.set_xy(x + w * 0.2, h + 0.5)
        self.__add_image(options, f_type=FINAL_AUDIT_REPORT, fym=d_prev.year_month, w=w * 0.1, h=h_line - 1)
        self.report.set_xy(x + w * 0.4, h + 0.5)
        self.__add_image(options, f_type=FINAL_AUDIT_REPORT, fym=d_current.year_month, w=w * 0.1, h=h_line - 1)

        self.report.set_xy(x + w * 0.55, h)
        self.report.multi_cell(w * 0.35, h=2.5,
                               txt='{}'.format(parse_comment(d_current.r_comments, size=380, remove_line_feeds=True)),
                               align='L')
        h += h_line

        return h

    def __do_compose_governance_table(self, x, h, w, options):
        d_prev, d_current = get_prev_and_current_month_data(options, '10_01')

        h = self.__create_request_governance_table_header(x, h, w, 5, text.GOVERNANCE,
                                                          d_prev.month[-3:].title(), d_current.month[-3:].title())
        h_line = 4
        self.__create_request_table_row(x, h, w, h_line, text.OMBUDSMAN_COMPLAINTS_RESULTING_IN_REPORTS_ISSUED,
                                        d_prev.result, d_current.result,
                                        d_current.target, d_current.r_comments, multi_line_title=True)
        self.__add_empty_line(h=h_line)
        h += h_line * 2
        d_prev, d_current = get_prev_and_current_month_data(options, '10_02')
        self.__create_request_table_row(x, h, w, h_line, text.JUDICIAL_REVIEW_CHALLENGES_SUCCESSFULLY_DEFENCED,
                                        d_prev.result, d_current.result,
                                        d_current.target, d_current.r_comments, multi_line_title=True)
        self.__add_empty_line(h=h_line)
        h += h_line * 2
        d_prev, d_current = get_prev_and_current_month_data(options, '10_03')
        self.__create_request_table_row(x, h, w, h_line,
                                        text.WHISTLEBLOWING_REQUESTS_RECEIVED_THAT_PROGRESS_UNDER_THE_BOUNDARIES_OF_THE_POLICY,
                                        d_prev.result, d_current.result,
                                        d_current.target, d_current.r_comments, multi_line_title=True)
        self.__add_empty_line(h=h_line)
        h += h_line * 2
        return h

    def __do_compose_request_table(self, x, h, w, options):
        d_prev, d_current = get_prev_and_current_month_data(options, '9_11')

        h = self.__create_request_governance_table_header(x, h, w, 5, text.REQUESTS_IN_TIMESCALE,
                                                          d_prev.month[-3:].title(), d_current.month[-3:].title())

        h_line = 4
        self.__create_request_table_row(x, h, w, h_line, text.FREEDOM_OF_INFORMATION, d_prev.result, d_current.result,
                                        d_current.target, d_current.r_comments)

        d_prev, d_current = get_prev_and_current_month_data(options, '9_12')
        h += h_line
        self.__create_request_table_row(x, h, w, h_line, text.SUBJECT_ACCESS_REQUESTS, d_prev.result, d_current.result,
                                        d_current.target, d_current.r_comments)
        h += h_line
        return h

    def __create_request_governance_table_header(self, x, h, w, h_line, title, p_month, c_month):
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x, h=h)
        self.report.cell(w * 0.15, h=h_line, txt=title, align='L', fill=1)
        self.report.cell(w * 0.1, h=h_line, txt=p_month, align='C', fill=1)
        self.report.cell(w * 0.1, h=h_line, txt=c_month, align='C', fill=1)
        self.report.cell(w * 0.1, h=h_line, txt=text.DOT, align='C', fill=1)
        self.report.cell(w * 0.1, h=h_line, txt=text.VARIANCE, align='C', fill=1)
        self.report.cell(w * 0.1, h=h_line, txt=text.TARGET, align='C', fill=1)
        self.report.cell(w * 0.35, h=h_line, txt=text.COMMENTARY, align='L', fill=1)

        return h + h_line

    def __create_request_table_row(self, x, h, w, h_line, title, p_value, c_value, target, comment,
                                   multi_line_title=False):
        self.report.set_xy(x, h)
        self.__set_font(size=5)

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value, is_percentage=True)
        tmp, target = self.__adjust_prev_current_values(0.0, target, is_percentage=True)
        variance, dot = get_variance_and_dot(p_value, c_value)

        if multi_line_title:
            self.report.multi_cell(w * 0.15, h=h_line / 2, txt=title, align='L')
        else:
            self.report.cell(w * 0.15, h=h_line, txt=title, align='L')
        self.report.cell(w * 0.1, h=h_line, txt='{:.2f}%'.format(p_value), align='C')
        self.report.cell(w * 0.1, h=h_line, txt='{:.2f}%'.format(c_value), align='C')
        self.report.cell(w * 0.1, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.1, h=h_line, txt='{:.2f}%'.format(variance), align='C')
        self.report.cell(w * 0.1, h=h_line, txt='{:.2f}%'.format(target), align='C')
        self.report.cell(w * 0.35, h=h_line,
                         txt='{}'.format(parse_comment(comment, size=70, remove_line_feeds=True)),
                         align='L')

    def __do_compose_corporate_risks(self, h, options):
        graph_size = (220, 183)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.__add_image(options, RISK_MAP, x=8, y=h + 0.5, w=graph_size[0] - 1, h=graph_size[1] - 1)
        return h + graph_size[1]

    def __do_compose_customer_relationships(self, h_orig, options):
        graph_size = (220, 83)
        h = h_orig
        x = 7.5
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)

        h = self.__do_compose_customer_rel_table(x + 0.5, h + 2, graph_size[0], options)
        h += 5
        self.__do_compose_complaints_table(x, h, graph_size[0], options)

        return h_orig + graph_size[1]

    def __do_compose_complaints_table(self, x, h_orig, w, options):
        h = h_orig
        self.report.set_xy(x, h)

        d_dcsc_1_prev, d_dcsc_1_current = get_prev_and_current_month_data(options, 'DCSC_01')
        d_dcsc_4_prev, d_dcsc_4_current = get_prev_and_current_month_data(options, 'DCSC_04')
        d_dcsc_7_prev, d_dcsc_7_current = get_prev_and_current_month_data(options, 'DCSC_07')

        w_table = w * 0.25

        self.__set_font(size=6, is_bold=True)
        self.__do_compose_complaints_name_table(x, h, w_table)
        self.__do_compose_volume_table(x + w_table, h, w_table, d_dcsc_1_prev, d_dcsc_1_current)
        self.__do_compose_no_responded_table(x + w_table * 2, h, w_table, d_dcsc_4_prev, d_dcsc_4_current)
        self.__do_compose_percent_responded_table(x + w_table * 3, h, w_table, d_dcsc_7_prev, d_dcsc_7_current)

    def __set_table_row_xy(self, x, y, h_line):
        y += h_line
        self.report.set_xy(x, y)
        return y

    def __do_compose_complaints_name_table(self, x, h, w):
        h_line = 8
        self.__set_font(size=6, is_bold=True)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x + 0.125, h=h)
        self.report.cell(w, h=h_line, txt=text.COMPLAINTS, align='C', fill=1)

        self.__set_font(size=6)
        h += h_line - 4
        h_line = 4
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.ADULT_SOCIAL_CARE, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.CHILDRENS_TRUST, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.EDUCATION_AND_SKILLS, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.INCLUSIVE_GROWTH, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.FINANCE_AND_GOVERNANCE, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.NEIGHBOURHOODS, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.DIGITAL_AND_CUSTOMER_SERVICES, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.HUMAN_RESOURCES, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.PARTNERSHIP_INSIGHT_AND_PREVENTION, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.COMMONWEALTH_GAMES, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.report.cell(w, h=h_line, txt=text.UNASSIGNED, align='L')
        h = self.__set_table_row_xy(x, h, h_line)
        self.__set_font(size=6, is_bold=True)
        self.report.cell(w, h=h_line, txt='    {}'.format(text.TOTAL_COMPLAINTS), align='L')

    def __do_compose_percent_responded_table(self, x, h, w, d_prev, d_current):
        h_line = 8
        self.__set_font(size=6, is_bold=True)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x, h=h)
        self.report.cell(w - 0.125, h=h_line, txt=text.PERCENT_RESPONDED_IN_15_WORKING_DAYS, align='C', fill=1)

        h += h_line
        h_line = 4

        self.report.set_xy(x, h)
        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C', border='R')

        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.adult_social_care,
                                                      d_current.adult_social_care)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.childrens_trust,
                                                      d_current.childrens_trust)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.education_and_skills,
                                                      d_current.education_and_skills)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.inclusive_growth,
                                                      d_current.inclusive_growth)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.finance_and_governance,
                                                      d_current.finance_and_governance)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.neighbourhoods,
                                                      d_current.neighbourhoods)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.digital_and_customer_services,
                                                      d_current.digital_and_customer_services)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.hr_and_od, d_current.hr_and_od)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.pip, d_current.pip)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.cwg, d_current.cwg)
        h = self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.unassigned, d_current.unassigned)
        self.__create_percent_responded_table_row(x, h, w, h_line, d_prev.bcc, d_current.bcc, is_total=True)

    def __create_percent_responded_table_row(self, x, h, w, h_line, p_value, c_value, is_total=False):
        h = self.__set_table_row_xy(x, h, h_line)
        self.__set_font(size=6, is_bold=is_total)

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value, is_percentage=True)
        variance, dot = get_variance_and_dot(p_value, c_value)

        self.report.cell(w * 0.25, h=h_line, txt='{:.2f}%'.format(p_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{:.2f}%'.format(c_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{:.2f}%'.format(variance), align='C', border='R')
        return h

    def __do_compose_no_responded_table(self, x, h, w, d_prev, d_current):
        h_line = 8
        self.__set_font(size=6, is_bold=True)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x, h=h)
        self.report.cell(w, h=h_line, txt=text.NO_RESPONDED_IN_15_WORKING_DAYS, align='C', fill=1)

        h += h_line
        h_line = 4

        self.report.set_xy(x, h)
        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C', border='R')

        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.adult_social_care,
                                                 d_current.adult_social_care)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.childrens_trust,
                                                 d_current.childrens_trust)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.education_and_skills,
                                                 d_current.education_and_skills)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.inclusive_growth,
                                                 d_current.inclusive_growth)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.finance_and_governance,
                                                 d_current.finance_and_governance)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.neighbourhoods, d_current.neighbourhoods)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.digital_and_customer_services,
                                                 d_current.digital_and_customer_services)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.hr_and_od, d_current.hr_and_od)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.pip, d_current.pip)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.cwg, d_current.cwg)
        h = self.__create_no_responded_table_row(x, h, w, h_line, d_prev.unassigned, d_current.unassigned)
        self.__create_no_responded_table_row(x, h, w, h_line, d_prev.bcc, d_current.bcc, is_total=True)

    def __create_no_responded_table_row(self, x, h, w, h_line, p_value, c_value, is_total=False):
        h = self.__set_table_row_xy(x, h, h_line)
        self.__set_font(size=6, is_bold=is_total)

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value)
        variance, dot = get_variance_and_dot(p_value, c_value)

        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(p_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(c_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(variance), align='C', border='R')
        return h

    def __do_compose_volume_table(self, x, h, w, d_prev, d_current):
        h_line = 8
        self.__set_font(size=6, is_bold=True)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, x=x, h=h)
        self.report.cell(w, h=h_line, txt=text.VOLUME, align='C', fill=1)

        h += h_line
        h_line = 4

        self.report.set_xy(x, h)
        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C', border='R')

        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.adult_social_care, d_current.adult_social_care)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.childrens_trust, d_current.childrens_trust)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.education_and_skills,
                                           d_current.education_and_skills)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.inclusive_growth, d_current.inclusive_growth)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.finance_and_governance,
                                           d_current.finance_and_governance)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.neighbourhoods, d_current.neighbourhoods)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.digital_and_customer_services,
                                           d_current.digital_and_customer_services)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.hr_and_od, d_current.hr_and_od)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.pip, d_current.pip)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.cwg, d_current.cwg)
        h = self.__create_volume_table_row(x, h, w, h_line, d_prev.unassigned, d_current.unassigned)
        self.__create_volume_table_row(x, h, w, h_line, d_prev.bcc, d_current.bcc, is_total=True)

    def __create_volume_table_row(self, x, h, w, h_line, p_value, c_value, is_total=False):
        h = self.__set_table_row_xy(x, h, h_line)
        self.__set_font(size=6, is_bold=is_total)

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value)
        variance, dot = get_variance_and_dot(p_value, c_value)

        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(p_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(c_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(variance), align='C', border='R')
        return h

    def __do_compose_customer_rel_table(self, x, h, w, options):
        h_line = 4
        self.__set_font(size=5, is_bold=True)
        self.report.set_xy(x, h)

        pym, cym = get_year_month_of_prev_and_current_quarters(options.fym)
        pq_data = get_data_by_m_id_and_date(options.entities, '9_05', pym)
        cq_data = get_data_by_m_id_and_date(options.entities, '9_05', cym)

        self.report.cell(w / 3, h=h_line)
        self.report.cell(w / 9, h=h_line, txt=pq_data.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=cq_data.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w / 9, h=h_line, txt=text.VARIANCE, align='C')

        h += h_line
        h_line = 3

        self.__create_customer_rel_table_row(x, h, w, h_line,
                                             text.CITIZENS_REGISTERING_SATISFACTION_WITH_THE_COUNCIL_QUARTERLY,
                                             pq_data.result, cq_data.result)
        h += h_line

        d_prev, d_current = get_prev_and_current_month_data(options, '9_07')

        self.report.set_xy(x, h)
        h_line = 4
        self.__set_font(size=5, is_bold=True)
        self.report.cell(w / 3, h=h_line)
        self.report.cell(w / 9, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w / 9, h=h_line, txt=text.VARIANCE, align='C')

        h += h_line
        h_line = 3
        self.__create_customer_rel_table_row(x, h, w, h_line,
                                             text.ONLINE_TRANSACTIONS_IN_COMPARISON_TO_TELEPHONE_CALLS, d_prev.result,
                                             d_current.result)
        return h

    def __create_customer_rel_table_row(self, x, h, w, h_line, title, p_value, c_value):
        self.report.set_xy(x, h)
        self.__set_font(size=5)
        self.report.cell(w / 3, h=h_line, txt=title, align='L')

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value, is_percentage=True)
        variance, dot = get_variance_and_dot(p_value, c_value)
        self.report.cell(w / 9, h=h_line, txt='{:.2f}%'.format(p_value), align='C')
        self.report.cell(w / 9, h=h_line, txt='{:.2f}%'.format(c_value), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w / 9, h=h_line, txt='{:.2f}%'.format(variance), align='C')

    def __do_compose_financial_hr_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True, h=2.25, w=405,
                                        month_id=try_parse(str(options.fym)[-2:], is_int=True))
        self.report.cell(330, h=8.5, txt=text.FINANCIAL_MANAGEMENT, fill=1, align='C', border=1)
        self.report.cell(75, h=8.5, txt=text.SCHOOLS_IN_DEFICIT_REPORTED_QUARTERLY, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        self.__do_compose_school_table(330 + 7.5, h, options)
        h = self.__do_compose_financial_charts(h, options)

        h = self.__create_scorecard_top(add_first=False, h=h)
        self.report.cell(405, h=8.5, txt=text.HUMAN_RESOURCES_WORKFORCE, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        h = self.__do_compose_hr_workforce(h, options)

        h = self.__create_scorecard_top(add_first=False, h=h)
        self.report.cell(220, h=8.5, txt=text.HEALTH_AND_SAFETY, fill=1, align='C', border=1)
        self.report.cell(185, h=8.5, txt=text.TRAINING_AND_DEVELOPMENT, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        self.__do_compose_training_table(7.5 + 220, h, options)
        h = self.__do_compose_health_and_safety(h, options)

        h = self.__create_scorecard_top(add_first=False, h=h)
        self.report.cell(220, h=8.5, txt=text.WORKFORCE_EXPENDITURE, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        h = self.__do_compose_workforce(h, options)

    def __do_compose_training_table(self, x, h, options):
        graph_size = (185, 91.5)
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        color = get_color(LIGHT_AQUA)
        self.report.set_fill_color(r=color.r, g=color.g, b=color.b)
        h_line = 8.5
        self.report.multi_cell(graph_size[0] / 11, h=h_line / 2, txt=text.E_LEARNING_COMPLIANCE, fill=1, border=1,
                               align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.THIS_IS_BHAM, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.DATA_PROTECT, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.CUSTOMER_SERVICE, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.EQUALITY, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.SAFE_GUARDING, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.H_AND_W_STRESS, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.PREVENT, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.FIRE_SAFETY, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.H_AND_S, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] / 11, h=h_line, txt=text.MODERN_SLAVERY, fill=1, border=1, align='C')

        hrt_data = [get_data_by_m_id_and_date(options.entities, 'HRT_{:02d}'.format(x), options.fym) for x in
                    range(1, 11, 1)]

        h += h_line
        h_line = 6

        self.__create_training_total_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_adult_social_care_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_cwg_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_digital_and_customer_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_education_and_skills_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_finance_and_governance_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_hr_and_od_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_inclusive_growth_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_neighbourhoods_table_row(x, h, graph_size[0], h_line, hrt_data)
        h += h_line
        self.__create_training_pip_table_row(x, h, graph_size[0], h_line, hrt_data)

    def __setup_training_table_row(self, x, h, w, h_line, title, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=4, is_bold=True)
        else:
            self.__set_font(size=4)
        self.report.cell(w / 11, h=h_line, txt=title, align='L', border=1)

    def __create_training_total_table_row(self, x, h, w, h_line, data):
        month = data[0].month[-3:]
        self.__setup_training_table_row(x, h, w, h_line, text.MONTH_TOTAL.format(month), is_total=True)
        for d in data:
            self.__create_training_table_row(w, h_line, d.bcc)

    def __create_training_adult_social_care_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.ADULT_SOCIAL_CARE)
        for d in data:
            self.__create_training_table_row(w, h_line, d.adult_social_care)

    def __create_training_cwg_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.CWG)
        for d in data:
            self.__create_training_table_row(w, h_line, d.cwg)

    def __create_training_digital_and_customer_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.DIGITAL_AND_CUSTOMER)
        for d in data:
            self.__create_training_table_row(w, h_line, d.digital_and_customer_services)

    def __create_training_education_and_skills_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.EDUCATION_AND_SKILLS)
        for d in data:
            self.__create_training_table_row(w, h_line, d.education_and_skills)

    def __create_training_finance_and_governance_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.FINANCE_AND_GOVERNANCE)
        for d in data:
            self.__create_training_table_row(w, h_line, d.finance_and_governance)

    def __create_training_hr_and_od_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.HR_AND_OD)
        for d in data:
            self.__create_training_table_row(w, h_line, d.hr_and_od)

    def __create_training_inclusive_growth_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.INCLUSIVE_GROWTH)
        for d in data:
            self.__create_training_table_row(w, h_line, d.inclusive_growth)

    def __create_training_neighbourhoods_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.NEIGHBOURHOODS)
        for d in data:
            self.__create_training_table_row(w, h_line, d.neighbourhoods)

    def __create_training_pip_table_row(self, x, h, w, h_line, data):
        self.__setup_training_table_row(x, h, w, h_line, text.PIP)
        for d in data:
            self.__create_training_table_row(w, h_line, d.pip)

    def __create_training_table_row(self, w, h, value):
        if value is None or (isinstance(value, str) and try_parse(value, is_float=True) is None):
            value = 0
        self.report.cell(w / 11, h, txt='{:.2f}%'.format(value), align='C', border=1)

    def __do_compose_health_and_safety(self, h_orig, options):
        graph_size = (220, 50)
        h = h_orig
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)

        h_sc = 4
        self.report.set_xy(7.5, h)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, h=h)
        self.report.cell(graph_size[0] * 0.6, h=h_sc, txt=text.ACCIDENTS_AND_INCIDENTS, fill=1, border=1, align='C')
        self.report.cell(graph_size[0] * 0.4, h=h_sc, txt=text.HSE_NOTIFIABLE, fill=1, border=1, align='C')
        h += h_sc
        self.__reset_colors()

        self.__do_compose_accident_and_incident_table(8, h + 2, graph_size[0] * 0.6, options, 'HRSC_01')
        self.__do_compose_hse_table(8 + graph_size[0] * 0.6, h + 2, graph_size[0] * 0.4, options, 'HRSC_02')

        return h_orig + graph_size[1]

    def __do_compose_hse_table(self, x, h, w, options, m_id):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4

        d_prev, d_current = get_prev_and_current_month_data(options, m_id)

        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C')
        h += h_line

        h_line = 3
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.adult_social_care, d_current.adult_social_care)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.education_and_skills, d_current.education_and_skills)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.inclusive_growth, d_current.inclusive_growth)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.finance_and_governance, d_current.finance_and_governance)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.hr_and_od,
                                   d_current.hr_and_od)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.neighbourhoods, d_current.neighbourhoods)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.pip,
                                   d_current.pip)
        h += h_line
        self.__creat_hse_table_row(x, h, w, h_line, d_prev.digital_and_customer_services,
                                   d_current.digital_and_customer_services)
        h += h_line * 2

        self.__creat_hse_table_row(x, h, w, h_line, d_prev.bcc, d_current.bcc, is_total=True)

    def __creat_hse_table_row(self, x, h, w, h_line, p_value, c_value, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=5, is_bold=True)
        else:
            self.__set_font(size=4)
        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value)
        variance, dot = get_variance_and_dot(p_value, c_value)
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(p_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(c_value), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(variance), align='C')

    def __do_compose_accident_and_incident_table(self, x, h, w, options, m_id):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4
        self.report.cell(w / 2 - 10, h=h_line)

        d_prev, d_current = get_prev_and_current_month_data(options, m_id)

        self.report.cell(w / 9, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w / 9, h=h_line, txt=text.VARIANCE, align='C')
        h += h_line

        h_line = 3
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.ADULT_SOCIAL_CARE,
                                                       d_prev.adult_social_care,
                                                       d_current.adult_social_care)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.EDUCATION_AND_SKILLS,
                                                       d_prev.education_and_skills, d_current.education_and_skills)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.INCLUSIVE_GROWTH, d_prev.inclusive_growth,
                                                       d_current.inclusive_growth)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.FINANCE_AND_GOVERNANCE,
                                                       d_prev.finance_and_governance, d_current.finance_and_governance)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.HR_AND_ORGANISATION_DEVELOPMENT,
                                                       d_prev.hr_and_od,
                                                       d_current.hr_and_od)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.NEIGHBOURHOODS, d_prev.neighbourhoods,
                                                       d_current.neighbourhoods)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.PARTNERSHIP_INSIGHT_AND_PREVENTION,
                                                       d_prev.pip,
                                                       d_current.pip)
        h += h_line
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line, text.DIGITAL_AND_CUSTOMER_SERVICES,
                                                       d_prev.digital_and_customer_services,
                                                       d_current.digital_and_customer_services)
        h += h_line * 2
        self.__creat_accidents_and_incidents_table_row(x, h, w, h_line,
                                                       text.TOTAL_ACCIDENTS_AND_INCIDENTS, d_prev.bcc, d_current.bcc,
                                                       is_total=True)

    def __creat_accidents_and_incidents_table_row(self, x, h, w, h_line, title, p_value, c_value, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=5, is_bold=True)
            self.report.cell(w / 2 - 10, h=h_line, txt='    {}'.format(title), align='L')
        else:
            self.__set_font(size=4)
            self.report.cell(w / 2 - 10, h=h_line, txt=title, align='L')

        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value)
        variance, dot = get_variance_and_dot(p_value, c_value)
        self.report.cell(w / 9, h=h_line, txt='{}'.format(p_value), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(c_value), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(variance), align='C')

    def __do_compose_workforce(self, h, options):
        graph_size = (220, 33)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.__add_image(options, WORKFORCE_EXPENDITURE, x=8, y=h + 0.5, w=graph_size[0] - 1, h=graph_size[1] - 1)
        return h + graph_size[1]

    def __do_compose_school_table(self, x, h, options):
        graph_size = (75, 83)
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.__add_image(options, SCHOOLS_IN_DEFICIT, x=x + 0.5, y=h + 0.5, w=graph_size[0] - 1, h=graph_size[1] / 2)

        entity = get_entity_by_m_id(options.entities, '10_05')
        comment = ''
        for d in entity.data_cfy:
            if d.r_comments is not None and len(d.r_comments) > 0:
                comment = d.r_comments
        if len(comment) == 0:
            for d in entity.data_lfy:
                if d.r_comments is not None and len(d.r_comments) > 0:
                    comment = d.r_comments

        self.report.set_xy(x + 0.5, h + graph_size[1] / 2 + 2)
        self.__set_font(size=6)
        self.report.multi_cell(graph_size[0] - 1, 2.5, txt=parse_comment(comment), align='J')

    def __do_compose_hr_workforce(self, h_orig, options):
        graph_size = (405, 83)
        h = h_orig
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)

        h_sc = 4

        self.report.set_xy(7.5, h)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, h=h)
        self.report.cell(121, h=h_sc, txt=text.ABSENCE_DAYS_LOST, fill=1, border=1, align='C')
        self.report.cell(180, h=h_sc, txt=text.WORKING_DAYS_LOST, fill=1, border=1, align='C')
        self.report.cell(104, h=h_sc, txt=text.WORKING_HOURS_LOST, fill=1, border=1, align='C')

        h += h_sc
        self.__reset_colors()
        h_add = self.__do_compose_absence_days_chart(8, h + 0.5, options, 'HRSC_04')
        self.__do_compose_working_day_lost_table(9 + 121, h + 2, 180, options, 'HRSC_03')
        self.__do_compose_working_hours_lost_table(9 + 121 + 180, h + 2, 104, options, 'HRSC_05')

        h = h_add

        self.report.set_xy(7.5, h)
        self.__create_scorecard_top(add_first=False, add_second=False, add_third=True, h=h)
        self.report.cell(121, h=h_sc, txt=text.INSTANCES_OF_ABSENCE_DAYS_LOST, fill=1, border=1, align='C')
        self.report.cell(180, h=h_sc, txt=text.SICKNESS_ABSENCE_RATES, fill=1, border=1, align='C')
        self.report.cell(104, h=h_sc, txt=text.TOP_6_REASONS_FOR_WORKING_DAYS_LOST, fill=1, border=1, align='C')

        h += h_sc
        self.__reset_colors()
        self.__do_compose_instance_table(9, h + 2, 121, options)
        self.__do_compose_sickness_rates_table(9 + 121, h + 2, 180, options, 'HRA_06')
        self.__do_compose_top_reasons_table(9 + 121 + 180, h + 2, 104, options)

        return h_orig + graph_size[1]

    def __do_compose_working_hours_lost_table(self, x, h, w, options, m_id):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4

        d_prev, d_current = get_prev_and_current_month_data(options, m_id)

        self.report.cell(w * 0.25, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w * 0.25, h=h_line, txt=text.VARIANCE, align='C')
        h += h_line

        h_line = 3
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.adult_social_care,
                                                   d_current.adult_social_care)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.education_and_skills,
                                                   d_current.education_and_skills)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.inclusive_growth, d_current.inclusive_growth)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.finance_and_governance,
                                                   d_current.finance_and_governance)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.hr_and_od,
                                                   d_current.hr_and_od)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.neighbourhoods, d_current.neighbourhoods)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.pip,
                                                   d_current.pip)
        h += h_line
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.digital_and_customer_services,
                                                   d_current.digital_and_customer_services)
        h += h_line * 2
        self.__create_working_hours_lost_table_row(x, h, w, h_line, d_prev.bcc, d_current.bcc, is_total=True)

    def __create_working_hours_lost_table_row(self, x, h, w, h_line, v_prev, v_current, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=5, is_bold=True)
        else:
            self.__set_font(size=4)
        v_prev, v_current = self.__adjust_prev_current_values(v_prev, v_current, is_percentage=True)
        variance, dot = get_variance_and_dot(v_prev, v_current)
        self.report.cell(w * 0.25, h=h_line, txt='{:.2f}%'.format(v_prev), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{:.2f}%'.format(v_current), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w * 0.25, h=h_line, txt='{:.2f}%'.format(variance), align='C')

    def __do_compose_working_day_lost_table(self, x, h, w, options, m_id):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4
        self.report.cell(w / 2 - 10, h=h_line)

        d_prev, d_current = get_prev_and_current_month_data(options, m_id)

        self.report.cell(w / 9, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w / 9, h=h_line, txt=text.VARIANCE, align='C')
        h += h_line

        h_line = 3
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.ADULT_SOCIAL_CARE, d_prev.adult_social_care,
                                                d_current.adult_social_care)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.EDUCATION_AND_SKILLS, d_prev.education_and_skills,
                                                d_current.education_and_skills)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.INCLUSIVE_GROWTH, d_prev.inclusive_growth,
                                                d_current.inclusive_growth)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.FINANCE_AND_GOVERNANCE,
                                                d_prev.finance_and_governance,
                                                d_current.finance_and_governance)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.HR_AND_ORGANISATION_DEVELOPMENT,
                                                d_prev.hr_and_od,
                                                d_current.hr_and_od)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.NEIGHBOURHOODS, d_prev.neighbourhoods,
                                                d_current.neighbourhoods)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.PARTNERSHIP_INSIGHT_AND_PREVENTION,
                                                d_prev.pip,
                                                d_current.pip)
        h += h_line
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.DIGITAL_AND_CUSTOMER_SERVICES,
                                                d_prev.digital_and_customer_services,
                                                d_current.digital_and_customer_services)
        h += h_line * 2
        self.__creat_working_day_lost_table_row(x, h, w, h_line, text.TOTAL_CITY_WIDE,
                                                d_prev.bcc,
                                                d_current.bcc,
                                                is_total=True)

    def __creat_working_day_lost_table_row(self, x, h, w, h_line, title, v_prev, v_current, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=5, is_bold=True)
            self.report.cell(w / 2 - 10, h=h_line, txt='    {}'.format(title), align='L')
        else:
            self.__set_font(size=4)
            self.report.cell(w / 2 - 10, h=h_line, txt=title, align='L')
        v_prev, v_current = self.__adjust_prev_current_values(v_prev, v_current)
        variance, dot = get_variance_and_dot(v_prev, v_current)
        self.report.cell(w / 9, h=h_line, txt='{}'.format(v_prev), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(v_current), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(variance), align='C')

    @staticmethod
    def __adjust_prev_current_values(v_prev, v_current, is_percentage=False, is_float=False):
        if v_prev is None or isinstance(v_prev, str):
            v_prev = 0
        if v_current is None or isinstance(v_current, str):
            v_current = 0
        if is_percentage:
            v_prev, v_current = try_parse('{:.2f}'.format(v_prev * 100), is_float=True), \
                                try_parse('{:.2f}'.format(v_current * 100), is_float=True)
        elif is_float:
            v_prev, v_current = try_parse('{:.2f}'.format(v_prev), is_float=True), \
                                try_parse('{:.2f}'.format(v_current), is_float=True)
        else:
            v_prev, v_current = round(v_prev), round(v_current)
        return v_prev, v_current

    def __do_compose_top_reasons_table(self, x, h, w, options):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4
        self.report.cell(w / 2 - 10, h=h_line)

        dp_hrs_3, dc_hrs_3 = get_prev_and_current_month_data(options, 'HRS_03')
        dp_hrs_4, dc_hrs_4 = get_prev_and_current_month_data(options, 'HRS_04')
        dp_hrs_5, dc_hrs_5 = get_prev_and_current_month_data(options, 'HRS_05')
        dp_hrs_6, dc_hrs_6 = get_prev_and_current_month_data(options, 'HRS_06')
        dp_hrs_7, dc_hrs_7 = get_prev_and_current_month_data(options, 'HRS_07')
        dp_hrs_8, dc_hrs_8 = get_prev_and_current_month_data(options, 'HRS_08')

        self.report.cell(w / 9, h=h_line, txt=dp_hrs_3.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=dc_hrs_3.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt='%', align='C')
        h += h_line

        h_line = 2.5
        self.__create_top_reasons_table_row(x, h, w, h_line, text.ANXIETY_STRESS_DEPRESSION, dp_hrs_3.total,
                                            dc_hrs_3.total, dc_hrs_3.percentage)
        h += h_line
        self.__create_top_reasons_table_row(x, h, w, h_line, text.INJURY_FRACTURE, dp_hrs_4.total, dc_hrs_4.total,
                                            dc_hrs_4.percentage)
        h += h_line
        self.__create_top_reasons_table_row(x, h, w, h_line, text.GASTROINTESTINAL_PROBLEMS, dp_hrs_5.total,
                                            dc_hrs_5.total, dc_hrs_5.percentage)
        h += h_line
        self.__create_top_reasons_table_row(x, h, w, h_line, text.OTHER_MUSCULOSKELETAL, dp_hrs_6.total, dc_hrs_6.total,
                                            dc_hrs_6.percentage)
        h += h_line
        self.__create_top_reasons_table_row(x, h, w, h_line, text.OTHER_KNOWN_CAUSES, dp_hrs_7.total, dc_hrs_7.total,
                                            dc_hrs_7.percentage)
        h += h_line
        self.__create_top_reasons_table_row(x, h, w, h_line, text.BACK_PROBLEMS, dp_hrs_8.total, dc_hrs_8.total,
                                            dc_hrs_8.percentage)
        h += h_line * 2
        p_total = dp_hrs_3.total + dp_hrs_4.total + dp_hrs_5.total + dp_hrs_6.total + dp_hrs_7.total + dp_hrs_8.total
        c_total = dc_hrs_3.total + dc_hrs_4.total + dc_hrs_5.total + dc_hrs_6.total + dc_hrs_7.total + dc_hrs_8.total
        self.__create_top_reasons_table_row(x, h, w, h_line, None, p_total, c_total, None, is_total=True)

    def __create_top_reasons_table_row(self, x, h, w, h_line, title, p_total, c_total, percentage, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=5, is_bold=True)
            self.report.cell(w / 2 - 10, h=h_line)
        else:
            self.__set_font(size=4)
            self.report.cell(w / 2 - 10, h=h_line, txt=title, align='L')

        p_total, c_total = self.__adjust_prev_current_values(p_total, c_total)

        self.report.cell(w / 9, h=h_line, txt='{}'.format(p_total), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(c_total), align='C')
        if not is_total:
            percentage, tmp = self.__adjust_prev_current_values(percentage, 0, is_percentage=True)
            self.report.cell(w / 9, h=h_line, txt='{:.2f}%'.format(percentage), align='C')

    def __do_compose_sickness_rates_table(self, x, h, w, options, m_id):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4
        self.report.cell(w / 2 - 10, h=h_line)

        d_prev, d_current = get_prev_and_current_month_data(options, m_id)

        self.report.cell(w / 9, h=h_line, txt=d_prev.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=d_current.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w / 9, h=h_line, txt=text.VARIANCE, align='C')
        h += h_line

        h_line = 2.5
        self.__create_sickness_table_row(x, h, w, h_line, text.ADULT_SOCIAL_CARE, d_prev.adult_social_care,
                                         d_current.adult_social_care)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.EDUCATION_AND_SKILLS, d_prev.education_and_skills,
                                         d_current.education_and_skills)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.INCLUSIVE_GROWTH, d_prev.inclusive_growth,
                                         d_current.inclusive_growth)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.FINANCE_AND_GOVERNANCE, d_prev.finance_and_governance,
                                         d_current.finance_and_governance)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.HR_AND_ORGANISATION_DEVELOPMENT,
                                         d_prev.hr_and_od, d_current.hr_and_od)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.NEIGHBOURHOODS, d_prev.neighbourhoods,
                                         d_current.neighbourhoods)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.PARTNERSHIP_INSIGHT_AND_PREVENTION,
                                         d_prev.pip,
                                         d_current.pip)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.DIGITAL_AND_CUSTOMER_SERVICES,
                                         d_prev.digital_and_customer_services, d_current.digital_and_customer_services)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.COMMONWEALTH_GAMES, d_prev.cwg,
                                         d_current.cwg)
        h += h_line
        self.__create_sickness_table_row(x, h, w, h_line, text.TOTAL_CITY_WIDE, d_prev.bcc, d_current.bcc)

    def __create_sickness_table_row(self, x, h, w, h_line, title, v_prev, v_current, is_total=False):
        self.report.set_xy(x, h)
        if is_total:
            self.__set_font(size=5, is_bold=True)
            self.report.cell(w / 2 - 10, h=h_line, txt='    {}'.format(title), align='L')
        else:
            self.__set_font(size=4)
            self.report.cell(w / 2 - 10, h=h_line, txt=title, align='L')
        v_prev, v_current = self.__adjust_prev_current_values(v_prev, v_current, is_float=True)
        variance, dot = get_variance_and_dot(v_prev, v_current)
        self.report.cell(w / 9, h=h_line, txt='{}'.format(v_prev), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(v_current), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(variance), align='C')

    def __do_compose_instance_table(self, x, h, w, options):
        self.report.set_xy(x, h)
        self.__set_font(size=5, is_bold=True)
        h_line = 4

        self.report.cell(w / 2 - 10, h=h_line)

        dp_hra_1, dc_hra_1 = get_prev_and_current_month_data(options, 'HRA_01')
        dp_hra_2, dc_hra_2 = get_prev_and_current_month_data(options, 'HRA_02')
        dp_hra_4, dc_hra_4 = get_prev_and_current_month_data(options, 'HRA_04')
        dp_hra_5, dc_hra_5 = get_prev_and_current_month_data(options, 'HRA_05')

        dp_hrs_1, dc_hrs_1 = get_prev_and_current_month_data(options, 'HRS_01')
        dp_hrs_2, dc_hrs_2 = get_prev_and_current_month_data(options, 'HRS_02')

        dp_hrsc_6, dc_hrsc_6 = get_prev_and_current_month_data(options, 'HRSC_06')

        self.report.cell(w / 9, h=h_line, txt=dp_hra_1.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=dc_hra_1.month[-3:].title(), align='C')
        self.report.cell(w / 9, h=h_line, txt=text.DOT, align='C')
        self.report.cell(w / 9, h=h_line, txt=text.VARIANCE, align='C')
        h += h_line

        h_line = 3
        self.__creat_instance_table_row(x, h, w, h_line, text.NO_OF_CORE_WORKFORCE_FTE, dp_hra_5.bcc, dc_hra_5.bcc)
        h += h_line
        p_total = dp_hrs_1.total + dp_hrs_2.total
        c_total = dc_hrs_1.total + dc_hrs_2.total
        self.__creat_instance_table_row(x, h, w, h_line, text.TOTAL_FTE_SICKNESS_DAYS_LOST, p_total, c_total)
        h += h_line
        p_total = dp_hra_1.bcc + dp_hra_2.bcc
        c_total = dc_hra_1.bcc + dc_hra_2.bcc
        self.__creat_instance_table_row(x, h, w, h_line, text.TOTAL_ABSENCES, p_total, c_total)
        h += h_line
        self.__creat_instance_table_row(x, h, w, h_line, text.ABSENCES_LESS_THAN_28_DAYS, dp_hra_1.bcc, dc_hra_1.bcc)
        h += h_line
        self.__creat_instance_table_row(x, h, w, h_line, text.ABSENCES_MORE_THAN_29_DAYS,
                                        dp_hra_2.bcc, dc_hra_2.bcc)
        h += h_line
        self.__creat_instance_table_row(x, h, w, h_line, text.LTS_ABSENCES_LONGER_THAN_6_MONTHS,
                                        dp_hra_4.bcc, dc_hra_4.bcc)
        h += h_line
        self.__creat_instance_table_row(x, h, w, h_line, text.STAFF_EXCEEDED_4_PERIODS_10_DAYS, dp_hrsc_6.bcc,
                                        dc_hrsc_6.bcc)

    def __creat_instance_table_row(self, x, h, w, h_line, title, p_value, c_value):
        self.report.set_xy(x, h)
        self.__set_font(size=4)
        self.report.cell(w / 2 - 10, h=h_line, txt=title, align='L')
        p_value, c_value = self.__adjust_prev_current_values(p_value, c_value)
        variance, dot = get_variance_and_dot(p_value, c_value)
        self.report.cell(w / 9, h=h_line, txt='{}'.format(p_value), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(c_value), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(dot), align='C')
        self.report.cell(w / 9, h=h_line, txt='{}'.format(variance), align='C')

    def __do_compose_absence_days_chart(self, x, h, options, m_id):
        graph_size = (120, 40)
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.set_title(text.ABSENCE_DAYS_LOST_12_MONTHS_ROLLING,
                     fontproperties=self.__get_font_props(DEJAVU_SERIF_CONDENSED_BOLD, size=12, bold=True), wrap=True)

        entity = get_entity_by_m_id(options.entities, m_id, has_measure=False)
        f_data = filter_data_by_fym(entity.data(), options.fym)
        freq = FREQ_MONTHLY
        x_ticks, x_ticks_lbl = self.__get_ticks_and_target(freq, f_data, populate_target=False)
        y_target = [x.bcc for x in f_data]

        y_lim_min = int(math.ceil(min(y_target) / 10.0)) * 10 - 20
        y_lim_max = int(math.ceil(max(y_target) / 10.0)) * 10 + 10

        if len(y_target) < len(x_ticks):
            for i in range(0, len(x_ticks) - len(y_target), 1):
                y_target.append(0)

        b_width = 0.4
        ind = np.arange(12)
        ax.bar(ind, y_target[:12], width=b_width, color=str(get_color(BLUE)))
        ax.bar(ind + b_width, y_target[12:], width=b_width, color=str(get_color(AMBER)))

        ax.set_ylim(y_lim_min, y_lim_max)
        ax.grid(color='grey', which='major', axis='y', linestyle='-', linewidth=0.5, zorder=0)

        ax.set_xticks(ind + b_width / 2)
        ax.set_xticklabels(x_ticks_lbl[:12], rotation='horizontal')

        ax.autoscale_view()

        f_path = join(get_dir_path(TEMP), '{}_bar_chart.png'.format(m_id))
        fig.savefig(f_path)
        plt.close(fig=fig)
        self.report.image(f_path, x=x, y=h, w=graph_size[0], h=graph_size[1], type='', link='')
        return h + graph_size[1]

    def __do_compose_financial_charts(self, h, options):
        graph_size = (110, 83)
        m_ids = ['9_08', '9_09', '9_10']
        titles = [text.COLLECTION_OF_COUNCIL_TAX_IN_YEAR, text.COLLECTION_OF_BUSINESS_RATES_IN_YEAR,
                  text.COUNCIL_TAX_PAID_BY_DIRECT_DEBIT]
        for m_id in m_ids:
            x = 7.5 + (graph_size[0] * m_ids.index(m_id))

            entity = get_entity_by_m_id(options.entities, m_id)
            freq = self.__get_freq(entity.measure_cfy.frequency.upper())
            f_data = filter_data_by_fym(entity.data(), options.fym)

            self.report.set_xy(x, h)
            self.report.cell(graph_size[0], h=graph_size[1], border=1)
            self.report.set_xy(x + 0.5, h + 0.5)
            self.__compose_financial_chart(f_data, titles[m_ids.index(m_id)],
                                           m_id, freq)

            self.report.set_xy(x + 2.5, h + graph_size[1] / 2 + 3)
            self.__compose_report_comment(f_data, w=graph_size[0] - 5)

            self.__compose_financial_table(entity, x=x + graph_size[0] / 2 + 22, y=h + 8)

        return h + graph_size[1]

    def __compose_financial_table(self, entity, x, y):
        self.report.set_xy(x, y)
        frequency = self.__get_freq(entity.measure_cfy.frequency.upper())
        d_format = entity.measure_cfy.data_format

        data_current_pos_list = get_current_pos(entity.data())
        if len(data_current_pos_list) == 0:
            dot, result, target = '', '', ''
            baseline = text.NOT_APPLICABLE
        else:
            recent_data = data_current_pos_list[len(data_current_pos_list) - 1]
            if FREQ_ANNUAL in frequency:
                dot = format_value(recent_data.dot_from_same_period_last_year)
            elif FREQ_QUARTER in frequency:
                dot = format_value(recent_data.dot_from_previous_quarter)
            else:
                dot = format_value(recent_data.dot_from_previous_month)
            dot = get_text_dot(dot)
            result = format_value(recent_data.result, d_format)
            target = format_value(recent_data.target, d_format)
            baseline = format_value(entity.get_measure(recent_data).baseline, d_format)

        self.__set_font(is_bold=True, size=5)
        self.report.cell(14, 6, text.DOT, border='L', ln=0, align='C')
        self.__set_font(is_bold=False, size=5)
        self.report.cell(15, 6, dot, border='R', ln=2, align='C')
        self.report.cell(-14)

        self.__set_font(is_bold=True, size=5)
        self.report.cell(14, 6, text.ACTUAL, border='L', ln=0, align='C')
        self.__set_font(is_bold=False, size=5)
        self.report.cell(15, 6, result, border='R', ln=2, align='C')
        self.report.cell(-14)

        self.__set_font(is_bold=True, size=5)
        self.report.cell(14, 6, text.TARGET, border='L', ln=0, align='C')
        self.__set_font(is_bold=False, size=5)
        self.report.multi_cell(15, 3, '{} ({})'.format(target, text.IN_YEAR_FORECAST), border='R', ln=2, align='C')
        self.report.cell(-14)

        self.__set_font(is_bold=True, size=5)
        self.report.cell(14, 6, text.BASELINE, border='L', ln=0, align='C')
        self.__set_font(is_bold=False, size=5)
        self.report.cell(15, 6, baseline, border='R', ln=2, align='C')
        self.report.cell(-14)

    def __compose_financial_chart(self, data, title, m_id, freq):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title(title, fontproperties=self.__get_font_props(DEJAVU_SERIF_CONDENSED_BOLD, size=16, bold=True),
                     wrap=True)

        x_ticks, x_ticks_lbl, y_target = self.__get_ticks_and_target(freq, data)
        y_target = [try_parse('{:.2f}'.format(x * 100), is_float=True) for x in y_target]
        ax.plot(x_ticks, y_target, "k--", color='darkblue', zorder=4)

        results = get_results_per_given_frequency(data, freq, x_ticks)
        results = [try_parse('{:.2f}'.format(x * 100), is_float=True) for x in results]
        performance = get_performance_per_given_frequency(data, freq, x_ticks)

        blue_data = sort_results_and_months_by_performance(results, x_ticks, performance, BLUE)
        green_data = sort_results_and_months_by_performance(results, x_ticks, performance, GREEN)
        amber_data = sort_results_and_months_by_performance(results, x_ticks, performance, AMBER)
        red_data = sort_results_and_months_by_performance(results, x_ticks, performance, RED)
        grey_data = sort_results_and_months_by_performance(results, x_ticks, performance, GREY)
        brag_grey_data = sort_results_and_months_by_performance(results, x_ticks, performance, None)

        self.__create_bar(ax, blue_data, get_color(BLUE))
        self.__create_bar(ax, green_data, get_color(GREEN))
        self.__create_bar(ax, amber_data, get_color(AMBER))
        self.__create_bar(ax, red_data, get_color(RED))
        self.__create_bar(ax, grey_data, get_color(GREY))
        self.__create_bar(ax, brag_grey_data, get_color(GREY))

        ax.set_ylim(0, 100)
        ax.set_yticklabels(['{}%'.format(x) for x in ax.get_yticks()])
        ax.grid(color='grey', which='major', axis='y', linestyle='-', linewidth=0.5, zorder=0)

        ax.set_xticks(x_ticks)
        new_lbl = []
        for x in x_ticks_lbl:
            if (x_ticks_lbl.index(x) + 1) % 2 != 0:
                new_lbl.append(x)
            else:
                new_lbl.append('')
        ax.set_xticklabels(new_lbl, rotation=45, ha='right')

        f_path = join(get_dir_path(TEMP), '{}_bar_chart.png'.format(m_id))
        fig.savefig(f_path)
        plt.close(fig=fig)
        self.report.image(f_path, x=None, y=None, w=80, h=0, type='', link='')

    def __do_compose_cpm_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True, month_id=try_parse(str(options.fym)[-2:], is_int=True))

        self.report.cell(112, h=8.5, txt=text.COUNCIL_PLANS_MEASURE_SUMMARY, fill=1, align='C', border=1)
        self.report.cell(153, h=8.5, txt=text.KEY_RESULTS_ACTIONS, fill=1, align='C', border=1)
        self.report.cell(140, h=8.5, txt=text.KEY, fill=1, align='C', border=1)

        self.__reset_colors()

        h += 8.5
        self.report.set_xy(7.5, h)
        self.report.cell(112, h=60, border=1)
        self.report.cell(153, h=60, border=1)
        self.report.cell(140, h=60, border=1)

        self.__compose_measure_summary(h, options.entities)
        self.__compose_key_results_actions(h, options.entities, m_id='PMT_01')

        self.report.set_xy(273, h + 0.5)
        self.__add_image(options, LEGEND, w=139, h=59)

    def __compose_measure_summary(self, h, entities, is_cpm=True):
        if is_cpm:
            e_sorted = [e for e in entities if isinstance(e, CpmEntity)]
        else:
            e_sorted = [e for e in entities if isinstance(e, SdmEntity)]

        h += 1
        self.report.set_xy(9, h)
        self.__set_font(size=6, is_bold=True)
        self.report.cell(35, 6, '{}:'.format(text.TOTAL_MEASURES), align='L')
        n_sorted = len(e_sorted)
        self.report.cell(20, 6, '{}'.format(n_sorted), align='L')

        b_sorted = sort_entities_by_performance(e_sorted, PERF_BLUE)
        exc = [x.measure_cfy.m_id for x in b_sorted]
        g_sorted = sort_entities_by_performance(e_sorted, PERF_GREEN, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in g_sorted]
        r_sorted = sort_entities_by_performance(e_sorted, PERF_RED, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in r_sorted]
        a_sorted = sort_entities_by_performance(e_sorted, PERF_AMBER, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in a_sorted]
        nyd_sorted = sort_entities_by_performance(e_sorted, PERF_NYD, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in nyd_sorted]
        pr_sorted = sort_entities_by_performance(e_sorted, PERF_PREV_REPORTED, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in pr_sorted]
        aw_sorted = sort_entities_by_performance(e_sorted, PERF_AWAITING, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in aw_sorted]
        t_sorted = sort_entities_by_performance(e_sorted, PERF_TREND, exclusions=exc)
        h += 3
        self.report.set_xy(15, h)
        self.report.cell(35, 6, '{}:'.format(text.AVAILABLE_TO_REPORT), align='L')
        m_sum = len(b_sorted) + len(g_sorted) + len(r_sorted) + len(a_sorted) + len(t_sorted)
        self.report.cell(50, 6, text.INCLUDING_TREND_OR_PROJECT_UPDATE_MEASURES.format(m_sum, len(t_sorted)), align='L')

        h += 6
        self.report.set_xy(7.5, h)
        for i in range(0, 7, 1):
            self.report.cell(16, h=8, border=1)

        h += 2
        self.report.set_xy(23.5, h)
        self.report.multi_cell(16, h=2.5, txt=text.LEAN_WORK_INVEST, align='C')
        self.report.multi_cell(16, h=2.5, txt=text.GROW_UP, align='C')
        self.report.multi_cell(16, h=2.5, txt=text.AGE_WELL, align='C')
        self.report.multi_cell(16, h=2.5, txt=text.LIVE_IN, align='C')
        if is_cpm:
            self.report.multi_cell(16, h=2.5, txt=text.CWG, align='C')
        else:
            self.report.multi_cell(16, h=2.5, txt=text.SSG, align='C')
        self.report.multi_cell(16, h=2.5, txt=text.TOTAL, align='C')

        h += 6
        self.__set_font(size=6, is_bold=True)
        for i in range(0, 8, 1):
            self.report.set_xy(7.5, h)
            for j in range(0, 7, 1):
                if i == 7:
                    self.report.cell(16, h=7, border=1)
                else:
                    self.report.cell(16, h=5, border=1)
            self.report.set_xy(7.5, h)

            if i == 0:
                self.__compose_measure_summary_row(text.BLUE, remove_entities_with_no_outcome(b_sorted),
                                                   color=get_color(BLUE), is_cpm=is_cpm)
            elif i == 1:
                self.__compose_measure_summary_row(text.GREEN, remove_entities_with_no_outcome(g_sorted),
                                                   color=get_color(GREEN), is_cpm=is_cpm)
            elif i == 2:
                self.__compose_measure_summary_row(text.AMBER, remove_entities_with_no_outcome(a_sorted),
                                                   color=get_color(AMBER), is_cpm=is_cpm)
            elif i == 3:
                self.__compose_measure_summary_row(text.RED, remove_entities_with_no_outcome(r_sorted),
                                                   color=get_color(RED), is_cpm=is_cpm)
            elif i == 4:
                self.__compose_measure_summary_row(text.TREND, remove_entities_with_no_outcome(t_sorted),
                                                   color=get_color(GREY), is_cpm=is_cpm)
            elif i == 5:
                self.__compose_measure_summary_row(text.NYD, remove_entities_with_no_outcome(nyd_sorted), is_cpm=is_cpm)
            elif i == 6:
                self.__compose_measure_summary_row(text.AWAITING, remove_entities_with_no_outcome(aw_sorted),
                                                   is_cpm=is_cpm)
            elif i == 7:
                self.__compose_measure_summary_row(text.PREVIOUSLY_REPORTED, remove_entities_with_no_outcome(pr_sorted),
                                                   is_cpm=is_cpm)
            h += 5

    def __compose_measure_summary_row(self, txt='', entities=(), color=get_color(BLACK), is_cpm=True):
        self.report.set_text_color(color.r, color.g, color.b)
        if txt == text.PREVIOUSLY_REPORTED:
            self.report.multi_cell(16, h=3, txt=txt, align='L')
        else:
            self.report.multi_cell(16, h=5, txt=txt, align='L')
        color = get_color(BLACK)
        self.report.set_text_color(color.r, color.g, color.b)
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_LEARN_WORK_INVEST))),
                         align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_GROW_UP))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_AGE_WELL))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_LIVE_IN))), align='C')
        if is_cpm:
            self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_CWG))), align='C')
        else:
            self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_SSG))), align='C')

        self.report.cell(16, h=6, txt='{}'.format(len(entities)), align='C')

    def __compose_key_results_actions(self, h, entities, m_id=None):
        data = get_data_by_m_id_and_date(entities, m_id, self.options.fym)
        self.report.set_xy(121, h + 2)
        self.__set_font(size=6)
        self.report.multi_cell(150, h=2.5, txt=parse_comment(data.measure_text_column_1), align='J')

    def __do_compose_grid_charts(self, options):
        graphs = 0
        coords = list(self.left_top)

        e_sorted = list()
        for e in options.entities:
            if not isinstance(e, CpmEntity):
                continue
            e_sorted.append(e)
        e_sorted.sort(key=lambda x: (get_outcome_priority(x.measure_cfy.outcome), x.measure_cfy.m_ref_no))

        # compose grid charts for CPM measures
        for entity in e_sorted:
            if not isinstance(entity, CpmEntity):
                continue
            # check if entity should be excluded from the report
            if options.exclusions is not None and entity.measure_cfy.m_id in options.exclusions:
                logging.debug('Ignoring entity [{}]'.format(entity.measure_lfy.m_id))
                continue
            # check if coords are equal to initial left-top
            # then create new page
            if graphs == 0:
                self.report.add_page()
            graphs += 1
            # create chart
            self.__compose_visuals_for_entity(entity, coords, options.fym)

            # check if number of graphs on grid row has exceeded the allowed amount
            if graphs % self.grid_size[1] == 0:
                coords[0] = self.left_top[0]
                coords[1] += self.graph_size[1]
            else:
                coords[0] += self.graph_size[0]
            # check if number of graphs on page has exceeded the allowed amount
            # then create setup properties for new page to be added
            if graphs % (self.grid_size[0] * self.grid_size[1]) == 0:
                self.__set_grid(n_cells=graphs)
                coords = list(self.left_top)
                graphs = 0
                self.__create_scorecard_top(x=self.left_top[0], h=self.left_top[1] - 8.5, add_second=False,
                                            w=self.graph_size[0] * self.grid_size[1],
                                            month_id=try_parse(str(options.fym)[-2:], is_int=True))
        if graphs > 0:
            self.__create_scorecard_top(x=self.left_top[0], h=self.left_top[1] - 8.5, add_second=False,
                                        w=self.graph_size[0] * self.grid_size[1],
                                        month_id=try_parse(str(options.fym)[-2:], is_int=True))
            self.__reset_colors()
            self.__set_grid(n_cells=graphs)

    def __reset_colors(self):
        color = get_color(WHITE)
        self.report.set_fill_color(color.r, color.g, color.b)
        color = get_color(BLACK)
        self.report.set_text_color(color.r, color.g, color.b)

    def __create_scorecard_top(self, add_page=False, h=98.0, add_first=True, add_second=True, add_third=False, w=405,
                               x=7.5, month_id=None):
        self.__set_font(size=8, is_bold=True)
        if add_page:
            self.report.add_page()
        if add_first:
            if month_id is None:
                raise RGError('Month ID is not provided for scorecard header')
            self.report.set_xy(x, h)
            color = get_color(DARK_BLUE)
            self.report.set_fill_color(color.r, color.g, color.b)
            color = get_color(WHITE)
            self.report.set_text_color(color.r, color.g, color.b)
            self.report.cell(w, h=8.5,
                             txt=text.MONTHLY_PERFORMANCE_SCORECARD.format(get_month_name_from_id(month_id), 2020),
                             fill=1, align='C')
            h += 8.5

        if add_second:
            self.report.set_xy(x, h)
            color = get_color(AQUA)
            self.report.set_fill_color(color.r, color.g, color.b)
            color = get_color(WHITE)
            self.report.set_text_color(color.r, color.g, color.b)

        if add_third:
            self.__set_font(size=5, is_bold=True)
            self.report.set_xy(x, h)
            color = get_color(LIGHT_AQUA)
            self.report.set_fill_color(color.r, color.g, color.b)
            color = get_color(BLACK)
            self.report.set_text_color(color.r, color.g, color.b)

        return h

    def __do_compose_sdm_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True, month_id=try_parse(str(options.fym)[-2:], is_int=True))

        self.report.cell(112, h=8.5, txt=text.SUMMARY, fill=1, align='C', border=1)
        self.report.cell(293, h=8.5, txt=text.KEY_RESULTS_SERVICE_DELIVERY_MEASURES, fill=1, align='C', border=1)

        self.__reset_colors()

        h += 8.5
        self.report.set_xy(7.5, h)
        self.report.cell(112, h=60, border=1)
        self.report.cell(293, h=60, border=1)

        self.__compose_measure_summary(h, options.entities, is_cpm=False)
        self.__compose_key_results_actions(h, options.entities, m_id='PMT_02')

    def __set_grid(self, n_cells=0):
        if n_cells == 0:
            return
        self.report.set_xy(10, 30)
        self.__set_font(size=8, is_bold=True)
        if n_cells > 0:
            self.report.cell(w=135, h=118, border=1)
        if n_cells > 1:
            self.report.cell(w=135, h=118, border=1)
        if n_cells > 2:
            self.report.cell(w=135, h=118, border=1, ln=2)
        if n_cells > 3:
            self.report.cell(-270)
            self.report.cell(w=135, h=118, border=1)
        if n_cells > 4:
            self.report.cell(w=135, h=118, border=1)
        if n_cells > 5:
            self.report.cell(w=135, h=118, border=1, ln=2)

    def __add_empty_line(self, h=1):
        self.__set_font(size=5)
        self.report.cell(0, h=h, txt=' ', ln=2, align='C')

    def __set_font(self, family=REPORT_FONT, is_bold=False, size=5):
        if is_bold:
            self.report.set_font(family, 'B', size)
        else:
            self.report.set_font(family, '', size)

    def __compose_visuals_for_entity(self, entity, left_top, fym):
        self.__reset_colors()
        self.report.set_xy(left_top[0], left_top[1])
        d_format = entity.measure_cfy.data_format
        frequency = entity.measure_cfy.frequency.upper()
        f_data = filter_data_by_fym(entity.data(), fym)
        self.__compose_bar_chart(entity.measure_cfy, f_data, frequency, d_format)

        self.__add_empty_line()
        self.__compose_report_comment(f_data)

        self.report.set_xy(left_top[0] + 95, left_top[1] + 5)
        self.__compose_benchmark_tbl(entity, d_format, fym)

        self.__add_empty_line()
        self.__compose_current_pos_tbl(entity, frequency, d_format, fym)

        self.__add_empty_line()
        self.__compose_gauge_chart(get_data_by_date(entity.data(), fym))

    def __compose_report_comment(self, data_list, w=93):
        r_comment = get_report_comment(data_list)
        self.__set_font(size=5, family=REPORT_FONT)
        self.report.multi_cell(w, 2.5, txt=parse_comment(r_comment), align='J')

    def __compose_benchmark_tbl(self, entity, d_format, fym):
        data_with_bmk_list = get_bmk(get_data_by_date(entity.data(), fym))
        if len(data_with_bmk_list) == 0:
            nat_avg = text.NO_BENCHMARK
            b_at_bmk, quartile, bmk_y, bmk_g, pref_dot = '', '', '', '', ''
        else:
            recent_data = data_with_bmk_list[len(data_with_bmk_list) - 1]
            nat_avg = format_value(recent_data.bck_result, d_format)
            b_at_bmk = format_value(recent_data.brum_result_at_bck, d_format)

            quartile = format_value(recent_data.brum_quartile_pos)
            if quartile is None or len(quartile) == 0:
                quartile = text.NOT_APPLICABLE
            quartile = quartile.upper()

            bmk_y = '{} {}'.format(text.BENCHMARK, format_value(recent_data.year_of_bck_data))
            bmk_g = format_value(recent_data.bck_group)

            pref_dot = get_text_dot(entity.measure_cfy.pref_dot)

        self.__set_font(is_bold=True, size=8)
        self.report.cell(37, 6, text.BENCHMARK, 1, 2, 'C')

        self.__set_font(size=7)
        self.report.cell(17, 6, text.PREFERRED_DOT, border='L', ln=0, align='C')
        self.report.cell(20, 6, pref_dot, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, text.NATIONAL_AVERAGE, border='L', ln=0, align='C')
        self.report.cell(20, 6, nat_avg, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, text.BIRMINGHAM, border='L', ln=0, align='C')
        self.report.cell(20, 6, b_at_bmk, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, text.QUARTILE, border='L', ln=0, align='C')
        if text.FOURTH in quartile:
            color = get_color(RED)
        elif text.THIRD in quartile:
            color = get_color(AMBER)
        elif text.SECOND in quartile:
            color = get_color(GREEN)
        elif text.FIRST in quartile:
            color = get_color(BLUE)
        else:
            color = get_color(WHITE)
        self.report.set_fill_color(r=color.r, g=color.g, b=color.b)
        self.report.cell(20, 6, quartile, border='R', ln=2, align='C', fill=True)
        self.report.cell(-17)

        self.__set_font(size=6)
        self.report.multi_cell(37, 5, '{} {}'.format(bmk_y, bmk_g), ln=2, border='LRB', align='C')

    def __compose_current_pos_tbl(self, entity, frequency, d_format, fym):
        data_current_pos_list = get_current_pos(get_data_by_date(entity.data(), fym))
        if len(data_current_pos_list) == 0:
            dot, result, target = '', '', ''
            fill_bool = False
            baseline = text.NOT_APPLICABLE
        else:
            month_data = data_current_pos_list[len(data_current_pos_list) - 1]
            if FREQ_ANNUAL in frequency:
                dot = format_value(month_data.dot_from_same_period_last_year)
            elif FREQ_QUARTER in frequency:
                dot = format_value(month_data.dot_from_previous_quarter)
            else:
                dot = format_value(month_data.dot_from_previous_month)
            dot = get_text_dot(dot)
            result = format_value(month_data.result, d_format)
            target = format_value(month_data.target, d_format)
            fill_bool = month_data.status.upper() == text.PROVISIONAL
            baseline = format_value(entity.get_measure(month_data).baseline, d_format)
        self.__set_font(is_bold=True, size=8)
        self.report.cell(37, 6, text.CURRENT_POSITION, 1, 2, 'C')
        self.__set_font(is_bold=False, size=7)

        self.report.cell(17, 6, text.DOT, border='L', ln=0, align='C')
        self.report.cell(20, 6, dot, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.set_fill_color(r=255, g=255, b=0)
        self.report.cell(17, 6, text.ACTUAL, border='L', ln=0, align='C')
        self.report.cell(20, 6, result, border='R', ln=2, align='C', fill=fill_bool)
        self.report.cell(-17)

        self.report.cell(17, 6, text.TARGET, border='L', ln=0, align='C')
        self.report.cell(20, 6, target, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, text.BASELINE, border='LB', ln=0, align='C')
        self.report.cell(20, 6, baseline, border='RB', ln=2, align='C')
        self.report.cell(-17)

    def __compose_gauge_chart(self, data_list):
        result = get_qp(data_list)
        if len(result) == 0:
            return
        data = result[0]
        self.__set_font(is_bold=True, size=6)
        self.report.cell(37, 6, text.QUARTILE_PROJECTION, align='C', ln=2)
        self.__set_font(size=5)
        self.report.multi_cell(37, 2.5, text.CURRENT_ACTUAL_AGAINST_NATIONAl_DATA_AVAILABLE, align='C', ln=2)

        qp_value = try_parse(data.quartile_projection, is_int=True)

        g_chart = graph_objects.Figure(data=graph_objects.Indicator(
            mode='gauge',
            value=0,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': 'darkblue'},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': 'gray',
                'steps': [
                    {'range': [0, 25], 'color': str(get_color(BLUE))},
                    {'range': [25, 50], 'color': str(get_color(GREEN))},
                    {'range': [50, 75], 'color': str(get_color(AMBER))},
                    {'range': [75, 100], 'color': str(get_color(RED))}],
                'threshold': {
                    'line': {'color': "black", 'width': 10},
                    'thickness': 1,
                    'value': qp_value
                }
            }
        ))
        f_path = join(get_dir_path(TEMP), '{}_quartile_projection.png'.format(data.m_id))
        g_chart.write_image(f_path)
        self.report.image(f_path, x=None, y=None, w=37, h=0, type='', link='')

    def __compose_bar_chart(self, measure, data_list, frequency, d_format):
        fig, ax = plt.subplots()
        graph_title = '{} (ex. {})'.format(measure.m_title, measure.m_ref_no)
        ax.set_title(graph_title.replace('\r', '').replace('\n', ''),
                     fontproperties=self.__get_font_props(DEJAVU_SERIF_CONDENSED_BOLD, size=12, bold=True), wrap=True)

        x_freq = self.__get_freq(frequency)
        x_ticks, x_ticks_lbl, y_target = self.__get_ticks_and_target(x_freq, data_list)

        is_empty_target = True
        for target in y_target:
            if target != 0:
                is_empty_target = False
        if not is_empty_target:
            ax.plot(x_ticks, y_target, "k--", color='darkblue', zorder=4)

        baseline = try_parse(measure.baseline, is_float=True)
        if baseline is None and isinstance(measure.baseline, str):
            baseline = measure.baseline.split('%')[0]
            baseline = ''.join(ch for ch in baseline if ch.isdigit() or ch == '.')
            baseline = try_parse(baseline, is_float=True)

        if baseline is not None:
            ax.plot(x_ticks, [baseline] * len(x_ticks), color='brown', zorder=4)
        else:
            logging.error('Invalid floating point value for measure baseline [{}]'.format(measure.baseline))

        ax.grid(color='grey', which='major', axis='y', linestyle='-', linewidth=0.5, zorder=0)
        results = get_results_per_given_frequency(data_list, x_freq, x_ticks)
        performance = get_performance_per_given_frequency(data_list, x_freq, x_ticks)

        blue_data = sort_results_and_months_by_performance(results, x_ticks, performance, BLUE)
        green_data = sort_results_and_months_by_performance(results, x_ticks, performance, GREEN)
        amber_data = sort_results_and_months_by_performance(results, x_ticks, performance, AMBER)
        red_data = sort_results_and_months_by_performance(results, x_ticks, performance, RED)
        grey_data = sort_results_and_months_by_performance(results, x_ticks, performance, GREY)
        brag_grey_data = sort_results_and_months_by_performance(results, x_ticks, performance, None)

        if len(x_ticks) == 1:
            ax.set_xlim(int(x_ticks[0]) - 1, int(x_ticks[0]) + 1)

        self.__create_bar(ax, blue_data, get_color(BLUE))
        self.__create_bar(ax, green_data, get_color(GREEN))
        self.__create_bar(ax, amber_data, get_color(AMBER))
        self.__create_bar(ax, red_data, get_color(RED))
        self.__create_bar(ax, grey_data, get_color(GREY))
        self.__create_bar(ax, brag_grey_data, get_color(GREY))

        ax.set_xticks(x_ticks)
        if x_freq == FREQ_MONTHLY:
            ax.set_xticklabels(x_ticks_lbl, rotation=45, ha='right')
        else:
            ax.set_xticklabels(x_ticks_lbl, rotation='horizontal')

        if d_format.upper() == PERCENTAGE:
            y_ticks = ax.get_yticks()
            ax.set_yticklabels(['{}%'.format(int(x * 100)) for x in y_ticks])

        f_path = join(get_dir_path(TEMP), '{}_bar_chart.png'.format(measure.m_id))
        fig.savefig(f_path)
        plt.close(fig=fig)
        self.report.image(f_path, x=None, y=None, w=94, h=0, type='', link='')

    @staticmethod
    def __create_bar(ax, data, color, width=0.6):
        if len(data[0]) > 0:
            ax.bar(data[0], data[1], color=str(color), width=width, align='center')

    @staticmethod
    def __get_ticks_and_target(freq, data_list, populate_target=True):
        y_target = None
        if freq == FREQ_ANNUAL:
            x_ticks = sorted(set([try_parse(x.year, is_int=True) for x in data_list]))
            x_ticks_lbl = sorted(set([x.f_year for x in data_list]))

            if populate_target:
                y_target = get_target_per_given_frequency(data_list, freq, x_ticks)
        elif freq == FREQ_QUARTER:
            x_ticks = sorted(set([try_parse(x.year_quarter, is_int=True) for x in data_list]))
            # get quarter abbreviations
            x_ticks_lbl = QUARTERS + QUARTERS

            PDFReporter.__validate_ticks(x_ticks, x_ticks_lbl, 4)

            if populate_target:
                y_target = get_target_per_given_frequency(data_list, freq, x_ticks)
        else:
            x_ticks = [try_parse(x.year_month, is_int=True) for x in data_list]
            # get month abbreviations
            x_ticks_lbl = list(FISCAL_MONTHS.values())
            x_ticks_lbl = x_ticks_lbl + x_ticks_lbl

            PDFReporter.__validate_ticks(x_ticks, x_ticks_lbl, 12)

            if populate_target:
                y_target = get_target_per_given_frequency(data_list, freq, x_ticks)

        if populate_target:
            return [str(x) for x in x_ticks], x_ticks_lbl, y_target
        else:
            return [str(x) for x in x_ticks], x_ticks_lbl

    @staticmethod
    def __get_freq(freq):
        # if frequency is unknown, by default it is configured to monthly
        r_freq = FREQ_MONTHLY
        if freq in ['Q', 'QUARTER', 'QUARTERLY']:
            r_freq = FREQ_QUARTER
        elif freq in ['A', 'ANNUAL', 'ANNUALLY', 'YEAR', 'YEARLY', 'BI A', 'BI ANNUAL', 'BI_ANNUALLY']:
            r_freq = FREQ_ANNUAL
        return r_freq

    @staticmethod
    def __validate_ticks(x_ticks, x_ticks_lbl, value):
        if len(x_ticks_lbl) > len(x_ticks):
            last_tick = x_ticks[len(x_ticks) - 1]
            if len(x_ticks) < value:
                for i in range(0, value - len(x_ticks), 1):
                    last_tick += 1
                    x_ticks.append(str(last_tick))
                # increase fiscal year and deduct 12 months
                last_tick += 10100 - value
                for i in range(0, value, 1):
                    last_tick += 1
                    x_ticks.append(str(last_tick))
            else:
                for i in range(0, len(x_ticks_lbl) - len(x_ticks), 1):
                    last_tick += 1
                    x_ticks.append(str(last_tick))
