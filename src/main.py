from argparse import ArgumentParser
from os import listdir, mkdir, remove
from os.path import isfile, join, exists, dirname, abspath

from dao import ExcelTemplateDao
from models import *
from reporter import PDFReporter

ROOT_DIR = dirname(abspath(__file__)).replace('\\src', '')


def __main(arg0=None):
    dao = ExcelTemplateDao(year=arg0.fiscal_year, path=arg0.templates_root)
    reporter = PDFReporter()
    try:
        reporter.generate(entities=dao.get_entities(), exclusions=arg0.exclusions, out_dir=arg0.out_dir)
    except RGError as ex:
        logging.error(str(ex))


def __init_logger(debug=False):
    log_root = join(ROOT_DIR, 'log')
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


def __arg_parser():
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='enable debug logging',
                        dest='debug')
    parser.add_argument('-y', '--year', default=datetime.now().year, action='store', type=int,
                        help='fiscal year of the report templates', dest='fiscal_year')
    parser.add_argument('-p', '--path', default=join(ROOT_DIR, 'templates'), action='store', type=str,
                        help='base directory of report templates', dest='templates_root')
    parser.add_argument('-e', '--exclusions', default=list(), action='store', type=list,
                        help='list of measure IDs to be excluded from the report', dest='exclusions')
    parser.add_argument('-o', '--output', default=join(ROOT_DIR, 'output'), action='store', type=str,
                        help='report output directory', dest='out_dir')
    return parser.parse_args()


if __name__ == '__main__':
    args = __arg_parser()
    __init_logger(args.debug)
    logging.info('PDF report generating tool')
    logging.info('Initializing...')
    __main(args)
