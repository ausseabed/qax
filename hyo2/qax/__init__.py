"""
Hyo2-Package
QAX
"""

import logging
import os
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

if os.path.isfile('version.txt'):
    with open('version.txt', 'r') as file:
        __version__ = file.read()
        logger.info("Read version from file {}".format(__version__))
else:
    logger.warn("no version.txt found")
    __version__ = 'unknown'

name = "QAX"
__author__ = 'gmasetti@ccom.unh.edu; tyanne.faulkes@noaa.gov'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright 2019 University of New Hampshire, Center for Coastal and Ocean Mapping'
