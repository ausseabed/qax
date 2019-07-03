from jsonschema import validate, ValidationError, SchemaError, Draft7Validator
import json
import logging
from pathlib import Path
from hyo2.abc.lib.logging import set_logging

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

here = Path(__file__).parent
data_folder = here.joinpath("data")
if not data_folder.exists():
    raise RuntimeError("Unable to locate %s" % data_folder)

schema_paths = list()
qa_paths = list()
for path in data_folder.glob('*.json'):

    if path.match('*.schema.json'):
        schema_paths.append(path)
    else:
        qa_paths.append(path)

schema_path = schema_paths[0]
logger.debug("schema path: %s" % schema_path)
schema = json.loads(open(schema_path).read())
Draft7Validator.check_schema(schema)
# logger.debug(schema)

qa_path = qa_paths[0]
logger.debug("qa path: %s" % qa_path)
qa = json.loads(open(qa_path).read())
# logger.debug(json)

try:
    validate(instance=qa, schema=schema)
except ValidationError as e:
    logger.warning("%s" % e)
    exit(1)
except SchemaError as e:
    logger.warning("%s" % e)
    exit(1)

logger.debug("valid!")
