from threading import Thread

from common.logger import set_level
from common.models.errors import RGError, RGTemplateNotFoundError
from common.models.utilities import RGConfig, RGReporterOptions
from common.text import TEMPLATES_FOR_CURRENT_AND_LAST_FISCAL_YEARS_NOT_FOUND
from common.utility_base import RGUtilityBase
from common.utils import get_cfy_prefix, try_parse, get_lfy_prefix
from reporter_tool.dao.excel_template_dao import ExcelTemplateDao
from reporter_tool.dao.file_dao import ImageFileDao
from reporter_tool.reporters.pdf_reporter import PDFReporter


class RGToolManager(RGUtilityBase):

    @staticmethod
    def execute(config, window, loader):
        if config is None or not isinstance(config, RGConfig):
            raise RGError('RGConfig expected, actual [{}]'.format(type(config)))
        thread = RGToolThread(config=config, window=window, loader=loader)
        thread.start()

    @staticmethod
    def parse_config_to_options(config):
        return RGReporterOptions(
            out_dir=config.out_dir,
            orca_path=config.orca_path,
            exclusions=[x.m_id for x in config.measure_entries],
            entities=RGToolManager.__get_entities(config),
            images=RGToolManager.__get_image_files(config),
            fym=try_parse('{}{:02d}'.format(get_cfy_prefix(cfy=config.f_year).replace('-', ''), config.f_month),
                          is_int=True
                          )
        )

    @staticmethod
    def __get_entities(config):
        return ExcelTemplateDao(year=config.f_year, month=config.f_month, path=config.template_dir).get_entities()

    @staticmethod
    def __get_image_files(config):
        return ImageFileDao(year=config.f_year, month=config.f_month, path=config.template_dir).get_files()


class RGToolThread(Thread):

    def __init__(self, config, window, loader, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.config = config
        self.window = window
        self.loader = loader

    def run(self):
        try:
            set_level(debug=self.config.debug_mode)
            # convert configuration to report options
            options = RGToolManager.parse_config_to_options(self.config)
            # generate report
            report_name = PDFReporter(options=options).generate()
            self.window.show_generation_completed_dialog(report_name)
        except RGTemplateNotFoundError:
            cfy = get_cfy_prefix(cfy=self.config.f_year)
            lfy = get_lfy_prefix(cfy=self.config.f_year)
            self.window.show_error_dialog(
                message=TEMPLATES_FOR_CURRENT_AND_LAST_FISCAL_YEARS_NOT_FOUND.format(cfy, lfy))
        except RGError as ex:
            self.window.show_error_dialog(message=str(ex))
        finally:
            # update UI
            self.loader.dismiss()
            self.window.release_ui()
