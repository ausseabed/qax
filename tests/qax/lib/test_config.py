from pathlib import Path
import unittest

from hyo2.qax.lib.config import QaxConfig
from hyo2.qax.lib.config import QaxConfigProfile


class TestQaxConfig(unittest.TestCase):

    profile_dict = {
      "name": "AusSeabed",
      "checkTools": [
        {
          "name": "Mate",
          "description": "QA checks for raw bathymetry data",
          "pluginClass": "hyo2.qax.plugins.mate.MateQaxPlugin",
          "enabled": False,
          "checked": True
        },
        {
          "name": "Flier Finder",
          "pluginClass": "hyo2.qax.plugins.test.FlierFinderQaxPlugin"
        },
        {
          "name": "Coverage check",
          "pluginClass": "hyo2.qax.plugins.test.CoverageCheckQaxPlugin"
        }
      ]
    }

    def test_qax_config_load(self):
        profile = QaxConfigProfile.from_dict(TestQaxConfig.profile_dict)

        self.assertEqual(3, len(profile.check_tools))
        self.assertTrue(any(p.name == "Mate" for p in profile.check_tools))
        self.assertTrue(
            any(p.name == "Flier Finder" for p in profile.check_tools))
        self.assertTrue(
            any(p.name == "Coverage check" for p in profile.check_tools))
