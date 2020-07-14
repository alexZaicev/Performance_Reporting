import logging
import re
from datetime import datetime
from os.path import dirname, abspath, join

from constants import *
from models.errors import RGError
from text import NOT_APPLICABLE, PERCENTAGE, NUMBER


def timestamp():
    now = datetime.now()
    return '{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)


def get_prev_fiscal_month(month=None, fm=None):
    if fm is None:
        FM = {
            1: 4,
            2: 5,
            3: 6,
            4: 7,
            5: 8,
            6: 9,
            7: 10,
            8: 11,
            9: 12,
            10: 1,
            11: 2,
            12: 3
        }
        if month is None:
            now = datetime.now()
            month = now.month - 1
        else:
            month -= 1
        if month == 0:
            month = 12
        # convert ordinary to fiscal month
        return FM[month]
    else:
        fm -= 1
        if fm == 0:
            fm = 12
        return fm


def get_dir_path(name=ROOT):
    base = dirname(abspath(__file__)).replace('\\src', '')
    DIR_PATH = {
        ROOT: base,
        RESOURCES: join(base, 'resources'),
        TEMP: join(base, 'tmp'),
        LOG: join(base, 'log'),
        TEMPLATES: join(base, 'templates'),
        OUTPUT: join(base, 'output')
    }
    try:
        return DIR_PATH[name]
    except KeyError:
        logging.error('Unknown directory type [{}]'.format(name))
    return None


def get_font(name=DEJAVU_SANS):
    if name is not None and len(name) > 0:
        return join(get_dir_path(RESOURCES), 'fonts', '{}.ttf'.format(name))
    return None


def get_color(name=BLACK):
    from models.utilities import RGColor
    COLOR_MAP = {
        WHITE: RGColor(255, 255, 255),
        BLACK: RGColor(),
        RED: RGColor(r=255),
        AMBER: RGColor(255, 153, 51),
        GREEN: RGColor(g=255),
        BLUE: RGColor(g=128, b=255),
        GREY: RGColor(r=128, g=128, b=128),
        DARK_BLUE: RGColor(r=31, g=73, b=125),
        AQUA: RGColor(r=83, g=141, b=213),
        LIGHT_AQUA: RGColor(220, 230, 241)
    }
    try:
        return COLOR_MAP[name]
    except KeyError:
        logging.error('Unknown color name [{}]'.format(name))
    return None


def try_parse(val, is_int=False, is_float=False):
    if not is_int and not is_float:
        return None
    try:
        val = str(val)
        if is_int:
            return int(val)
        elif is_float:
            return float(val)
    except ValueError:
        return None


def get_cfy():
    """
    Function to get current fiscal year
    :return: Fiscal year (int)
    """
    now = datetime.now()
    if now.month >= 4:
        return now.year
    else:
        return now.year - 1


def get_cfy_prefix(cfy=None):
    if cfy is None:
        cfy = get_cfy()
    return '%04d-%s' % (cfy, str(cfy + 1)[2:])


def get_lfy_prefix(cfy=None):
    if cfy is None:
        cfy = get_cfy()
    return '%04d-%s' % (cfy - 1, str(cfy)[2:])


def parse_columns(column):
    val = str(column).upper().replace('\n', ' ').replace('\r', ' ').replace('\\', ' ').replace('/', ' ').replace(
        '-', ' ').replace('(', ' ').replace(')', ' ').replace(',', ' ')
    val = re.sub(' +', '_', val)
    if val.endswith('_'):
        val = val[:-1]
    if val.startswith('_'):
        val = val[1:]
    val = val.replace('&', 'AND')
    return val


def get_val(df, key):
    try:
        val = df[key]
        if val is None or (str(val) == 'nan'):
            return ''
        else:
            if isinstance(val, str):
                try:
                    temp = parse_unicode_str(val).encode(encoding='utf-8')
                    val = temp.decode(encoding=REPORT_ENCODING, errors='strict')
                except UnicodeEncodeError:
                    logging.error('Failed to encode UTF-8 to {} [{}]'.format(REPORT_ENCODING, val))
                except UnicodeDecodeError:
                    logging.error('Failed to decode to {} [{}]'.format(REPORT_ENCODING, val))
            return val
    except KeyError:
        logging.debug('Data frame does not contain the following key value [{}]'.format(key))
    return None


def parse_unicode_str(val):
    val = val.replace('\u0028', '\u007b').replace('\u0029', '\u007d')
    if REPORT_ENCODING.lower() == 'utf-8':
        return val
    return val \
        .replace('\u2018', '\u0027').replace('\u2019', '\u0027') \
        .replace('\u201a', '\u0027').replace('\u201b', '\u0027') \
        .replace('\u201c', '\u0022').replace('\u201d', '\u0022') \
        .replace('\u201e', '\u0022').replace('\u201F', '\u0022') \
        .replace('\u25b2', '\u005e').replace('\u25bc', '\u005e') \
        .replace('\u25bc', '\u0021\u005e').replace('\u25bd', '\u0021\u005e') \
        .replace('\u2015', '\u002d').replace('\u2014', '\u002d').replace('\u2013', '\u002d')


def get_report_comment(data_list):
    if data_list is not None:
        for data in data_list:
            if data.reportComments is not None and len(data.reportComments) > 0:
                return data.reportComments
    return ''


def get_bmk(data_list):
    result = list()
    if data_list is not None:
        for data in data_list:
            if data.benchmarkResult is not None and not isinstance(data.benchmarkResult, str):
                result.append(data)
    return result


def format_value(val, d_format=None):
    if NAN is str(val).lower():
        val = NOT_APPLICABLE
    elif try_parse(val, is_int=True) is None and try_parse(val, is_float=True) is None:
        if len(val) > MAX_FORMATTED_VALUE_SIZE:
            val = '{}..'.format(val[:MAX_FORMATTED_VALUE_SIZE - 3])
    elif d_format.upper() == PERCENTAGE.upper():
        if isinstance(val, str):
            tmp = try_parse(val, is_float=True)
            if tmp is None:
                logging.error('Failed to format non floating point string value [{}]'.format(val))
                return None
            else:
                val = tmp
        val = '%.2f' % (val * 100) + '%'
    elif d_format.upper() == NUMBER.upper():
        if isinstance(val, str):
            tmp = try_parse(val, is_float=True)
            if tmp is None:
                logging.error('Failed to format non floating point string value [{}]'.format(val))
                return None
            else:
                val = tmp
        val = '%.2f' % val
    return str(val)


def get_current_pos(data_list):
    result = list()
    if data_list is not None:
        for data in data_list:
            if data.result is not None and not isinstance(data.result, str):
                result.append(data)
    return result


def get_qp(data_list):
    result = list()
    if data_list is not None:
        for data in data_list:
            if try_parse(data.quartileProjection) is not None:
                result.append(data)
    return result


def get_target_per_given_frequency(data_list, frequency, freq_num):
    result = list()
    if data_list is not None and freq_num is not None and frequency is not None:
        for fn in freq_num:
            d_fn = list()
            for data in data_list:
                if (frequency == FREQ_ANNUAL and data.year == str(fn)) or \
                        (frequency == FREQ_QUARTER and data.yearQuarter == str(fn)) or \
                        (frequency == FREQ_MONTHLY and data.yearMonth == str(fn)):
                    d_fn.append(data)
            d_fn = [x for x in d_fn if try_parse(x.target, is_float=True) is not None]
            if len(d_fn) == 0:
                result.append(0)
            else:
                result.append(d_fn[len(d_fn) - 1].target)
    return result


def get_results_per_given_frequency(data_list, frequency, freq_num):
    result = list()
    if data_list is not None and freq_num is not None and frequency is not None:
        for fn in freq_num:
            d_fn = list()
            for data in data_list:
                if (frequency == FREQ_ANNUAL and data.year == fn) or \
                        (frequency == FREQ_QUARTER and data.yearQuarter == fn) or \
                        (frequency == FREQ_MONTHLY and data.yearMonth == fn):
                    d_fn.append(data)
            d_fn = [x for x in d_fn if try_parse(x.result, is_float=True) is not None]
            if len(d_fn) == 0:
                result.append(0)
            else:
                result.append(d_fn[len(d_fn) - 1].result)
    return result


def get_performance_per_given_frequency(data_list, frequency, freq_num):
    result = list()
    if data_list is not None and freq_num is not None and frequency is not None:
        for fn in freq_num:
            d_fn = list()
            for data in data_list:
                if (frequency == FREQ_ANNUAL and data.year == fn) or \
                        (frequency == FREQ_QUARTER and data.yearQuarter == fn) or \
                        (frequency == FREQ_MONTHLY and data.yearMonth == fn):
                    d_fn.append(data)
            d_fn = [x for x in d_fn if try_parse(x.result, is_float=True) is not None]
            if len(d_fn) == 0:
                result.append(None)
            else:
                result.append(d_fn[len(d_fn) - 1].performance.upper())
    return result


def check_performance_color(p_list, color):
    if p_list is not None:
        for p in p_list:
            if color in str(p).upper():
                return True
    return False


def sort_results_and_months_by_performance(r_list, freq_num, p_list, value):
    months = list()
    results = list()
    if r_list is not None and freq_num is not None and p_list is not None:
        for i in range(0, len(p_list), 1):
            if value is None:
                if BLUE not in str(p_list[i]).upper() and \
                        GREEN not in str(p_list[i]).upper() and \
                        AMBER not in str(p_list[i]).upper() and \
                        RED not in str(p_list[i]).upper() and \
                        GREY not in str(p_list[i]).upper():
                    if r_list[i] is not None:
                        months.append(freq_num[i])
                        results.append(r_list[i])
            else:
                if value in str(p_list[i]).upper():
                    if r_list[i] is not None:
                        months.append(freq_num[i])
                        results.append(r_list[i])
    return months, results


def sort_entities_by_performance(entities, performance, exclusions=()):
    def __get_data(data_list):
        for i in range(len(data_list) - 1, 0, -1):
            if data_list[i].performance is None:
                continue
            dp = data_list[i].performance.upper().replace(' ', '_')
            if dp == performance:
                return data_list[i]
        return None

    result = list()
    if entities is not None and performance is not None:
        for e in entities:
            if e.measure_cfy.m_id in exclusions or e.measure_lfy.m_id in exclusions:
                continue
            r_data = __get_data(e.data_cfy)
            if r_data is None:
                r_data = __get_data(e.data_lfy)

            if r_data is not None:
                result.append(e)
    return result


def sort_entities_by_outcome(entities, outcome):
    result = list()
    if entities is not None and outcome is not None:
        for e in entities:
            if isinstance(e.measure_cfy.outcome, str) and outcome in e.measure_cfy.outcome:
                result.append(e)
    return result


def remove_entities_with_no_outcome(entities):
    result = list()
    if entities is not None:
        for e in entities:
            if e.measure_cfy.outcome is not None and len(e.measure_cfy.outcome) > 0:
                result.append(e)
    return result


def get_entity_by_m_id(entities, m_id, has_measure=True):
    if entities is None and m_id is None:
        return None
    for e in entities:
        if has_measure and e.measure_cfy.m_id == m_id and e.measure_lfy.m_id == m_id:
            return e
        elif not has_measure and e.data_cfy[0].m_id == m_id and e.data_cfy[1].m_id == m_id:
            return e
    return None


def get_variance_and_dot(a, b):
    variance = b - a
    if variance > 0:
        dot = '\u25b2'
    elif variance < 0:
        dot = '\u25bd'
    else:
        dot = '\u25b6'
    return variance, dot


def get_data_by_m_id_and_date(entities, m_id, fym):
    if entities is not None and m_id is not None:
        e = None
        for entity in entities:
            if len(entity.data()) > 0 and entity.data()[0].m_id == m_id:
                e = entity
        if e is None:
            return None
        for d in e.data():
            if str(d.yearMonth) == str(fym):
                return d
    return None


def get_fiscal_month_id(s_month):
    if s_month is None or s_month.upper() not in list(FISCAL_MONTHS.values()):
        raise RGError('Unknown fiscal month provided [{}]'.format(s_month))
    for k, v in FISCAL_MONTHS.items():
        if v == s_month.upper():
            return k
    raise RGError(
        'Provided fiscal month [{}] cannot be parsed. Please double check the correctness of the 3-character '
        'month name'.format(s_month))


def filter_data_by_fym(data, fym):
    result = list()
    if data is not None and fym is not None:
        for d in data:
            stamp = try_parse(d.yearMonth, is_int=True)
            if stamp is not None and fym >= stamp:
                result.append(d)
    return result


def get_data_by_date(data, fym):
    result = list()
    if data is not None and fym is not None:
        for d in data:
            if str(d.yearMonth) == str(fym):
                result.append(d)
    return result


def get_text_dot(dot):
    if dot is not None:
        if ~(dot in ["p", "q", "r", "s", "u"]):
            return dot
    return ''


def get_prev_and_current_month_data(options, m_id):
    d_prev, d_current = None, None
    # set current & previous fiscal months IDs
    m_current = try_parse(str(options.fym)[-2:], is_int=True)
    m_previous = get_prev_fiscal_month(fm=m_current)
    # get entity by measure ID
    entity = get_entity_by_m_id(options.entities, m_id, has_measure=False)
    if entity is not None:
        d_prev = get_data_by_date(entity.data(), '{}{:02d}'.format(str(options.fym)[:6], m_previous))
        d_current = get_data_by_date(entity.data(), options.fym)
        if d_prev is not None and len(d_prev) > 0:
            d_prev = d_prev[0]
        else:
            # TODO handle data that was not found
            pass
        if d_current is not None and len(d_current) > 0:
            d_current = d_current[0]
        else:
            # TODO handle data that was not found
            pass
    return d_prev, d_current
