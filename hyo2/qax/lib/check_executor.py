from typing import List
import multiprocessing as mp

from ausseabed.qajson.model import QajsonRoot
from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxPlugins


class CheckExecutor():
    """ Executes checks sequentially, calling a number of functions throughout
    to provide feedback on execution status. This class will work independently
    but is intended to be inherited (refer to MultiprocessCheckExecutor for
    example)
    """

    def __init__(
            self,
            qa_json: QajsonRoot,
            profile_name: str,
            check_tool_class_names: List[str]):
        self.qa_json = qa_json
        self.profile_name = profile_name
        self.check_tool_class_names = check_tool_class_names
        self.current_check_number = 1
        self.stopped = False
        self.status = "Not started"

        # dictionary containing some options that will be passed to each check
        # includes things lke location to write spatial outputs too, what
        # spatial outputs to write
        self.options = {}

        self.check_tools = [
            QaxPlugins.instance().get_plugin(
                self.profile_name,
                check_tool_class_name
            )
            for check_tool_class_name in self.check_tool_class_names
        ]

    def _progress_callback(self, check_tool, progress):
        print(progress)

    def _qajson_update_callback(self):
        print("QAJSON Updated")

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
            if self.is_stopped():
                self._set_status("Stopped")
                self._checks_complete()
                return

            self._check_tool_started(
                check_tool,
                self.current_check_number,
                len(self.check_tools)
            )

            check_tool.options = self.options

            check_tool.run(
                self.qa_json,
                self._progress_callback,
                self._qajson_update_callback,
                self.is_stopped
            )
            self._increment_check_number()
        if self.is_stopped():
            self._set_status("Stopped")
        else:
            self._set_status("Complete")
            self._progress_callback(None, 1.0)
        self._checks_complete()

    def is_stopped(self) -> bool:
        return self.stopped

    def stop(self):
        self._set_status("Stopping")
        for check_tool in self.check_tools:
            check_tool.stop()
        self.stopped = True


''' The following *QueueItem classes are used for communication between the parent
and child process via a multiprocessing queue. The information they pass needs to
be kept simple (must be pickle'able).
'''


class ProgressQueueItem:

    def __init__(self, check_tool_class_name: str, progress: float):
        self.check_tool_class_name = check_tool_class_name
        self.progress = progress

    def __str__(self):
        return f"ProgressQueueItem ({self.check_tool_class_name}, {self.progress})"


class CheckToolStartedQueueItem:

    def __init__(
            self,
            check_tool_class_name: str,
            check_number: int,
            total_check_count: int):
        self.check_tool_class_name = check_tool_class_name
        self.check_number = check_number
        self.total_check_count = total_check_count

    def __str__(self):
        return (
            f"CheckToolStartedQueueItem ({self.check_tool_class_name}, "
            f"{self.check_number}/{self.total_check_count})"
        )


class StatusQueueItem:

    def __init__(self, status: str):
        self.status = status

    def __str__(self):
        return f"StatusQueueItem ({self.status})"


class QajsonChangedQueueItem:

    def __init__(self, qajson: QajsonRoot):
        self.qajson = qajson

    def __str__(self):
        return f"QajsonChangedQueueItem"


class ChecksCompleteQueueItem:
    """ There's no information to pass back when the checks have completed, this
    class exists to maintain the patern of passing these instance back to the
    GUI thread via a single thread.
    """

    def __str__(self):
        return "ChecksCompleteQueueItem"


class MultiprocessCheckExecutor(mp.Process, CheckExecutor):
    ''' Implementation of multiprocessing Process class for the QAX CheckExecutor.
    Allows the checks to be processed in a background thread (to keep UI
    responsive). Communication with parent thread is handled by the Queue object
    passed into __init__
    '''

    def __init__(
            self,
            qa_json: QajsonRoot,
            profile_name: str,
            check_tool_class_names: List[str],
            queue: mp.Queue):
        super(MultiprocessCheckExecutor, self).__init__()
        CheckExecutor.__init__(
            self,
            qa_json,
            profile_name,
            check_tool_class_names)
        self.queue = queue
        self.stop_event = mp.Event()

    def run(self):
        # seems ugly, but is required
        # expect this is related to the fact both the Process and CheckExecutor
        # classes implement a `run` function.
        CheckExecutor.run(self)

    def stop(self):
        self._set_status("Stopping")
        self.stop_event.set()

    def is_stopped(self) -> bool:
        return self.stop_event.is_set()

    def _progress_callback(self, check_tool, progress):
        # check_tool is none when all the checks have been completed
        check_tool_str = (
            None
            if check_tool is None else check_tool.plugin_class
        )
        progress_item = ProgressQueueItem(check_tool_str, progress)
        self.queue.put(progress_item)

    def _qajson_update_callback(self):
        self.queue.put(
            QajsonChangedQueueItem(self.qa_json)
        )

    def _check_tool_started(self, check_tool, check_number, total_check_count):
        cts_item = CheckToolStartedQueueItem(
            check_tool.plugin_class,
            check_number,
            total_check_count
        )
        self.queue.put(cts_item)

    def _checks_complete(self):
        self.queue.put(ChecksCompleteQueueItem())

    def _set_status(self, status: str):
        self.status = status
        self.queue.put(StatusQueueItem(status))
