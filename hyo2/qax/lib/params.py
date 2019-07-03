import logging
from typing import Optional
from hyo2.abc.lib.progress.abstract_progress import AbstractProgress
from hyo2.abc.lib.progress.cli_progress import CliProgress

logger = logging.getLogger(__name__)


class QAXParams:

    def __init__(self):

        self._progress = CliProgress()
        self._profile = str()

        self._flier_finder = False
        self._holiday_finder = False
        self._grid_qa = False
        self._designated_scan = False
        self._feature_scan = False
        self._valsou_check = False

        self._write_kml = False
        self._write_shp = False

    @property
    def profile(self) -> str:
        return self._profile

    @profile.setter
    def profile(self, value: str) -> None:
        self._profile = value

    @property
    def progress(self) -> Optional[AbstractProgress]:
        return self._progress

    @progress.setter
    def progress(self, value: AbstractProgress) -> None:
        self._progress = value

    @property
    def flier_finder(self) -> bool:
        return self._flier_finder

    @flier_finder.setter
    def flier_finder(self, value: bool) -> None:
        self._flier_finder = value

    @property
    def holiday_finder(self) -> bool:
        return self._holiday_finder

    @holiday_finder.setter
    def holiday_finder(self, value: bool) -> None:
        self._holiday_finder = value

    @property
    def grid_qa(self) -> bool:
        return self._grid_qa

    @grid_qa.setter
    def grid_qa(self, value: bool) -> None:
        self._grid_qa = value

    @property
    def designated_scan(self) -> bool:
        return self._designated_scan

    @designated_scan.setter
    def designated_scan(self, value: bool) -> None:
        self._designated_scan = value

    @property
    def feature_scan(self) -> bool:
        return self._feature_scan

    @feature_scan.setter
    def feature_scan(self, value: bool) -> None:
        self._feature_scan = value

    @property
    def valsou_check(self) -> bool:
        return self._valsou_check

    @valsou_check.setter
    def valsou_check(self, value: bool) -> None:
        self._valsou_check = value

    def __repr__(self):
        msg = "  <%s>\n" % self.__class__.__name__
        msg += "    <progress: %s>\n" % bool(self.progress)
        msg += "    <profile: %s>\n" % self._profile
        msg += "    <flier finder: %s>\n" % self._flier_finder
        msg += "    <holiday finder: %s>\n" % self._holiday_finder
        msg += "    <grid qa: %s>\n" % self._grid_qa
        msg += "    <designated scan: %s>\n" % self._designated_scan
        msg += "    <feature scan: %s>\n" % self._feature_scan
        msg += "    <valsou check: %s>\n" % self._valsou_check
        return msg
