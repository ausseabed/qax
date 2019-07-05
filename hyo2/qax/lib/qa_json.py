from collections import defaultdict
import json
import time
import os
from pathlib import Path
import traceback
import logging
from typing import Optional
from jsonschema import validate, ValidationError, SchemaError, Draft7Validator

logger = logging.getLogger(__name__)


class QAJson:

    here = Path(__file__).parent

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

    def __init__(self, path: Path, schema_path: Optional[Path] = None, check_valid: bool = True):
        self._path = path
        if schema_path is None:
            schema_path = self.schema_paths()[-1]
        self._schema_path = schema_path

        # validation stuff
        if check_valid:
            valid = self.validate_schema(path=self._schema_path)
            logger.debug("valid QA schema: %s" % valid)
            if not valid:
                raise RuntimeError("invalid schema: %s" % self._schema_path)

            valid = self.validate_qa_json(path=self._path, schema_path=self._schema_path)
            logger.debug("valid QA json: %s" % valid)
            if not valid:
                raise RuntimeError("invalid json: %s" % self._path)

        self._js = json.loads(open(str(self._path)).read())

    @property
    def path(self) -> Path:
        return self._path

    @property
    def schema_path(self) -> Path:
        return self._schema_path

    @property
    def js(self) -> Optional[object]:
        return self._js

    @js.setter
    def js(self, value: object) -> None:
        self._js = value

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "  <path: %s>\n" % (self.path, )
        msg += "  <schemas folder: %s>\n" % (self.schemas_folder())
        msg += "  <schema path: %s>\n" % (self.schema_path, )
        return msg
