import logging
from typing import Optional

def set_logging(
        ns_list: Optional[list] = None,
        default_logging: int = logging.WARNING,
        lib_logging: int = logging.DEBUG
    ):

    logging.basicConfig(
        level=default_logging,
        format="%(asctime)s %(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger("hyo2").setLevel(default_logging)

    main_ns = "__main__"
    if ns_list is None:
        ns_list = [main_ns, ]
    if main_ns not in ns_list:
        ns_list.append(main_ns)

    for ns in ns_list:
        logging.getLogger(ns).setLevel(lib_logging)
