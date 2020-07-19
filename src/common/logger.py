import logging

from os import *
from os.path import *
from datetime import datetime

from common.constants import LOG
from common.utils import get_dir_path


def init_logger(debug=False):
    log_root = get_dir_path(LOG)
    now = datetime.now()
    timestamp = ('%04d%02d%02d%02d%02d%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second))
    if not exists(log_root):
        mkdir(log_root)
    else:
        file_dict = dict()
        log_files = [f for f in listdir(log_root) if isfile(join(log_root, f))]
        for lf in log_files:
            ts = int(lf.replace('RG_', '').replace('.log', ''))
            file_dict[ts] = lf
        keys = sorted(file_dict, reverse=True)
        if len(keys) > 9:
            i = 0
            for k in keys:
                if i >= 9:
                    remove(join(log_root, file_dict[k]))
                i += 1
    if debug:
        log_lvl = logging.DEBUG
    else:
        log_lvl = logging.INFO
    logging.basicConfig(
        level=log_lvl,
        format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s',
        handlers=[
            logging.FileHandler(join(log_root, 'RG_{}.log'.format(timestamp))),
            logging.StreamHandler()
        ]
    )