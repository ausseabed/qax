import os
import sys
from pathlib import Path
import logging

LOG = logging.getLogger()

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    LOG.info('QAX running in pyinstaller bundle')
    pth = Path(sys._MEIPASS)
    gdal_path = pth.joinpath('Library', 'share', 'gdal')
    os.environ['GDAL_DATA'] = str(gdal_path.resolve())
    LOG.info(f"set env var GDAL_DATA = {os.environ['GDAL_DATA']}")
else:
    LOG.info('QAX not runint in pyinstaller bundle')
    LOG.info('Not setting env var GDAL_DATA')
