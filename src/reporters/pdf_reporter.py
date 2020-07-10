import os

import matplotlib.pyplot as plt
from fpdf import FPDF
from matplotlib.ticker import PercentFormatter
from plotly import graph_objects

import text as text
from models.entities import CpmEntity, SdmEntity, PmtAdditionalEntity
from reporters.reporter_base import RGReporterBase
from utils import *


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
        super().do_init()
        self.report = FPDF('L', 'mm', (297, 420))
        self.report.add_font(DEJAVU_SANS, '', get_font(DEJAVU_SANS), uni=True)
        self.report.add_font(DEJAVU_SANS, 'B', get_font(DEJAVU_SANS_BOLD), uni=True)
        self.report.add_font(DEJAVU_SANS_MONO, '', get_font(DEJAVU_SANS_MONO), uni=True)
        self.report.add_font(DEJAVU_SANS_MONO, 'B', get_font(DEJAVU_SANS_MONO_BOLD), uni=True)
        self.report.add_font(DEJAVU_SERIF, '', get_font(DEJAVU_SERIF), uni=True)
        self.report.add_font(DEJAVU_SERIF, 'B', get_font(DEJAVU_SERIF_BOLD), uni=True)
        self.report.add_font(DEJAVU_SERIF_CONDENSED, '', get_font(DEJAVU_SERIF_CONDENSED), uni=True)
        self.report.add_font(DEJAVU_SERIF_CONDENSED, 'B', get_font(DEJAVU_SERIF_BOLD), uni=True)
        self.report.add_font(LUCIDA_SANS, '', get_font(LUCIDA_SANS), uni=True)
        self.report.add_font(LUCIDA_SANS, 'B', get_font(LUCIDA_SANS), uni=True)

        self.report.set_doc_option("core_fonts_encoding", REPORT_ENCODING)

        self.report.set_auto_page_break(auto=False)

    def do_export(self, out_dir=None):
        self.report.output(name=os.path.join(out_dir, '{}_{}.{}'.format(self.report_name, timestamp(), EXT_PDF)),
                           dest='F')

    def do_compose(self, options=None):
        # self.__do_compose_cpm_scorecard(options)
        # self.__do_compose_grid_charts(entities=options.entities, exclusions=options.exclusions)
        # self.__do_compose_sdm_scorecard(options)
        self.__do_compose_financial_hr_scorecard(options)
        # self.__do_compose_relationship_effectiveness_scorecard(options)

    def __do_compose_relationship_effectiveness_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True, h=2.25, w=405)
        self.report.cell(220, h=8.5, txt=text.FINANCIAL_MANAGEMENT, fill=1, align='C', border=1)
        self.report.cell(185, h=8.5, txt=text.REPORTED_QUARTERLY_NO_UPDATE_RECEIVED, fill=1, align='C', border=1)
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
        graph_size = (185, 52)
        self.__set_font(size=6)
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        entity = get_entity_by_m_id(options.entities, 'PMT_03', has_measure=False)
        column_1, column_2 = '', ''
        for d in entity.data_cfy:
            if d.measureTextColumn1 is not None and len(d.measureTextColumn1) > 0:
                column_1 = d.measureTextColumn1
        if len(column_1) == 0:
            for d in entity.data_lfy:
                if d.measureTextColumn1 is not None and len(d.measureTextColumn1) > 0:
                    column_1 = d.measureTextColumn1

        for d in entity.data_cfy:
            if d.measureTextColumn2 is not None and len(d.measureTextColumn2) > 0:
                column_2 = d.measureTextColumn2
        if len(column_2) == 0:
            for d in entity.data_lfy:
                if d.measureTextColumn2 is not None and len(d.measureTextColumn2) > 0:
                    column_2 = d.measureTextColumn2

        self.report.set_xy(x + 1, h + 1)
        self.report.multi_cell(graph_size[0] / 2 - 2, h=2.5, txt=column_1, align='J')

        self.report.set_xy(x + graph_size[0] / 2, h)
        self.report.cell(graph_size[0] / 2, h=graph_size[1], border='L')

        self.report.set_xy(x + 1 + graph_size[0] / 2 + 4, h + 1)
        self.report.multi_cell(graph_size[0] / 2 - 2, h=2.5, txt=column_2, align='J')

    def __do_compose_effectiveness_and_compliance(self, x, h, options):
        graph_size = (185, 214)
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.report.image(options.images[OFSTED], x=x + 0.5, y=h + 0.5, w=graph_size[0] - 1, h=0)
        return h + graph_size[1]

    def __do_compose_corporate_risks(self, h, options):
        graph_size = (220, 183)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.report.image(options.images[RISK_MAP], x=8, y=h + 0.5, w=graph_size[0] - 1,
                          h=graph_size[1] - 1)
        return h + graph_size[1]

    def __do_compose_customer_relationships(self, h, options):
        graph_size = (220, 83)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        return h + graph_size[1]

    def __do_compose_financial_hr_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True, h=2.25, w=405)
        self.report.cell(330, h=8.5, txt=text.FINANCIAL_MANAGEMENT, fill=1, align='C', border=1)
        self.report.cell(75, h=8.5, txt=text.REPORTED_QUARTERLY_NO_UPDATE_RECEIVED, fill=1, align='C', border=1)
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
        h = self.__do_compose_health_and_safety(h, options)

        h = self.__create_scorecard_top(add_first=False, h=h)
        self.report.cell(220, h=8.5, txt=text.WORKFORCE_EXPENDITURE, fill=1, align='C', border=1)
        h += 8.5
        self.__reset_colors()
        h = self.__do_compose_workforce(h, options)

    def __do_compose_health_and_safety(self, h, options):
        graph_size = (220, 53)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        return h + graph_size[1]

    def __do_compose_workforce(self, h, options):
        graph_size = (220, 30)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.report.image(options.images[WORKFORCE_EXPENDITURE], x=8, y=h + 0.5, w=graph_size[0] - 1,
                          h=graph_size[1] - 1)
        return h + graph_size[1]

    def __do_compose_school_table(self, x, h, options):
        graph_size = (75, 83)
        self.report.set_xy(x, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        self.report.image(options.images[SCHOOLS_IN_DEFICIT], x=x + 0.5, y=h + 0.5, w=graph_size[0] - 1,
                          h=graph_size[1] / 2)

        entity = get_entity_by_m_id(options.entities, '10_05')
        comment = ''
        for d in entity.data_cfy:
            if d.reportComments is not None and len(d.reportComments) > 0:
                comment = d.reportComments
        if len(comment) == 0:
            for d in entity.data_lfy:
                if d.reportComments is not None and len(d.reportComments) > 0:
                    comment = d.reportComments

        self.report.set_xy(x + 0.5, h + graph_size[1] / 2 + 2)
        self.__set_font(size=6)
        self.report.multi_cell(graph_size[0] - 1, 2.5, txt=comment, align='J')

    def __do_compose_hr_workforce(self, h, options):
        graph_size = (405, 83)
        self.report.set_xy(7.5, h)
        self.report.cell(graph_size[0], h=graph_size[1], border=1)
        return h + graph_size[1]

    def __do_compose_financial_charts(self, h, options):
        graph_size = (110, 83)
        m_ids = ['9_08', '9_09', '9_10']
        titles = [text.COLLECTION_OF_COUNCIL_TAX_IN_YEAR, text.COLLECTION_OF_BUSINESS_RATES_IN_YEAR,
                  text.COUNCIL_TAX_PAID_BY_DIRECT_DEBIT]
        for m_id in m_ids:
            x = 7.5 + (graph_size[0] * m_ids.index(m_id))

            entity = get_entity_by_m_id(options.entities, m_id)

            self.report.set_xy(x, h)
            self.report.cell(graph_size[0], h=graph_size[1], border=1)
            self.report.set_xy(x + 0.5, h + 0.5)
            self.__compose_financial_chart(h, entity, titles[m_ids.index(m_id)], m_id)

            self.report.set_xy(x + 2.5, h + graph_size[1] / 2 - 5)
            self.__compose_report_comment(entity.data(), w=graph_size[0] - 5)

            self.__compose_financial_table(entity, x=x + graph_size[0] / 2 + 17, y=h + 3)

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
                dot = format_value(recent_data.dotFromSamePeriodLastYear)
            elif FREQ_QUARTER in frequency:
                dot = format_value(recent_data.dotFromPreviousQuarter)
            else:
                dot = format_value(recent_data.dotFromPreviousMonth)
            result = format_value(recent_data.result, d_format)
            target = format_value(recent_data.target, d_format)
            baseline = format_value(entity.get_measure(recent_data).baseline, d_format)

        text_dot = " "
        if ~(dot in ["p", "q", "r", "s", "u"]):
            text_dot = dot

        self.__set_font(is_bold=True, size=5)
        self.report.cell(14, 6, text.DOT, border='L', ln=0, align='C')
        self.__set_font(is_bold=False, size=5)
        self.report.cell(15, 6, text_dot, border='R', ln=2, align='C')
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

    def __compose_financial_chart(self, h, entity, title, m_id):
        fig, ax = plt.subplots(figsize=(7, 3))
        plt.title(title, fontsize=16, wrap=True)

        x_freq = self.__get_freq(entity.measure_cfy.frequency.upper())
        x_ticks, x_ticks_lbl, y_target = self.__get_ticks_and_target(x_freq, entity.data())
        y_target = [try_parse('{:.2f}'.format(x * 100), is_float=True) for x in y_target]
        ax.plot(x_ticks, y_target, "k--", color='darkblue', zorder=4)

        results = get_results_per_given_frequency(entity.data(), x_freq, x_ticks)
        results = [try_parse('{:.2f}'.format(x * 100), is_float=True) for x in results]
        performance = get_performance_per_given_frequency(entity.data(), x_freq, x_ticks)

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
        plt.savefig(f_path)
        self.report.image(f_path, x=None, y=None, w=69, h=0, type='', link='')

    def __do_compose_cpm_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True)

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
        self.report.image(options.images[LEGEND], x=None, y=None, w=139, h=59, type='', link='')

    def __compose_measure_summary(self, h, entities, is_cpm=True):
        if is_cpm:
            e_sorted = [e for e in entities if isinstance(e, CpmEntity)]
        else:
            e_sorted = [e for e in entities if isinstance(e, SdmEntity)]

        h += 1
        self.report.set_xy(9, h)
        self.report.set_font(REPORT_FONT, 'B', 6)
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
        self.report.set_font(REPORT_FONT, '', 6)
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
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_LEAN_WORK_INVEST))),
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
        h += 2
        for entity in entities:
            if not isinstance(entity, PmtAdditionalEntity):
                continue
            if entity.data_cfy[0].m_id == m_id:
                comment = ''
                for d in entity.data_cfy:
                    if d.measureTextColumn1 is not None and len(d.measureTextColumn1) > 0:
                        comment = d.measureTextColumn1
                if len(comment) == 0:
                    for d in entity.data_lfy:
                        if d.measureTextColumn1 is not None and len(d.measureTextColumn1) > 0:
                            comment = d.measureTextColumn1
                self.report.set_xy(121, h)
                self.report.set_font(REPORT_FONT, '', 6)
                self.report.multi_cell(150, h=2.5, txt=comment, align='J')
                break

    def __do_compose_grid_charts(self, entities=None, exclusions=None):
        graphs = 0
        coords = list(self.left_top)

        # compose grid charts for CPM measures
        for entity in entities:
            if not isinstance(entity, CpmEntity):
                continue
            # check if entity should be excluded from the report
            if exclusions is not None and entity.measure_cfy.m_id in exclusions:
                logging.debug('Ignoring entity [{}]'.format(entity.measure_lfy.m_id))
                continue
            # check if coords are equal to initial left-top
            # then create new page
            if graphs == 0:
                self.report.add_page()
            graphs += 1
            # create chart
            self.__compose_visuals_for_entity(entity, coords)

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
                                            w=self.graph_size[0] * self.grid_size[1])
        if graphs > 0:
            self.__create_scorecard_top(x=self.left_top[0], h=self.left_top[1] - 8.5, add_second=False,
                                        w=self.graph_size[0] * self.grid_size[1])
            self.__reset_colors()
            self.__set_grid(n_cells=graphs)

    def __reset_colors(self):
        color = get_color(WHITE)
        self.report.set_fill_color(color.r, color.g, color.b)
        color = get_color(BLACK)
        self.report.set_text_color(color.r, color.g, color.b)

    def __create_scorecard_top(self, add_page=False, h=98.0, add_first=True, add_second=True, w=405, x=7.5):
        self.report.set_font(REPORT_FONT, 'B', 8)
        if add_page:
            self.report.add_page()
        if add_first:
            self.report.set_xy(x, h)
            color = get_color(DARK_BLUE)
            self.report.set_fill_color(color.r, color.g, color.b)
            color = get_color(WHITE)
            self.report.set_text_color(color.r, color.g, color.b)
            # TODO get month and FY
            self.report.cell(w, h=8.5, txt=text.MONTHLY_PERFORMANCE_SCORECARD.format('April', 2020), fill=1, align='C')
            h += 8.5

        if add_second:
            self.report.set_xy(7.5, h)
            color = get_color(AQUA)
            self.report.set_fill_color(color.r, color.g, color.b)
            color = get_color(WHITE)
            self.report.set_text_color(color.r, color.g, color.b)

        return h

    def __do_compose_sdm_scorecard(self, options):
        h = self.__create_scorecard_top(add_page=True)

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
        self.report.set_font(REPORT_FONT, 'B', 8)
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

    def __add_empty_line(self):
        self.report.set_font(REPORT_FONT, '', 5.5)
        # self.report.cell(35, 5, '', ln=2, align='C')
        self.report.cell(0, 1, ' ', 0, 2, 'C')

    def __set_font(self, is_bold=False, size=5):
        if is_bold:
            self.report.set_font(REPORT_FONT, 'B', size)
        else:
            self.report.set_font(REPORT_FONT, '', size)

    def __compose_visuals_for_entity(self, entity, left_top):
        self.__reset_colors()
        self.report.set_xy(left_top[0], left_top[1])
        d_format = entity.measure_cfy.data_format
        frequency = entity.measure_cfy.frequency.upper()

        self.__compose_bar_chart(entity.measure_cfy, entity.data(), frequency, d_format)

        self.__add_empty_line()
        # TODO conclude how to get comments from last/current fiscal year
        self.__compose_report_comment(entity.data())

        self.report.set_xy(left_top[0] + 95, left_top[1] + 5)
        self.__compose_benchmark_tbl(entity.data(), d_format)

        self.__add_empty_line()
        self.__compose_current_pos_tbl(entity, frequency, d_format)

        self.__add_empty_line()
        self.__compose_gauge_chart(entity.data())

    def __compose_report_comment(self, data_list, w=93):
        r_comment = get_report_comment(data_list)
        self.report.set_font(REPORT_FONT, '', 5.5)
        self.report.multi_cell(w, 2.5, r_comment, 0, 'J')

    def __compose_benchmark_tbl(self, data_list, d_format):
        data_with_bmk_list = get_bmk(data_list)
        if len(data_with_bmk_list) == 0:
            nat_avg = text.NO_BENCHMARK
            b_at_bmk, quartile, bmk_y, bmk_g = '', '', '', ''
        else:
            recent_data = data_with_bmk_list[len(data_with_bmk_list) - 1]
            nat_avg = format_value(recent_data.benchmarkResult, d_format)
            b_at_bmk = format_value(recent_data.birmResultAtBenchmark, d_format)

            quartile = format_value(recent_data.birmQuartilePosition)
            if quartile is None:
                quartile = text.NOT_APPLICABLE
            quartile = quartile.upper()

            bmk_y = '{} {}'.format(text.BENCHMARK, format_value(recent_data.yearOfBenchmarkData))
            bmk_g = format_value(recent_data.benchmarkGroup)

        self.__set_font(is_bold=True, size=8)
        self.report.cell(37, 6, text.BENCHMARK, 1, 2, 'C')

        self.__set_font(size=7)
        self.report.cell(17, 6, text.PREFERRED_DOT, border='L', ln=0, align='C')
        self.report.cell(20, 6, ' ', border='R', ln=2, align='C')
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

    def __compose_current_pos_tbl(self, entity, frequency, d_format):
        data_current_pos_list = get_current_pos(entity.data())
        if len(data_current_pos_list) == 0:
            dot, result, target = '', '', ''
            fill_bool = False
            baseline = NOT_APPLICABLE
        else:
            recent_data = data_current_pos_list[len(data_current_pos_list) - 1]
            if FREQ_ANNUAL in frequency:
                dot = format_value(recent_data.dotFromSamePeriodLastYear)
            elif FREQ_QUARTER in frequency:
                dot = format_value(recent_data.dotFromPreviousQuarter)
            else:
                dot = format_value(recent_data.dotFromPreviousMonth)
            result = format_value(recent_data.result, d_format)
            target = format_value(recent_data.target, d_format)
            fill_bool = recent_data.status.upper() == text.PROVISIONAL
            baseline = format_value(entity.get_measure(recent_data).baseline, d_format)
        self.__set_font(is_bold=True, size=8)
        self.report.cell(37, 6, text.CURRENT_POSITION, 1, 2, 'C')
        self.__set_font(is_bold=False, size=7)

        self.report.cell(17, 6, text.DOT, border='L', ln=0, align='C')
        text_dot = " "
        if ~(dot in ["p", "q", "r", "s", "u"]):
            text_dot = dot
        self.report.cell(20, 6, text_dot, border='R', ln=2, align='C')
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
        data_qp_list = get_qp(data_list)
        if len(data_qp_list) == 0:
            return
        recent_data = data_qp_list[len(data_qp_list) - 1]
        self.__set_font(is_bold=True, size=8)
        self.report.cell(35, 6, text.QUARTILE_PROJECTION, 0, 2, 'C')
        self.__set_font(size=7)
        self.report.cell(35, 3, text.CURRENT_ACTUAL_AGAINST, 0, 2, 'C')
        self.report.cell(35, 3, text.NATIONAl_DATA_AVAILABLE, 0, 2, 'C')
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
                    'value': try_parse(recent_data.quartileProjection, is_float=True)}}))
        f_path = join(get_dir_path(TEMP), '{}_quartile_projection.png'.format(recent_data.m_id))
        g_chart.write_image(f_path)
        self.report.image(f_path, x=None, y=None, w=35, h=0, type='', link='')

    def __compose_bar_chart(self, measure, data_list, frequency, d_format):
        fig, ax = plt.subplots()
        if d_format.upper() == PERCENTAGE:
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        graph_title = '{} (ex. {})'.format(measure.m_title, measure.m_ref_no)
        plt.title(graph_title.replace('\r', '').replace('\n', ''), fontsize=12, wrap=True)

        x_freq = self.__get_freq(frequency)
        x_ticks, x_ticks_lbl, y_target = self.__get_ticks_and_target(x_freq, data_list)

        ax.plot(x_ticks, y_target, "k--", color='darkblue', zorder=4)
        baseline = try_parse(measure.baseline, is_float=True)
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

        f_path = join(get_dir_path(TEMP), '{}_bar_chart.png'.format(measure.m_id))
        plt.savefig(f_path)
        self.report.image(f_path, x=None, y=None, w=94, h=0, type='', link='')

    @staticmethod
    def __create_bar(ax, data, color, width=0.6):
        if len(data[0]) > 0:
            ax.bar(data[0], data[1], color=str(color), width=width, align='center')

    @staticmethod
    def __get_ticks_and_target(freq, data_list):
        if freq == FREQ_ANNUAL:
            x_ticks = sorted(set([try_parse(x.year, is_int=True) for x in data_list]))
            x_ticks_lbl = sorted(set([x.f_year for x in data_list]))

            y_target = get_target_per_given_frequency(data_list, freq, x_ticks)
        elif freq == FREQ_QUARTER:
            x_ticks = sorted(set([try_parse(x.yearQuarter, is_int=True) for x in data_list]))
            # create two list of quarters for last & current fiscal years
            x_ticks_lbl = sorted(set([x.quarter for x in data_list]))
            x_ticks_lbl = x_ticks_lbl + x_ticks_lbl

            y_target = get_target_per_given_frequency(data_list, freq, x_ticks)
        else:
            x_ticks = [try_parse(x.yearMonth, is_int=True) for x in data_list]
            # get month abbreviations
            x_ticks_lbl = dict()
            for x in data_list:
                m_dt = x.month.split(' - ')
                x_ticks_lbl[try_parse(m_dt[0].replace('M', ''), is_int=True)] = m_dt[1]
            # create 2 list of month abbreviations for last & current fiscal year
            x_ticks_lbl = list((x_ticks_lbl.values()))
            x_ticks_lbl = x_ticks_lbl + x_ticks_lbl

            y_target = get_target_per_given_frequency(data_list, freq, x_ticks)

        return [str(x) for x in x_ticks], x_ticks_lbl, y_target

    @staticmethod
    def __get_freq(freq):
        # if frequency is unknown, by default it is configured to monthly
        r_freq = FREQ_MONTHLY
        if freq in ['Q', 'QUARTER', 'QUARTERLY']:
            r_freq = FREQ_QUARTER
        elif freq in ['A', 'ANNUAL', 'ANNUALLY', 'YEAR', 'YEARLY', 'BI A', 'BI ANNUAL', 'BI_ANNUALLY']:
            r_freq = FREQ_ANNUAL
        return r_freq
