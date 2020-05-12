from typing import List, Dict, NoReturn, Callable
import time

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from hyo2.qax.lib.qa_json import QaJsonParam, QaJsonRoot


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
        self.stopped = False

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="54321",
            name="Flier finder checks",
            data_level="survey_products",
            description="Identifies outliers in grided data products",
            supported_file_types=FlierFinderQaxPlugin.supported_file_types,
            default_input_params=[
                QaJsonParam("Height threshold", "32.3"),
                QaJsonParam("Algorithm", "nearest"),
                QaJsonParam("Max flier count", 20),
            ]
        )

        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(
            self,
            qajson: QaJsonRoot,
            progress_callback: Callable = None
            ) -> NoReturn:
        self.stopped = False
        print("Start flier finder checks")
        max_val = 20
        for i in range(0, max_val):
            if self.stopped:
                return
            time.sleep(0.5)
            progress_callback(self, i/max_val)
        print("End flier finder checks")

    def stop(self):
        self.stopped = True


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
        self.stopped = False

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="654321",
            name="Holiday finder checks",
            data_level="survey_products",
            description="Identifies areas of missing data",
            supported_file_types=HolidayFinderQaxPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(
            self,
            qajson: QaJsonRoot,
            progress_callback: Callable = None
            ) -> NoReturn:
        self.stopped = False
        print("Start holiday finder checks")
        max_val = 20
        for i in range(0, max_val):
            if self.stopped:
                return
            time.sleep(0.5)
            progress_callback(self, i/max_val)
        print("End holiday finder checks")

    def stop(self):
        self.stopped = True


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
        self.stopped = False

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="654321",
            name="Coverage checker",
            data_level="survey_products",
            description="Confirms coverage of data across expected area",
            supported_file_types=CoverageCheckQaxPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(
            self,
            qajson: QaJsonRoot,
            progress_callback: Callable = None
            ) -> NoReturn:
        self.stopped = False
        print("Start Coverage checker checks")
        max_val = 10
        for i in range(0, max_val):
            if self.stopped:
                return
            time.sleep(0.5)
            progress_callback(self, i/max_val)
        print("End Coverage checker checks")

    def stop(self):
        self.stopped = True
