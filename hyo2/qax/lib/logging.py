import logging
from typing import Optional

from hyo2.qax.app import gui_settings_const
from hyo2.qax.app.gui_settings import GuiSettings

# for the purposes of logging, these namespaces are the ones
# we classify as being part of QAX
QAX_NAMESPACES = ["hyo2.qax", "ausseabed"]

def set_logging(
        ns_list: Optional[list] = QAX_NAMESPACES,
        default_logging: int = logging.WARNING,
        qax_logging: int = logging.DEBUG,
        qt_logging: int = logging.INFO
    ):

    logging.basicConfig(
        level=default_logging,
        format="%(asctime)s %(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    main_ns = "__main__"
    if ns_list is None:
        ns_list = [main_ns]
    if main_ns not in ns_list:
        ns_list.append(main_ns)

    for ns in ns_list:
        logging.getLogger(ns).setLevel(qax_logging)

    logging.getLogger("qt").setLevel(qt_logging)

def setup_logging() -> None:
    log_qax_val = GuiSettings.settings().value(gui_settings_const.logging_qax)
    log_qt_val = GuiSettings.settings().value(gui_settings_const.logging_qt)
    log_other_val = GuiSettings.settings().value(gui_settings_const.logging_other)

    log_qax_val = gui_settings_const.logging_qax_default if log_qax_val is None else log_qax_val
    log_qt_val = gui_settings_const.logging_qt_default if log_qt_val is None else log_qt_val
    log_other_val = gui_settings_const.logging_other_default if log_other_val is None else log_other_val

    log_qax_int = [item[1] for item in gui_settings_const.LOG_LEVELS if item[0] == log_qax_val][0]
    log_qt_int = [item[1] for item in gui_settings_const.LOG_LEVELS if item[0] == log_qt_val][0]
    log_other_int = [item[1] for item in gui_settings_const.LOG_LEVELS if item[0] == log_other_val][0]

    set_logging(
        default_logging=log_other_int,
        qax_logging=log_qax_int,
        qt_logging=log_qt_int
    )

    logger = logging.getLogger(__name__)
    logger.debug(f"log levels: QAX-{log_qax_int}, default-{log_other_int}, QT-{log_qt_int}")
