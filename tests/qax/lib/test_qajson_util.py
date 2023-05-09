import os
from collections import OrderedDict
from pathlib import Path
import unittest


from ausseabed.qajson.model import QajsonFile, QajsonParam, QajsonInputs, \
    QajsonOutputs, QajsonInfo, QajsonRoot, QajsonQa, QajsonDataLevel
from ausseabed.qajson.parser import QajsonParser
from hyo2.qax.lib.plugin import QaxPlugins, QaxConfig
from hyo2.qax.lib.qajson_util import QajsonExcelExporter, QajsonTableSummary, QajsonFileSummary
from hyo2.qax.app.gui_settings import GuiSettings

class TestParser(unittest.TestCase):

    def test_qajson_read(self):
        here = os.path.abspath(os.path.dirname(__file__))
        test_file = Path(os.path.join(here, "export_test.json"))

        qajson = QajsonParser(test_file).root

        cfg_dir = GuiSettings.config_default()

        config = QaxConfig(Path(cfg_dir))
        config.load()
        plugins = QaxPlugins()
        plugins.load(config)

        profile = QaxConfig.instance().profiles[0]
        profile_plugins = QaxPlugins.instance().get_profile_plugins(profile)

        output_file = Path(str(test_file) + '.xlsx')

        exporter = QajsonExcelExporter()
        exporter.export(
            qajson,
            file=output_file,
            plugins=profile_plugins
        )

        self.assertTrue(output_file.resolve().is_file())

    def test_summary_heading_label(self):
        fn = 'Xi1039_B11_MBES_c1m_Prelim_r3_MULTI_crop.tif'
        summary = QajsonFileSummary(fn)
        self.assertEqual(summary.summary_heading_label, 'Xi1039_B11_MBES_c1m')

        fn = 'Xi1039_B12_MBES_c1m_LAT_Prelim_r4_MULTI_crop.tif'
        summary = QajsonFileSummary(fn)
        self.assertEqual(summary.summary_heading_label, 'Xi1039_B12_MBES_c1m')

        fn = 'Xi1039 B12 MBES c1m LAT Prelim r4_MULTI_crop.tif'
        summary = QajsonFileSummary(fn)
        self.assertEqual(summary.summary_heading_label, 'Xi1039 B12 MBES c1m')

        fn = 'Xi1039B12MBESc1mLATPrelimr4MULTIcrop.tif'
        summary = QajsonFileSummary(fn)
        self.assertEqual(
            summary.summary_heading_label,
            'Xi1039B12MBESc1mLATPrelimr4MULTIcrop'
        )

        fn = 'a-b.tif'
        summary = QajsonFileSummary(fn)
        self.assertEqual(
            summary.summary_heading_label,
            'a-b'
        )

    def test_get_safe_shortname(self):
        existing_data = []
        exporter = QajsonExcelExporter()

        fn = 'Xi1039_B11_MBES_c1m_Prelim_r3_MULTI_crop.tif'
        summary1 = QajsonFileSummary(fn)
        safe_name = exporter._get_safe_shortname(summary1, existing_data)
        self.assertEqual(safe_name, 'Xi1039_B11_MBES_c1m')

        existing_data.append(summary1)


        fn = 'Xi1039_B11_MBES_c1m_LAT_Prelim_r4_MULTI_crop.tif'
        summary2 = QajsonFileSummary(fn)
        safe_name = exporter._get_safe_shortname(summary2, existing_data)
        self.assertEqual(safe_name, 'Xi1039_B11_MBES_c1m (1)')

        existing_data.append(summary2)

        fn = 'Zi1039_B11_MBES_c1m_LAT_Prelim_r4_MULTI_crop.tif'
        summary3 = QajsonFileSummary(fn)
        safe_name = exporter._get_safe_shortname(summary3, existing_data)
        self.assertEqual(safe_name, 'Zi1039_B11_MBES_c1m')

        existing_data.append(summary3)
