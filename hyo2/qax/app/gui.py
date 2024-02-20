import os
import sys
import traceback
from pathlib import Path
from PySide2 import QtCore, QtWidgets

import logging

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.mainwin import MainWin
from hyo2.qax.lib.config import QaxConfig
from hyo2.qax.lib.plugin import QaxPlugins
from hyo2.qax.lib.logging import setup_logging


logger = logging.getLogger(__name__)
qt_logger = logging.getLogger('qt')

def qt_custom_handler(
        error_type: QtCore.QtMsgType,
        error_context: QtCore.QMessageLogContext,
        message: str
    ):
    if "Cannot read property 'id' of null" in message:
        return
    if "The event loop is already running" in message:
        return

    qt_logger.info(
        f"Qt error: {error_type} [{error_context}] -> {message}"
    )

    for line in traceback.format_stack():
        qt_logger.debug(f"- {line.strip()}")

QtCore.qInstallMessageHandler(qt_custom_handler)


# There's a Qt issue that causes seg faults when app is defined within a
# function, so do it here.
# more details https://stackoverflow.com/a/57792609/5416735
app = QtWidgets.QApplication(sys.argv)


def gui(dev_mode=False):
    """Run the QAX gui"""

    # temporary fix for CORS warning (QTBUG-70228)
    sys.argv.append("--disable-web-security")
    # stop auto scaling on windows
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # stop auto scaling on windows - part 2
    # app.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)

    setup_logging()

    cfg_dir = GuiSettings.config_default()
    logger.info("Using config {}".format(cfg_dir))

    config = QaxConfig(Path(cfg_dir))
    config.load()
    plugins = QaxPlugins()
    plugins.load(config)

    main_win = MainWin()
    main_win.initialize()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    if dev_mode:
        main_win.do()

    sys.exit(app.exec_())
