from hyo2.abc.lib.logging import set_logging
import logging
from pathlib import Path

from hyo2.qax.lib.project import QAXProject
from hyo2.qax.lib.inputs import QAXInputs
from hyo2.qax.lib.outputs import QAXOutputs
from hyo2.qax.lib.params import QAXParams

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qax", ])

prj = QAXProject()
logger.debug("%s" % prj)
# prj.outputs.open_output_folder()
