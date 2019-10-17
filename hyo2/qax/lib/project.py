from collections import defaultdict
import json
import time
import os
from pathlib import Path
from PySide2 import QtCore
import traceback
import logging
from typing import Optional, NoReturn
from jsonschema import validate, ValidationError, SchemaError, Draft7Validator
from hyo2.abc.lib.helper import Helper
from hyo2.qax.lib import lib_info

from hyo2.qax.lib.inputs import QAXInputs
from hyo2.qax.lib.params import QAXParams
from hyo2.qax.lib.qa_json import QaJsonRoot

logger = logging.getLogger(__name__)


# inherits from QObject to support signals
class QAXProject(QtCore.QObject):
    """ Class represents the current QAX project as configured by the user.
    This includes option settings, QA JSON details are persisted elsewhere.
    """

    qa_json_changed = QtCore.Signal(QaJsonRoot)
    qa_json_path_changed = QtCore.Signal(Path)

    @classmethod
    def default_output_folder(cls):
        output_folder = Helper(lib_info=lib_info).package_folder()
        # create it if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        return output_folder

    def __init__(self):
        super(QAXProject, self).__init__()

        self._qa_json = None  # QaJsonRoot
        self._qa_json_path = None
        self._create_project_folder = False
        self._per_tool_folders = False
        self._output_folder = QAXProject.default_output_folder()

        self._p = QAXParams()
        self._i = QAXInputs()

    @property
    def qa_json(self) -> Optional[QaJsonRoot]:
        return self._qa_json

    @qa_json.setter
    def qa_json(self, value: Optional[QaJsonRoot]) -> NoReturn:
        self._qa_json = value
        self.qa_json_changed.emit(self._qa_json)

    @property
    def qa_json_path(self) -> Optional[Path]:
        return self._qa_json_path

    @qa_json_path.setter
    def qa_json_path(self, value: Optional[Path]) -> NoReturn:
        self._qa_json_path = value
        self.qa_json_path_changed.emit(self._qa_json_path)

    @property
    def create_project_folder(self) -> bool:
        return self._create_project_folder

    @create_project_folder.setter
    def create_project_folder(self, value: bool) -> NoReturn:
        self._create_project_folder = value

    @property
    def per_tool_folders(self) -> bool:
        return self._per_tool_folders

    @per_tool_folders.setter
    def per_tool_folders(self, value: bool) -> NoReturn:
        self._per_tool_folders = value

    @property
    def output_folder(self) -> Optional[Path]:
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: Optional[Path]) -> NoReturn:
        self._output_folder = value

    def open_output_folder(self) -> None:
        if self.output_folder:
            Helper.explore_folder(str(self.output_folder))
        else:
            logger.warning('unable to define the output folder to open')

    def get_qa_json_path(self) -> Path:
        if self.qa_json_path is not None:
            return self.qa_json_path
        if self.output_folder is not None:
            return self.output_folder.joinpath('qa.json')
        if QAXProject.default_output_folder() is not None:
            return QAXProject.default_output_folder().joinpath('qa.json')
        raise RuntimeError("could not construct qa json path")

    def save_qa_json(self) -> NoReturn:
        path = self.get_qa_json_path()
        if self.qa_json_path is None or str(path) != str(self.qa_json_path):
            # then set the qa json path to fire events so the ui updates
            # to show where the qa json file was written
            self.qa_json_path = path
        logger.debug("save json to {}".format(path))
        with open(str(path), "w") as file:
            json.dump(self.qa_json.to_dict(), file, indent=4)


    @property
    def params(self) -> QAXParams:
        return self._p

    @params.setter
    def params(self, value: QAXParams) -> None:
        self._p = value

    @property
    def inputs(self) -> QAXInputs:
        return self._i

    @inputs.setter
    def inputs(self, value: QAXInputs) -> None:
        self._i = value

    def clear_inputs(self):
        self._i = QAXInputs()




    def execute_all(self, qa_group: str = "survey_products"):
        checks = self.inputs.qa_json.js['qa'][qa_group]['checks']
        logger.debug("checks: %s" % checks)
        nr_of_checks = len(checks)
        for idx in range(nr_of_checks):
            # TODO
            checks[idx]['outputs']['execution']['status'] = "completed"

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "%s" % (self._p,)
        msg += "%s" % (self._i,)
        msg += "%s" % (self._o,)
        return msg
