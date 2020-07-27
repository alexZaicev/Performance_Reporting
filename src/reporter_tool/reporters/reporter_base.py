import logging
import os
import shutil
from abc import ABC, abstractmethod

from common.constants import REPORT_NAME, TEMP
from common.models.errors import RGError
from common.models.utilities import RGReporterOptions
from common.utils import get_dir_path


class RGReporterBase(ABC):
    """
    RG reporter base class
    """

    def __init__(self, options):
        ABC.__init__(self)
        self.options = options
        self.report = None
        self.report_name = REPORT_NAME

    def do_init(self):
        # TODO resolve issue with temp directory failing to delete
        tmp_dir = get_dir_path(TEMP)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)

    def generate(self):
        if self.options is None or not isinstance(self.options, RGReporterOptions):
            raise RGError('Invalid report options provided')
        logging.info('Generating report...')
        self.do_init()
        self.do_compose(options=self.options)
        self.do_prepare_export(out_dir=self.options.out_dir)
        self.do_export(out_dir=self.options.out_dir)
        self.do_clean()
        logging.info('Report successfully generated! [{}]'.format(self.report_name))

    @abstractmethod
    def do_compose(self, options=None):
        if self.report is None:
            raise RGError('PDF document has not been initialized')
        if options.entities is None or len(options.entities) < 1:
            raise RGError('No measures provided to PDF report generator')

    def do_prepare_export(self, out_dir=None):
        if self.report is None:
            raise RGError('Report document has not been initialized')
        if out_dir is None:
            raise RGError('Invalid report output directory provided [{}]'.format(out_dir))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    @abstractmethod
    def do_export(self, out_dir=None):
        with open(os.path.join(out_dir, self.report_name), 'w') as ff:
            ff.write(self.report)

    @staticmethod
    def do_clean():
        tmp_dir = get_dir_path(TEMP)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
