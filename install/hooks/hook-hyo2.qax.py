from PyInstaller.utils.hooks import collect_data_files, copy_metadata
from PySide2.QtCore import QLibraryInfo

plugins_dir = QLibraryInfo.location(QLibraryInfo.PluginsPath)

datas = [
    *collect_data_files("hyo2.qax"),
    *copy_metadata("hyo2.qax"),
    (f"{plugins_dir}/geoservices", "PySide2/plugins/geoservices"),
    (f"{plugins_dir}/platformthemes", "PySide2/plugins/platformthemes"),
]

hiddenimports = [
    'PySide2.QtPrintSupport',
    'PySide2.QtWebChannel',
    'PySide2.QtWebEngineCore',
    'PySide2.QtQuick',
    'pyproj',
    'hyo2.mate',
    'hyo2.qax',
    'hyo2.mate.qax.plugin',
    'hyo2.qax.plugins.test',
    'hyo2.qax.plugins.placeholder',
    'ausseabed.mbesgc',
    'ausseabed.mbesgc.qax.plugin',
    'ausseabed.findergc',
    'ausseabed.findergc.qax.plugin',
    'ausseabed.ggoutlier',
    'ausseabed.ggoutlier.qax.plugin',
    'ggoutlier',
    'win32'
]