from collections import defaultdict
import json
import time
import os
from pathlib import Path
import traceback
import logging
from typing import Optional
from jsonschema import validate, ValidationError, SchemaError, Draft7Validator

from hyo2.qax.lib.inputs import QAXInputs
from hyo2.qax.lib.outputs import QAXOutputs
from hyo2.qax.lib.params import QAXParams

logger = logging.getLogger(__name__)


class QAXProject:

    here = Path(__file__).parent

    def __init__(self):

        self._p = QAXParams()
        self._i = QAXInputs()
        self._o = QAXOutputs()

    @classmethod
    def schemas_folder(cls) -> Path:
        schemas_path = cls.here.joinpath("schemas")
        if not schemas_path.exists():
            raise RuntimeError("unable to locate schemas folder")
        return schemas_path

    @classmethod
    def schema_paths(cls) -> list:
        paths = list()
        for path in cls.schemas_folder().rglob('*.json'):

            if path.match('*.schema.json'):
                paths.append(path)

        return paths

    @classmethod
    def validate_schema(cls, path: Path) -> bool:
        schema = json.loads(open(str(path)).read())
        try:
            Draft7Validator.check_schema(schema)
        except Exception as e:
            logger.warning("%s" % e)
            return False

        return True

    @classmethod
    def validate_qa_json(cls, path: Path, schema_path: Path) -> bool:
        qa = json.loads(open(str(path)).read())
        # logger.debug(json)
        try:
            validate(instance=qa, schema=json.loads(open(str(schema_path)).read()))
        except ValidationError as e:
            logger.warning("%s" % e)
            return False
        except SchemaError as e:
            logger.warning("%s" % e)
            return False
        return True

    @classmethod
    def example_paths(cls) -> list:
        paths = list()
        for path in cls.schemas_folder().rglob('*.json'):

            if not path.match('*.schema.json'):
                paths.append(path)

        return paths

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

    @property
    def outputs(self) -> QAXOutputs:
        return self._o

    @outputs.setter
    def outputs(self, value: QAXOutputs) -> None:
        self._o = value

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "  <schemas folder: %s>\n" % (self.schemas_folder())
        msg += "%s" % (self._p,)
        msg += "%s" % (self._i,)
        msg += "%s" % (self._o,)
        return msg
