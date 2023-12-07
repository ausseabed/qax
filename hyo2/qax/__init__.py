"""
Hyo2-Package
QAX
"""

import logging
try:
    from importlib import metadata as _md
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as _md

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    __version__ = _md.version(__name__)
except _md.PackageNotFoundError:
    # keeping the original logic of specifying unknown
    logger.warn("module version not found")
    __version__ = "unknown"

name = "QAX"
__author__ = 'gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2019 University of New Hampshire, Center for Coastal and Ocean Mapping'
