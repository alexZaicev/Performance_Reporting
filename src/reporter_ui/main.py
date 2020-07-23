import logging

from common.logger import init_logger
from common.models.errors import RGError, RGInvalidConfigurationError
from reporter_ui.components.application import RGApplication
from reporter_ui.config_manager import RGConfigManager


def __main():
    try:
        config = RGConfigManager.read_config()
        ui = RGApplication(config=config)
        ui.build()
    except RGInvalidConfigurationError as ex:
        RGApplication.show_error_dialog(message=str(ex), exit_on_ok=True)
    except RGError as ex:
        # Fatal application exceptions
        logging.getLogger(__name__).error(str(ex))
        RGApplication.show_error_dialog(message=str(ex), exit_on_ok=True)


if __name__ == '__main__':
    init_logger()
    __main()
