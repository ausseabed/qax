from typing import List, Dict, NoReturn

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType


class MateQaxPlugin(QaxCheckToolPlugin):

    # all Mate checks support the same file types
    supported_file_types = [
        QaxFileType(
            name="Kongsberg raw sonar files",
            extension="all",
            group="Raw Files",
            icon="kng.png"
        ),
        QaxFileType(
            name="Kongsberg raw sonar files",
            extension="wcd",
            group="Raw Files",
            icon="kng.png"
        )
    ]

    def __init__(self):
        super(MateQaxPlugin, self).__init__()
        # name of the check tool
        self.name = 'Mate'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="4321",
            name="Placeholder mate check",
            data_level="raw_data",
            description="This is only for test purposes",
            supported_file_types=MateQaxPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        print("Running Mate")
