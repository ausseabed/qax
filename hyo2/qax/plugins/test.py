from typing import List, Dict, NoReturn

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType


class FlierFinderQaxPlugin(QaxCheckToolPlugin):

    # all Mate checks support the same file types
    supported_file_types = [
        QaxFileType(
            name="BAG file",
            extension="bag",
            group="Survey DTMs",
            icon="bag.png"
        ),
        QaxFileType(
            name="CSAR file",
            extension="csar",
            group="Survey DTMs",
            icon="csar.png"
        )
    ]

    def __init__(self):
        super(FlierFinderQaxPlugin, self).__init__()
        # name of the check tool
        self.name = 'Flier Finder'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="54321",
            name="Placeholder flier finder checks",
            data_level="survey_products",
            description="This is only for test purposes",
            supported_file_types=FlierFinderQaxPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        print("Running Flier finder")


class HolidayFinderQaxPlugin(QaxCheckToolPlugin):

    # all Mate checks support the same file types
    supported_file_types = [
        QaxFileType(
            name="BAG file",
            extension="bag",
            group="Survey DTMs",
            icon="bag.png"
        ),
        QaxFileType(
            name="CSAR file",
            extension="csar",
            group="Survey DTMs",
            icon="csar.png"
        )
    ]

    def __init__(self):
        super(HolidayFinderQaxPlugin, self).__init__()
        # name of the check tool
        self.name = 'Holiday Finder'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="654321",
            name="Placeholder holiday finder checks",
            data_level="survey_products",
            description="This is only for test purposes",
            supported_file_types=HolidayFinderQaxPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        print("Running Holiday finder")


class CoverageCheckQaxPlugin(QaxCheckToolPlugin):

    # all Mate checks support the same file types
    supported_file_types = [
        QaxFileType(
            name="BAG file",
            extension="bag",
            group="Survey DTMs",
            icon="bag.png"
        ),
        QaxFileType(
            name="CSAR file",
            extension="csar",
            group="Survey DTMs",
            icon="csar.png"
        ),
        QaxFileType(
            name="Shapefile",
            extension="shp",
            group="Expected coverage"
        ),
        QaxFileType(
            name="GeoJSON",
            extension="json",
            group="Expected coverage"
        )
    ]

    def __init__(self):
        super(CoverageCheckQaxPlugin, self).__init__()
        # name of the check tool
        self.name = 'Coverage checker'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="654321",
            name="Coverage checker",
            data_level="survey_products",
            description="This is only for test purposes",
            supported_file_types=CoverageCheckQaxPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        print("Running coverage check")
