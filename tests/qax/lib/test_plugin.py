from pathlib import Path
from typing import Dict, NoReturn, List
import unittest

from hyo2.qax.lib.config import QaxConfigCheckTool, QaxConfigProfile
from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference
from hyo2.qax.lib.plugin import QaxFileType, QaxFileGroup
from hyo2.qax.lib.plugin import QaxPlugins
from ausseabed.qajson.model import QajsonRoot


class MyPlugin(QaxCheckToolPlugin):

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
        super(MyPlugin, self).__init__()
        self.name = 'MyPlugin test'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr01 = QaxCheckReference(
            id="ecd55c7c-ce54-4555-a344-ae53ccdd774b",
            name="Test check 01",
            data_level="survey_products",
            description="This is only for test purposes",
            supported_file_types=MyPlugin.supported_file_types
        )
        cr02 = QaxCheckReference(
            id="ca04d1f5-3b9e-44cd-bc96-6665df6206f9",
            name="Test check 02",
            data_level="survey_products",
            description="This is only for test purposes",
            supported_file_types=MyPlugin.supported_file_types
        )
        return [cr01, cr02]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        pass


class MyOtherPlugin(QaxCheckToolPlugin):

    supported_file_types = [
        QaxFileType(
            name="shp file",
            extension="shp",
            group="Shapefiles"
        )
    ]

    def __init__(self):
        super(MyOtherPlugin, self).__init__()
        self.name = 'MyOtherPlugin test'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> List[QaxCheckReference]:
        cr = QaxCheckReference(
            id="bff164d5-9fc8-40c5-ab36-6c73e47257bd",
            name="Test check 03",
            data_level="survey_products",
            description="This is only for test purposes",
            supported_file_types=MyOtherPlugin.supported_file_types
        )
        return [cr]

    def checks(self) -> List[QaxCheckReference]:
        return self._check_references

    def run(self, qajson: Dict) -> NoReturn:
        pass


class TestQaxPlugins(unittest.TestCase):

    check_tool_config = QaxConfigCheckTool.from_dict(
        {
            'name': 'test check tool',
            'pluginClass': 'tests.qax.lib.test_plugin.MyPlugin'
        }
    )
    check_tool_profile = QaxConfigProfile.from_dict(
        {
            'name': 'test profile',
            'checkTools': [
                {
                    'name': 'test check tool',
                    'pluginClass': 'tests.qax.lib.test_plugin.MyPlugin'
                },
                {
                    'name': 'test check tool other',
                    'pluginClass': 'tests.qax.lib.test_plugin.MyOtherPlugin'
                }
            ]
        }
    )

    check_tool_config_other = QaxConfigCheckTool.from_dict(
        {
            'name': 'test check tool other',
            'pluginClass': 'tests.qax.lib.test_plugin.MyOtherPlugin'
        }
    )

    def test_load_plugin(self):
        plugins = QaxPlugins()
        check_tool_plugin = plugins._load_plugin(
            TestQaxPlugins.check_tool_profile,
            TestQaxPlugins.check_tool_config)
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

    def test_qa_json_generation(self):
        qa_json = QaJsonRoot(qa=None)
        plugins = QaxPlugins()
        check_tool_plugin = plugins._load_plugin(
            TestQaxPlugins.check_tool_profile,
            TestQaxPlugins.check_tool_config)
        check_tool_plugin_other = plugins._load_plugin(
            TestQaxPlugins.check_tool_profile,
            TestQaxPlugins.check_tool_config_other)

        check_tool_plugin.update_qa_json(qa_json)
        check_tool_plugin_other.update_qa_json(qa_json)

        files = [
            Path('/my/test/bagfile.bag'),
            Path('/my/test/csarfile.csar'),
            Path('/my/test/shpfile.shp'),
        ]
        check_tool_plugin.update_qa_json_input_files(qa_json, files)
        check_tool_plugin_other.update_qa_json_input_files(qa_json, files)

        # todo: some asserts
