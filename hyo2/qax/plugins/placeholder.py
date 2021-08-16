from typing import List, Dict, NoReturn, Callable
import time

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from ausseabed.qajson.model import QajsonParam, QajsonRoot


class PlaceholderQaxPlugin(QaxCheckToolPlugin):
    """ Placeholder implementation. Use this check tool plugin for tools that are
    not yet implemented. It defines no supported file types or checks.
    """

    supported_file_types = []

    def __init__(self):
        super(PlaceholderQaxPlugin, self).__init__()

        self.name = 'Placeholder'
        self._check_references = []
        self.stopped = False

    def _build_check_references(self) -> List[QaxCheckReference]:
        return []

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(
            self,
            qajson: QajsonRoot,
            progress_callback: Callable = None
    ) -> NoReturn:
        pass

    def stop(self):
        pass
