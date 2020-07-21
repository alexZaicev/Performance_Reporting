import logging

from common.logger import init_logger
from common.models.errors import RGError, RGUIError
from reporter_ui.config_manager import RGConfigManager
from reporter_ui.components.application import RGApplication


def __main():
    try:
        config = RGConfigManager.read_config()

        ui = RGApplication(config=config)
        ui.build()
    except RGError as ex:
        # Fatal application exceptions
        logging.error(str(ex))


if __name__ == '__main__':
    init_logger()
    __main()
