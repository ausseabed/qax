from collections import defaultdict
import time
import os
import traceback
import logging
from typing import Optional

from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.qax.lib.inputs import QAXInputs
from hyo2.qax.lib.outputs import QAXOutputs
from hyo2.qax.lib.params import QAXParams

logger = logging.getLogger(__name__)


class QAXProject:

    def __init__(self):

        self._p = QAXParams()
        self._i = QAXInputs()
        self._o = QAXOutputs()

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

    @property
    def outputs(self) -> QAXOutputs:
        return self._o

    @outputs.setter
    def outputs(self, value: QAXOutputs) -> None:
        self._o = value

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "%s" % (self._p,)
        msg += "%s" % (self._i,)
        msg += "%s" % (self._o,)
        return msg
