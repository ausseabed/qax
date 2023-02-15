import os
from pathlib import Path
import unittest

from ausseabed.qajson.model import QajsonFile, QajsonParam, QajsonInputs, \
    QajsonOutputs, QajsonInfo, QajsonRoot, QajsonQa, QajsonDataLevel
from ausseabed.qajson.parser import QajsonParser
from hyo2.qax.lib.plugin import QaxPlugins, QaxConfig
from hyo2.qax.lib.qajson_util import QajsonExcelExporter, QajsonTableSummary
from hyo2.qax.app.gui_settings import GuiSettings

class TestParser(unittest.TestCase):

    def test_qajson_read(self):
        here = os.path.abspath(os.path.dirname(__file__))
        test_file = Path(os.path.join(here, "test.json"))

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



