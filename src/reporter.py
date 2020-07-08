import os

import matplotlib.pyplot as plt
from fpdf import FPDF
from matplotlib.ticker import PercentFormatter
from plotly import graph_objects

import report_text as rt
from models import RGReporterBase, CpmEntity, UnknownEntity
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

    def do_compose(self, options=None):
        self.do_compose_cpm_scorecard(options)
        self.do_compose_grid_charts(entities=options.entities, exclusions=options.exclusions)

    def do_compose_cpm_scorecard(self, options):
        self.report.add_page()
        h = 98
        self.report.set_xy(7.5, h)
        self.report.set_font(REPORT_FONT, '', 6)
        # set grid
        # TODO get month and FY
        color = get_color(DARK_BLUE)
        self.report.set_fill_color(color.r, color.g, color.b)
        color = get_color(WHITE)
        self.report.set_text_color(color.r, color.g, color.b)
        self.report.set_font(REPORT_FONT, 'B', 8)
        self.report.cell(405, h=8.5, txt=rt.MONTHLY_PERFORMANCE_SCORECARD.format('April', 2020), fill=1, align='C')

        h += 8.5
        self.report.set_xy(7.5, h)
        color = get_color(AQUA)
        self.report.set_fill_color(color.r, color.g, color.b)
        color = get_color(WHITE)
        self.report.set_text_color(color.r, color.g, color.b)

        self.report.cell(112, h=8.5, txt=rt.COUNCIL_PLANS_MEASURE_SUMMARY, fill=1, align='C', border=1)
        self.report.cell(153, h=8.5, txt=rt.KEY_RESULTS_ACTIONS, fill=1, align='C', border=1)
        self.report.cell(140, h=8.5, txt=rt.KEY, fill=1, align='C', border=1)

        color = get_color(WHITE)
        self.report.set_fill_color(color.r, color.g, color.b)
        color = get_color(BLACK)
        self.report.set_text_color(color.r, color.g, color.b)

        h += 8.5
        self.report.set_xy(7.5, h)
        self.report.cell(112, h=60, border=1)
        self.report.cell(153, h=60, border=1)
        self.report.cell(140, h=60, border=1)

        self.__compose_measure_summary(h, options.entities)
        self.__compose_key_results_actions(h, options.entities)

        self.report.set_xy(273, h + 0.5)
        self.report.image(options.images[LEGEND], x=None, y=None, w=139, h=59, type='', link='')

    def __compose_measure_summary(self, h, entities):
        e_cpm = [e for e in entities if isinstance(e, CpmEntity)]
        h += 1
        self.report.set_xy(9, h)
        self.report.set_font(REPORT_FONT, 'B', 6)
        self.report.cell(35, 6, '{}:'.format(rt.TOTAL_MEASURES), align='L')
        n_cpm = len(e_cpm)
        self.report.cell(20, 6, '{}'.format(n_cpm), align='L')

        b_cpm = sort_entities_by_performance(e_cpm, PERF_BLUE)
        exc = [x.measure_cfy.m_id for x in b_cpm]
        g_cpm = sort_entities_by_performance(e_cpm, PERF_GREEN, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in g_cpm]
        r_cpm = sort_entities_by_performance(e_cpm, PERF_RED, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in r_cpm]
        a_cpm = sort_entities_by_performance(e_cpm, PERF_AMBER, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in a_cpm]
        nyd_cpm = sort_entities_by_performance(e_cpm, PERF_NYD, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in nyd_cpm]
        pr_cpm = sort_entities_by_performance(e_cpm, PERF_PREV_REPORTED, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in pr_cpm]
        aw_cpm = sort_entities_by_performance(e_cpm, PERF_AWAITING, exclusions=exc)
        exc = exc + [x.measure_cfy.m_id for x in aw_cpm]
        t_cpm = sort_entities_by_performance(e_cpm, PERF_TREND, exclusions=exc)
        h += 3
        self.report.set_xy(15, h)
        self.report.cell(35, 6, '{}:'.format(rt.AVAILABLE_TO_REPORT), align='L')
        m_sum = len(b_cpm) + len(g_cpm) + len(r_cpm) + len(a_cpm) + len(t_cpm)
        self.report.cell(50, 6, rt.INCLUDING_TREND_OR_PROJECT_UPDATE_MEASURES.format(m_sum, len(t_cpm)), align='L')

        h += 6
        self.report.set_xy(7.5, h)
        for i in range(0, 7, 1):
            self.report.cell(16, h=8, border=1)

        h += 2
        self.report.set_xy(23.5, h)
        self.report.multi_cell(16, h=2.5, txt=rt.LEAN_WORK_INVEST, align='C')
        self.report.multi_cell(16, h=2.5, txt=rt.GROW_UP, align='C')
        self.report.multi_cell(16, h=2.5, txt=rt.AGE_WELL, align='C')
        self.report.multi_cell(16, h=2.5, txt=rt.LIVE_IN, align='C')
        self.report.multi_cell(16, h=2.5, txt=rt.CWG, align='C')
        self.report.multi_cell(16, h=2.5, txt=rt.TOTAL, align='C')

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
                self.__compose_measure_summary_row(rt.BLUE, b_cpm, get_color(BLUE))
            elif i == 1:
                self.__compose_measure_summary_row(rt.GREEN, g_cpm, get_color(GREEN))
            elif i == 2:
                self.__compose_measure_summary_row(rt.AMBER, a_cpm, get_color(AMBER))
            elif i == 3:
                self.__compose_measure_summary_row(rt.RED, r_cpm, get_color(RED))
            elif i == 4:
                self.__compose_measure_summary_row(rt.TREND, t_cpm, get_color(GREY))
            elif i == 5:
                self.__compose_measure_summary_row(rt.NYD, nyd_cpm)
            elif i == 6:
                self.__compose_measure_summary_row(rt.AWAITING, aw_cpm)
            elif i == 7:
                self.__compose_measure_summary_row(rt.PREVIOUSLY_REPORTED, pr_cpm)
            h += 5

    def __compose_measure_summary_row(self, txt='', entities=(), color=get_color(BLACK)):
        self.report.set_text_color(color.r, color.g, color.b)
        if txt == rt.PREVIOUSLY_REPORTED:
            self.report.multi_cell(16, h=3, txt=txt, align='L')
        else:
            self.report.multi_cell(16, h=5, txt=txt, align='L')
        color = get_color(BLACK)
        self.report.set_text_color(color.r, color.g, color.b)
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_LEAN_WORK_INVEST))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_GROW_UP))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_AGE_WELL))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_LIVE_IN))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(sort_entities_by_outcome(entities, OUTCOME_CWG))), align='C')
        self.report.cell(16, h=6, txt='{}'.format(len(entities)), align='C')

    def __compose_key_results_actions(self, h, entities):
        h += 2
        for entity in entities:
            if not isinstance(entity, UnknownEntity):
                continue
            if entity.data_cfy[0].m_id == 'PMT_01':
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

    def do_compose_grid_charts(self, entities=None, exclusions=None):
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
            graphs += 1
            # check if coords are equal to initial left-top
            # then create new page
            if coords[0] == self.left_top[0] and coords[1] == self.left_top[1]:
                self.report.add_page()

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
        self.__set_grid(n_cells=graphs)

    def do_export(self, out_dir=None):
        self.report.output(name=os.path.join(out_dir, '{}_{}.{}'.format(self.report_name, timestamp(), EXT_PDF)),
                           dest='F')

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

    def __compose_report_comment(self, data_list):
        r_comment = get_report_comment(data_list)
        self.report.multi_cell(93, 2.5, r_comment, 0, 'J')

    def __compose_benchmark_tbl(self, data_list, d_format):
        data_with_bmk_list = get_bmk(data_list)
        if len(data_with_bmk_list) == 0:
            nat_avg = rt.NO_BENCHMARK
            b_at_bmk, quartile, bmk_y, bmk_g = '', '', '', ''
        else:
            recent_data = data_with_bmk_list[len(data_with_bmk_list) - 1]
            nat_avg = format_value(recent_data.benchmarkResult, d_format)
            b_at_bmk = format_value(recent_data.birmResultAtBenchmark, d_format)

            quartile = format_value(recent_data.birmQuartilePosition)
            if quartile is None:
                quartile = rt.NOT_APPLICABLE
            quartile = quartile.upper()

            bmk_y = '{} {}'.format(rt.BENCHMARK, format_value(recent_data.yearOfBenchmarkData))
            bmk_g = format_value(recent_data.benchmarkGroup)

        self.__set_font(is_bold=True, size=8)
        self.report.cell(37, 6, rt.BENCHMARK, 1, 2, 'C')

        self.__set_font(size=7)
        self.report.cell(17, 6, rt.PREFERRED_DOT, border='L', ln=0, align='C')
        self.report.cell(20, 6, ' ', border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, rt.NATIONAL_AVERAGE, border='L', ln=0, align='C')
        self.report.cell(20, 6, nat_avg, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, rt.BIRMINGHAM, border='L', ln=0, align='C')
        self.report.cell(20, 6, b_at_bmk, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, rt.QUARTILE, border='L', ln=0, align='C')
        if rt.FOURTH in quartile:
            color = get_color(RED)
        elif rt.THIRD in quartile:
            color = get_color(AMBER)
        elif rt.SECOND in quartile:
            color = get_color(GREEN)
        elif rt.FIRST in quartile:
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
            fill_bool = recent_data.status.upper() == rt.PROVISIONAL
            baseline = format_value(entity.get_measure(recent_data).baseline, d_format)
        self.__set_font(is_bold=True, size=8)
        self.report.cell(37, 6, rt.CURRENT_POSITION, 1, 2, 'C')
        self.__set_font(is_bold=False, size=7)

        self.report.cell(17, 6, rt.DOT, border='L', ln=0, align='C')
        text_dot = " "
        if ~(dot in ["p", "q", "r", "s", "u"]):
            text_dot = dot
        self.report.cell(20, 6, text_dot, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.set_fill_color(r=255, g=255, b=0)
        self.report.cell(17, 6, rt.ACTUAL, border='L', ln=0, align='C')
        self.report.cell(20, 6, result, border='R', ln=2, align='C', fill=fill_bool)
        self.report.cell(-17)

        self.report.cell(17, 6, rt.TARGET, border='L', ln=0, align='C')
        self.report.cell(20, 6, target, border='R', ln=2, align='C')
        self.report.cell(-17)

        self.report.cell(17, 6, rt.BASELINE, border='LB', ln=0, align='C')
        self.report.cell(20, 6, baseline, border='RB', ln=2, align='C')
        self.report.cell(-17)

    def __compose_gauge_chart(self, data_list):
        data_qp_list = get_qp(data_list)
        if len(data_qp_list) == 0:
            return
        recent_data = data_qp_list[len(data_qp_list) - 1]
        self.__set_font(is_bold=True, size=8)
        self.report.cell(35, 6, rt.QUARTILE_PROJECTION, 0, 2, 'C')
        self.__set_font(size=7)
        self.report.cell(35, 3, rt.CURRENT_ACTUAL_AGAINST, 0, 2, 'C')
        self.report.cell(35, 3, rt.NATIONAl_DATA_AVAILABLE, 0, 2, 'C')
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

        b_width = 0.6

        if len(blue_data[0]) > 0:
            ax.bar(blue_data[0], blue_data[1], color=str(get_color(BLUE)), width=b_width, align='center')
        if len(green_data[0]) > 0:
            ax.bar(green_data[0], green_data[1], color=str(get_color(GREEN)), width=b_width, align='center')
        if len(amber_data[0]) > 0:
            ax.bar(amber_data[0], amber_data[1], color=str(get_color(AMBER)), width=b_width, align='center')
        if len(red_data[0]) > 0:
            ax.bar(red_data[0], red_data[1], color=str(get_color(RED)), width=b_width, align='center')
        if len(grey_data[0]) > 0:
            ax.bar(grey_data[0], grey_data[1], color=str(get_color(GREY)), width=b_width, align='center')
        if len(brag_grey_data[0]) > 0:
            ax.bar(brag_grey_data[0], brag_grey_data[1], color=str(get_color(GREY)), width=b_width, align='center')

        ax.set_xticks(x_ticks)
        if x_freq == FREQ_MONTHLY:
            ax.set_xticklabels(x_ticks_lbl, rotation=45, ha='right')
        else:
            ax.set_xticklabels(x_ticks_lbl, rotation='horizontal')

        f_path = join(get_dir_path(TEMP), '{}_bar_chart.png'.format(measure.m_id))
        plt.savefig(f_path)
        self.report.image(f_path, x=None, y=None, w=94, h=0, type='', link='')

    @staticmethod
    def __get_ticks_and_target(freq, data_list):
        x_ticks, x_ticks_lbl, y_target = None, None, None

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
