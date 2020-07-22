from common.logger import set_level
from common.models.errors import RGError, RGUIError
from common.models.utilities import RGConfig, RGReporterOptions
from common.utility_base import RGUtilityBase
from common.utils import get_cfy_prefix, try_parse
from reporter_tool.dao.excel_template_dao import ExcelTemplateDao
from reporter_tool.dao.file_dao import ImageFileDao
from reporter_tool.reporters.pdf_reporter import PDFReporter


class RGToolManager(RGUtilityBase):

    @staticmethod
    def execute(config):
        if config is None or not isinstance(config, RGConfig):
            raise RGError('RGConfig expected, actual [{}]'.format(type(config)))
        try:
            set_level(debug=config.debug_mode)
            # convert configuration to report options
            options = RGToolManager.__parse_config_to_options(config)
            # generate report
            PDFReporter(orca_path=options.orca_path).generate(options)
        except RGError as ex:
            # catch errors fro  m reporter tool and convert them to UI errors
            raise RGUIError(str(ex))

    @staticmethod
    def __parse_config_to_options(config):
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
