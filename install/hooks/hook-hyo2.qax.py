from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = [
    *collect_data_files("hyo2.qax"),
    *copy_metadata("hyo2.qax"),
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
    'ausseabed.mbespc',
    'ausseabed.mbespc.qax.plugin',
    'ausseabed.findergc',
    'ausseabed.findergc.qax.plugin',
    'ausseabed.ggoutlier',
    'ausseabed.ggoutlier.qax.plugin',
    'ggoutlier',
    'win32'
]