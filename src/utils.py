import re
from datetime import datetime


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


def get_cfy_prefix():
    cfy = get_cfy()
    return '%04d-%s' % (cfy, str(cfy + 1)[2:])


def get_lfy_prefix():
    cfy = get_cfy()
    return '%04d-%s' % (cfy - 1, str(cfy)[2:])


def parse_columns(column):
    val = str(column).upper().replace('\n', ' ').replace('\r', ' ').replace('\\', ' ').replace('/', ' ').replace(
        '-', ' ').replace('(', ' ').replace(')', ' ')
    val = re.sub(' +', '_', val)
    if val.endswith('_'):
        val = val[:-1]
    if val.startswith('_'):
        val = val[1:]
    return val

def get_val(df, key):
    val = df[key]
    if val is None or (str(val) == 'nan'):
        return ''
    else:
        return val