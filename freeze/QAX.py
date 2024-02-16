import logging

from hyo2.qax.lib.logging import set_logging
from hyo2.qax.app.gui import gui


set_logging(
    ns_list=["hyo2.qax", "ausseabed"],
    default_logging=logging.ERROR,
    lib_logging=logging.INFO
)
gui()
