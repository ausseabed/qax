from pathlib import Path
from typing import Dict, NoReturn
import unittest

from hyo2.qax.lib.config import QaxConfigCheckTool
from hyo2.qax.lib.plugin import QaxCheckToolPlugin
from hyo2.qax.lib.plugin import QaxFileType, QaxFileGroup
from hyo2.qax.lib.plugin import QaxPlugins


class MyPlugin(QaxCheckToolPlugin):

    def __init__(self):
        super(MyPlugin, self).__init__()
        self.name = 'MyPlugin test'

    def run(self, qajson: Dict) -> NoReturn:
        pass


class TestQaxPlugins(unittest.TestCase):

    def test_load_plugin(self):
        check_tool_config = QaxConfigCheckTool.from_dict(
            {
                'name': 'test check tool',
                'pluginClass': 'tests.qax.lib.test_plugin.MyPlugin'
            }
        )

        plugins = QaxPlugins()
        check_tool_plugin = plugins._load_plugin(check_tool_config)
        self.assertIsInstance(check_tool_plugin, MyPlugin)

    def test_file_group_from_dict(self):
        file_group_dict = {
            'name': 'test name',
            'fileTypes': [
                {'name': 'ft name 1', 'extension': 'ft1', 'group': 'a'},
                {'name': 'ft name 2', 'extension': 'ft2', 'group': 'a'}
            ]
        }
        file_group = QaxFileGroup.from_dict(file_group_dict)

        self.assertEqual(file_group_dict['name'], file_group.name)
        self.assertEqual(
            len(file_group_dict['fileTypes']),
            len(file_group.file_types))

    def test_file_group_merge(self):
        sp1 = QaxFileGroup(
            name="Raw Products",
            file_types=[
                QaxFileType('all file', 'all', 'Raw Products'),
                QaxFileType('raw file', 'raw', 'Raw Products'),
            ]
        )
        sp2 = QaxFileGroup(
            name="Raw Products",
            file_types=[
                QaxFileType('raw file', 'raw', 'Raw Products'),
            ]
        )
        sp3 = QaxFileGroup(
            name="Survey DTMs",
            file_types=[
                QaxFileType('tif file', 'tif', 'Survey DTMs'),
            ]
        )

        merged_prods = QaxFileGroup.merge([sp1, sp2, sp3])
        self.assertEqual(2, len(merged_prods))

        self.assertTrue(any(p.name == "Raw Products" for p in merged_prods))
        self.assertTrue(any(p.name == "Survey DTMs" for p in merged_prods))

        raw_prod = next(
            (p for p in merged_prods if p.name == "Raw Products"), None)
        self.assertEqual(2, len(raw_prod.file_types))
        raw_prod_all_ft = next(
            (ft for ft in raw_prod.file_types if ft.name == "all file"), None)
        self.assertTrue(raw_prod_all_ft is not None)
        raw_prod_raw_ft = next(
            (ft for ft in raw_prod.file_types if ft.name == "raw file"), None)
        self.assertTrue(raw_prod_raw_ft is not None)
        raw_prod_tif_ft = next(
            (ft for ft in raw_prod.file_types if ft.name == "tif file"), None)
        self.assertTrue(raw_prod_tif_ft is None)

        dtm_prod = next(
            (p for p in merged_prods if p.name == "Survey DTMs"), None)
        self.assertEqual(1, len(dtm_prod.file_types))
        dtm_prod_tif_ft = next(
            (ft for ft in dtm_prod.file_types if ft.name == "tif file"), None)
        self.assertTrue(dtm_prod_tif_ft is not None)

    def test_matching_file_type(self):
        sp1 = QaxFileGroup(
            name="Raw Products",
            file_types=[
                QaxFileType('all file', 'all', 'a'),
                QaxFileType('raw file', 'raw', 'a'),
            ]
        )

        path = Path('test/file/path/raw.all')
        matching_file_type = sp1.matching_file_type(path)
        self.assertEqual("all file", matching_file_type.name)

        path = Path('test/file/path/raw.has_no_file_type')
        matching_file_type = sp1.matching_file_type(path)
        self.assertIsNone(matching_file_type)
