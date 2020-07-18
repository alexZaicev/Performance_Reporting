import logging
from argparse import ArgumentParser
from datetime import datetime

from common.logger import init_logger
from common.constants import TEMPLATES, OUTPUT
from reporter_tool.dao.excel_template_dao import ExcelTemplateDao
from reporter_tool.dao.file_dao import ImageFileDao
from common.models.errors import RGError
from common.models.utilities import RGReporterOptions
from reporter_tool.reporters.pdf_reporter import PDFReporter

from common.utils import get_dir_path, get_prev_fiscal_month, get_fiscal_month_id, get_cfy_prefix, try_parse


def __main(arg0=None):
    fm_id = get_fiscal_month_id(arg0.month)
    dao = ExcelTemplateDao(year=arg0.year, month=fm_id, path=arg0.templates_root)
    f_dao = ImageFileDao(year=arg0.year, month=fm_id, path=arg0.templates_root)
    reporter = PDFReporter()
    try:
        options = RGReporterOptions(entities=dao.get_entities(),
                                    exclusions=arg0.exclusions,
                                    out_dir=arg0.out_dir,
                                    images=f_dao.get_files(),
                                    fym=try_parse(
                                        '{}{:02d}'.format(get_cfy_prefix(cfy=arg0.year).replace('-', ''), fm_id),
                                        is_int=True)
                                    )
        reporter.generate(options)
    except RGError as ex:
        logging.error(str(ex))


def __arg_parser():
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='Enable debug logging',
                        dest='debug')
    parser.add_argument('-y', '--year', default=datetime.now().year, action='store', type=int,
                        help='Current fiscal year of the report to be generated (valid integer in YYYY format). '
                             'Default value is current fiscal year.',
                        dest='year')
    parser.add_argument('-m', '--month', default=get_prev_fiscal_month(), action='store', type=str,
                        help='Current month of the report to be generated (valid 3-character string in MMM format). '
                             'Default value is current date previous month.',
                        dest='month')
    parser.add_argument('-p', '--path', default=get_dir_path(TEMPLATES), action='store', type=str,
                        help='Base directory of report templates', dest='templates_root')
    parser.add_argument('-e', '--exclusions', default=list(), action='store', type=list,
                        help='List of measure IDs to be excluded from the report', dest='exclusions')
    parser.add_argument('-o', '--output', default=get_dir_path(OUTPUT), action='store', type=str,
                        help='Report output directory', dest='out_dir')
    return parser.parse_args()


if __name__ == '__main__':
    args = __arg_parser()
    init_logger(args.debug)
    logging.info('PDF report generating tool')
    __main(args)
