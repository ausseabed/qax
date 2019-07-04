import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class QAXInputs:

    def __init__(self):
        self._json_path = None
        self._ff_paths = list()
        self._dtm_paths = list()

    @property
    def json_path(self) -> Optional[str]:
        return self._json_path

    @json_path.setter
    def json_path(self, value: str) -> None:
        self._json_path = value

    @property
    def ff_paths(self) -> list:
        return self._ff_paths

    @ff_paths.setter
    def ff_paths(self, value: list) -> None:
        self._ff_paths = value

    @property
    def dtm_paths(self) -> list:
        return self._dtm_paths

    @dtm_paths.setter
    def dtm_paths(self, value: list) -> None:
        self._dtm_paths = value

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <QA JSON path: %s>\n" % (self.json_path, )
        msg += "    <DTM paths: %s>\n" % (self.dtm_paths, )
        msg += "    <FF paths: %s>\n" % (self.ff_paths, )
        return msg
