import logging
from hyo2.abc.lib.logging import set_logging
from hyo2.qax.lib.qa_json import QAJson

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qax", ])

schemas_folder = QAJson.schemas_folder()
logger.debug("QA schemas folder: %s" % schemas_folder)

# validate json schema
schema_path = QAJson.schema_paths()[-1]
logger.debug("QA schema path: %s" % schema_path)
valid = QAJson.validate_schema(path=schema_path)
# logger.debug(schema)
logger.debug("valid QA schema: %s" % valid)

# validate QA json
qa_path = QAJson.example_paths()[-1]
logger.debug("QA json path: %s" % qa_path)
valid = QAJson.validate_qa_json(path=qa_path, schema_path=schema_path)
logger.debug("valid QA json: %s" % valid)
