from collections import defaultdict
from jsonschema import validate, ValidationError, SchemaError, Draft7Validator
from pathlib import Path
from typing import Optional, Dict, List, Any
import json
import logging
import os
import time
import traceback

logger = logging.getLogger(__name__)


class QaJsonFile:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonFile':
        instance = cls(
            path=data['path'],
            description=data['description'] if 'description' in data else None
        )
        return instance

    def __init__(self, path: str, description: str):
        self.path = path
        self.description = description

    def to_dict(self):
        dict = {
            'path': self.path,
        }
        if self.description is not None:
            dict['description'] = self.description
        return dict


class QaJsonGroup:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonGroup':
        instance = cls(
            id=data['id'],
            name=data['name'] if 'name' in data else None,
            description=data['description'] if 'description' in data else None
        )
        return instance

    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self):
        dict = {
            'id': self.id,
        }
        if self.name is not None:
            dict['name'] = self.name
        if self.description is not None:
            dict['description'] = self.description
        return dict


class QaJsonExecution:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonExecution':
        instance = cls(
            start=data['start'] if 'start' in data else None,
            end=data['end'] if 'end' in data else None,
            status=data['status'] if 'status' in data else None
        )
        return instance

    def __init__(self, start: str, end: str, status: str):
        self.start = start
        self.end = end
        self.status = status

    def to_dict(self):
        dict = {
            'status': self.status,
        }
        if self.start is not None:
            dict['start'] = self.start
        if self.end is not None:
            dict['end'] = self.end
        return dict


class QaJsonParam:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonParam':
        group = (
            QaJsonGroup.from_dict(data['group']) if 'group' in data else None)
        instance = cls(
            name=data['name'],
            value=data['value']
        )
        return instance

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def to_dict(self):
        dict = {
            'name': self.name,
            'value': self.value
        }
        return dict


class QaJsonInfo:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonInfo':
        group = (
            QaJsonGroup.from_dict(data['group']) if 'group' in data else None)
        instance = cls(
            id=data['id'],
            name=data['name'] if 'name' in data else None,
            description=data['description'] if 'description' in data else None,
            version=data['version'] if 'version' in data else None,
            group=group,
        )
        return instance

    def __init__(
            self,
            id: str,
            name: str,
            description: str,
            version: str,
            group: QaJsonGroup):
        self.id = id
        self.name = name
        self.description = description
        self.version = version
        self.group = group

    def to_dict(self):
        dict = {
            'id': self.id,
        }
        if self.name is not None:
            dict['name'] = self.name
        if self.description is not None:
            dict['description'] = self.description
        if self.version is not None:
            dict['version'] = self.version
        if self.group is not None:
            dict['group'] = self.group.to_dict()
        return dict


class QaJsonInputs:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonInputs':
        files = []
        if 'files' in data:
            files = [
                QaJsonFile.from_dict(file_dict)
                for file_dict in data['files']
            ]
        params = []
        if 'params' in data:
            params = [
                QaJsonParam.from_dict(param_dict)
                for param_dict in data['params']
            ]
        instance = cls(files=files, params=params)
        return instance

    def __init__(self, files: List[QaJsonFile], params: List[QaJsonParam]):
        self.files = files
        self.params = params

    def to_dict(self):
        return {
            'files': [file.to_dict() for file in self.files],
            'params': [param.to_dict() for param in self.params]
        }


class QaJsonOutputs:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonOutputs':
        files = []
        if 'files' in data:
            files = [
                QaJsonFile.from_dict(file_dict)
                for file_dict in data['files']
            ]

        instance = cls(
            execution=QaJsonExecution.from_dict(data['execution']),
            files=files,
            count=data['count'] if 'count' in data else None,
            percentage=data['percentage'] if 'percentage' in data else None,
        )
        return instance

    def __init__(
            self,
            execution: QaJsonExecution,
            files: List[QaJsonFile],
            count: int,
            percentage: float):
        self.execution = execution
        self.files = files
        self.count = count
        self.percentage = percentage

    def to_dict(self):
        dict = {
            'execution': QaJsonExecution.to_dict(self.execution),
            'files': [file.to_dict() for file in self.files],
        }
        if self.count is not None:
            dict['count'] = self.count
        if self.percentage is not None:
            dict['percentage'] = self.percentage
        return dict


class QaJsonCheck:

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonCheck':
        outputs = (
            QaJsonOutputs.from_dict(data['outputs'])
            if 'outputs' in data else None)
        inputs = (
            QaJsonInputs.from_dict(data['inputs'])
            if 'inputs' in data else None)

        instance = cls(
            info=QaJsonInfo.from_dict(data['info']),
            outputs=outputs,
            inputs=inputs,
        )
        return instance

    def __init__(
            self,
            info: QaJsonInfo,
            inputs: QaJsonInputs,
            outputs: QaJsonOutputs):
        self.info = info
        self.inputs = inputs
        self.outputs = outputs

    def get_or_add_inputs(self) -> QaJsonInputs:
        if self.inputs is None:
            self.inputs = QaJsonInputs(files=[], params=[])
        return self.inputs

    def to_dict(self):
        dict = {
            'info': self.info.to_dict(),
        }
        if self.inputs is not None:
            dict['inputs'] = self.inputs.to_dict()
        if self.outputs is not None:
            dict['outputs'] = self.outputs.to_dict()
        return dict


class QaJsonDataLevel:
    """ Represents QA JSON data type. Data type refers to a grouping of
    input data loosly based on processed state. eg; raw data, or survey
    products.
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonDataLevel':
        checks = []
        if 'checks' in data:
            checks = [
                QaJsonCheck.from_dict(check_dict)
                for check_dict in data['checks']
            ]
        instance = cls(checks=checks)
        return instance

    def __init__(self, checks: List[QaJsonCheck]):
        self.checks = checks

    def get_check(self, check_id: str) -> QaJsonCheck:
        """ Gets a check based on id, or None if the check does not exist
        """
        check = next((c for c in self.checks if c.info.id == check_id), None)
        return check

    def to_dict(self):
        return {
            'checks': [check.to_dict() for check in self.checks]
        }


class QaJsonQa:
    """ Represents QA JSON QA object. Includes metadata about the QA JSON
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonQa':
        version = data['version'] if 'version' in data else None
        chart_adequacy = (
            QaJsonDataLevel.from_dict(data['chart_adequacy'])
            if 'chart_adequacy' in data else None)
        instance = cls(
            version=version,
            raw_data=QaJsonDataLevel.from_dict(data['raw_data']),
            survey_products=QaJsonDataLevel.from_dict(data['survey_products']),
            chart_adequacy=chart_adequacy
        )
        return instance

    def __init__(
            self,
            version: str,
            raw_data: QaJsonDataLevel,
            survey_products: QaJsonDataLevel,
            chart_adequacy: QaJsonDataLevel = None):
        self.version = version
        self.raw_data = raw_data
        self.survey_products = survey_products
        self.chart_adequacy = chart_adequacy

    def get_or_add_data_level(
            self, data_level: str) -> QaJsonDataLevel:
        """ If a data level exists in the `qa` object it will be returned,
        otherwise a new QaJsonDataLevel will be created, added to the qa object
        and returned
        """
        dl = getattr(self, data_level)
        if dl is None:
            dl = QaJsonDataLevel(checks=[])
            setattr(self, data_level, dl)
        return dl

    def to_dict(self):
        dict = {
            'version': self.version,
            'raw_data': self.raw_data.to_dict(),
            'survey_products': self.survey_products.to_dict()
        }
        if self.chart_adequacy is not None:
            dict['chart_adequacy'] = self.chart_adequacy.to_dict()
        return dict


class QaJsonRoot:
    """ Represents root of a QA JSON file
    """

    @classmethod
    def from_dict(cls, data: Dict) -> 'QaJsonRoot':
        instance = cls(
            qa=QaJsonQa.from_dict(data['qa']),
        )
        return instance

    def __init__(self, qa: QaJsonQa):
        self.qa = qa

    def to_dict(self) -> Dict:
        return {
            'qa': self.qa.to_dict()
        }


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

        # todo: find more robust mechanism for identifying latest schema
        # version
        paths.sort()
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
            validate(
                instance=qa, schema=json.loads(open(str(schema_path)).read()))
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

    def __init__(
            self, path: Path, schema_path: Optional[Path] = None,
            check_valid: bool = True):
        self._path = Path(path)
        if schema_path is None:
            schema_path = self.schema_paths()[-1]
        self._schema_path = schema_path

        # validation stuff
        if check_valid:
            valid = self.validate_schema(path=self._schema_path)
            logger.debug("valid QA schema: %s" % valid)
            if not valid:
                raise RuntimeError("invalid schema: %s" % self._schema_path)

            valid = self.validate_qa_json(
                path=self._path, schema_path=self._schema_path)
            logger.debug("valid QA json: %s" % valid)
            if not valid:
                raise RuntimeError("invalid json: %s" % self._path)

        self._js = json.loads(open(str(self._path)).read())
        self._root = QaJsonRoot.from_dict(self.js)

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

    @property
    def root(self) -> QaJsonRoot:
        return self._root

    def __repr__(self):
        msg = super().__repr__()
        msg += "\n"
        msg += "  <path: %s>\n" % (self.path, )
        msg += "  <schemas folder: %s>\n" % (self.schemas_folder())
        msg += "  <schema path: %s>\n" % (self.schema_path, )
        return msg
