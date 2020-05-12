from PySide2 import QtCore
from typing import List
from ausseabed.qajson.model import QajsonRoot
from .plugin import QaxCheckToolPlugin


class CheckExecutor():
    """ Executes checks sequentially, calling a number of functions throughout
    to provide feedback on execution status. This class will work independently
    but is intended to be inherited (refer to QtCheckExecutor for example)
    """

    def __init__(
            self,
            qa_json: QajsonRoot,
            check_tools: List[QaxCheckToolPlugin]):
        self.qa_json = qa_json
        self.check_tools = check_tools
        self.current_check_number = 1
        self.stopped = False
        self.status = "Not started"

    def _progress_callback(self, check_tool, progress):
        print(progress)

    def _check_tool_started(self, check_tool, check_number, total_check_count):
        print("Started {}".format(check_tool.name))

    def _increment_check_number(self):
        self.current_check_number += 1

    def _checks_complete(self):
        print("all checks done")

    def _set_status(self, status: str):
        self.status = status

    def run(self):
        self._set_status("Running")
        self.stopped = False
        self.current_check_number = 1
        for check_tool in self.check_tools:
            if self.stopped:
                self._set_status("Stopped")
                self._checks_complete()
                return

            self._check_tool_started(
                check_tool,
                self.current_check_number,
                len(self.check_tools))

            check_tool.run(self.qa_json, self._progress_callback)
            self._increment_check_number()
        if self.stopped:
            self._set_status("Stopped")
        else:
            self._set_status("Complete")
            self._progress_callback(self, 1.0)
        self._checks_complete()

    def stop(self):
        self._set_status("Stopping")
        for check_tool in self.check_tools:
            check_tool.stop()
        self.stopped = True
