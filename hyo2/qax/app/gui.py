import os
import sys
import traceback
from pathlib import Path
from PySide2 import QtCore, QtWidgets

import logging

from hyo2.abc.app.app_style import AppStyle
from hyo2.abc.lib.logging import set_logging
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.mainwin import MainWin
from hyo2.qax.lib.config import QaxConfig
from hyo2.qax.lib.plugin import QaxPlugins

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qax", ])


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    if "Cannot read property 'id' of null" in message:
        return
    if "The event loop is already running" in message:
        return

    logger.info("Qt error: %s [%s] -> %s"
                % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui(dev_mode=False):
    """Run the QAX gui"""

    # temporary fix for CORS warning (QTBUG-70228)
    sys.argv.append("--disable-web-security")
    # stop auto scaling on windows
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    # stop auto scaling on windows - part 2
    app.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)
    app.setStyleSheet(AppStyle.load_stylesheet())

    cfg_dir = GuiSettings.config()
    # setup user editable config directory
    if not os.path.isdir(cfg_dir):
        # config does not exist, so copy out default settings
        logger.info("Copying default config to {}".format(cfg_dir))
        import shutil
        shutil.copytree(GuiSettings.config_default(), cfg_dir)
    else:
        logger.info("Using existing config {}".format(cfg_dir))

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
