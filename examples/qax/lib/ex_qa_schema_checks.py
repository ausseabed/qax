import logging
from hyo2.qax.lib.logging import set_logging
from ausseabed.qajson.parser import QajsonParser

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qax", ])

schemas_folder = QajsonParser.schemas_folder()
logger.debug("QA schemas folder: %s" % schemas_folder)

# validate json schema
schema_path = QajsonParser.schema_paths()[-1]
logger.debug("QA schema path: %s" % schema_path)
valid = QajsonParser.validate_schema(path=schema_path)
# logger.debug(schema)
logger.debug("valid QA schema: %s" % valid)

# validate QA json
qa_path = QajsonParser.example_paths()[-1]
logger.debug("QA json path: %s" % qa_path)
valid = QajsonParser.validate_qa_json(path=qa_path, schema_path=schema_path)
logger.debug("valid QA json: %s" % valid)
