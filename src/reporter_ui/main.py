import logging

from common.logger import init_logger
from common.models.errors import RGError
from reporter_ui.config_reader import RGConfigReader
from reporter_ui.ui_components.ui import RGUI


def __main():
    try:
        config = RGConfigReader.read_config()
        ui = RGUI(config=config)
        ui.build()
    except RGError as ex:
        logging.error(str(ex))


if __name__ == '__main__':
    init_logger()
    __main()
