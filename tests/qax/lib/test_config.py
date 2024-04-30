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
          "pluginClass": "hyo2.qax.plugins.mate.MateQaxPlugin"
        },
        {
          "name": "Flier Finder",
          "pluginClass": "hyo2.qax.plugins.test.FlierFinderQaxPlugin"
        },
        {
          "name": "Coverage check",
          "pluginClass": "hyo2.qax.plugins.test.CoverageCheckQaxPlugin"
        }
      ],
      "specifications": [
        {
          "name": "s1",
          "description": "International Hydrographic Organization (IHO) order 1a",
          "parameters": [
            {
              "checkId": "cid1",
              "name": "p1",
              "value": 1
            },
            {
              "checkId": "cid2",
              "name": "p2",
              "value": 2
            },
          ]
        },
        {
          "name": "s2",
          "parameters": [
            {
              "checkId": "cid1",
              "name": "p3",
              "value": 3
            },
            {
              "checkId": "cid2",
              "name": "p4",
              "value": 4
            },
            {
              "checkId": "cid2",
              "name": "p5",
              "value": 5
            },
          ]
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

        self.assertEqual(2, len(profile.specifications))
        self.assertEqual(2, len(profile.specifications[0].parameters))
        self.assertEqual('s1', profile.specifications[0].name)
        self.assertEqual('p1', profile.specifications[0].parameters[0].name)
        self.assertEqual(1, profile.specifications[0].parameters[0].value)
