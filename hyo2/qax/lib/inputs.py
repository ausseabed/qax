import logging
from pathlib import Path
from typing import Optional
from hyo2.qax.lib.qa_json import QAJson

logger = logging.getLogger(__name__)


class QAXInputs:

    def __init__(self):
        self._qa_json = None
        self._raw_paths = list()
        self._ff_paths = list()
        self._dtm_paths = list()
        self._enc_paths = list()

    @property
    def qa_json(self) -> Optional[QAJson]:
        return self._qa_json

    @qa_json.setter
    def qa_json(self, value: QAJson) -> None:
        self._qa_json = value

    @property
    def json_path(self) -> Optional[Path]:
        if self._qa_json is None:
            return None
        return self._qa_json.path

    @json_path.setter
    def json_path(self, value: Path) -> None:
        if value is None:
            self._qa_json = None
            return
        self._qa_json = QAJson(path=value)

    @property
    def raw_paths(self) -> list:
        return self._raw_paths

    @raw_paths.setter
    def raw_paths(self, value: list) -> None:
        self._raw_paths = value

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

    @property
    def enc_paths(self) -> list:
        return self._enc_paths

    @enc_paths.setter
    def enc_paths(self, value: list) -> None:
        self._enc_paths = value

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <QA JSON path: %s>\n" % (self.json_path, )
        msg += "    <raw paths: %s>\n" % (len(self.raw_paths), )
        msg += "    <DTM paths: %s>\n" % (len(self.dtm_paths), )
        msg += "    <FF paths: %s>\n" % (len(self.ff_paths), )
        msg += "    <ENC paths: %s>\n" % (len(self.enc_paths), )
        return msg
