import logging

from common.logger import init_logger
from common.models.errors import RGError
from reporter_ui.config_manager import RGConfigManager
from reporter_ui.ui_components.ui import RGUI


def __main():
    try:
        config = RGConfigManager.read_config()

        ui = RGUI(config=config)
        ui.build()
    except RGError as ex:
        logging.error(str(ex))


if __name__ == '__main__':
    init_logger()
    __main()
