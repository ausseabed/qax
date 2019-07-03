import logging
import os
from pathlib import Path
from typing import Optional
from hyo2.abc.lib.helper import Helper
from hyo2.qax.lib import lib_info

logger = logging.getLogger(__name__)


class QAXOutputs:

    def __init__(self):
        self._output_folder = self.default_output_folder()

    @property
    def output_folder(self) -> Optional[Path]:
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: Path) -> None:
        self._output_folder = value

    def open_output_folder(self) -> None:
        if self.output_folder:
            Helper.explore_folder(str(self.output_folder))
        else:
            logger.warning('unable to define the output folder to open')

    @classmethod
    def default_output_folder(cls):

        output_folder = Helper(lib_info=lib_info).package_folder()
        if not os.path.exists(output_folder):  # create it if it does not exist
            os.makedirs(output_folder)

        return output_folder

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <output folder: %s>\n" % self.output_folder
        return msg
