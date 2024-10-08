# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import copy_metadata, collect_data_files


spec_root = os.path.abspath(SPECPATH)
qax_root = os.path.abspath(os.path.join(SPECPATH, '..'))

print(os.environ)

conda_prefix = os.path.join(os.path.expanduser("~"), "miniconda", "envs", "qax")
# epsg_data = os.path.abspath(os.path.join(conda_prefix , 'Library\\share\\epsg'))  # this dir doesn't exist
proj_data = os.path.abspath(os.path.join(conda_prefix , 'Library\\share\\proj'))
gdal_data = os.path.abspath(os.path.join(conda_prefix , 'Library\\share\\gdal'))

qt_platforms = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\platforms'))
qt_webengine_res = os.path.abspath(os.path.join(conda_prefix , 'Library\\resources\\*'))
qt_webengine = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin\\QtWebEngineProcess.exe'))
qt_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin\\*.dll'))
qml_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\qml'))
pyside2_libs = os.path.abspath(os.path.join(conda_prefix , 'Lib\\site-packages\\PySide2'))
styles_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\styles'))
platformthemes_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\platformthemes'))
geoservices_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\geoservices'))
ggoutlier_pngs = os.path.abspath(os.path.join(conda_prefix , 'Lib\\site-packages\\*.png'))

bin_dir = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin'))
hooks_dir = os.path.join(spec_root ,'hooks')

block_cipher = None

# build data reqs
datas = []
datas += collect_data_files('hyo2.qax', include_py_files=True)
datas += copy_metadata('hyo2.qax')
datas.append((proj_data ,"Library\\share\\proj"))
datas.append((gdal_data ,"Library\\share\\gdal"))
datas.append((qt_platforms ,"platforms"))
datas.append((qt_webengine_res ,"."))
datas.append((qt_webengine ,"."))
datas.append((qt_libs ,"."))
datas.append((qml_libs ,"."))
datas.append((pyside2_libs, "PySide2"))
datas.append((styles_libs, "styles"))
datas.append((platformthemes_libs, "plugins\\platformthemes"))
datas.append((geoservices_libs, "PySide2\\plugins\\geoservices"))
datas.append((r'..\docs\_build\html', "docs\_build\html"))
datas.append((ggoutlier_pngs ,"."))

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

# hack to workaround missing rasterio imports
# https://stackoverflow.com/a/69376916
import pkgutil
import rasterio
rasterio_packages = list()
for package in pkgutil.iter_modules(rasterio.__path__, prefix="rasterio."):
    rasterio_packages.append(package.name)
hiddenimports.extend(rasterio_packages)


a = Analysis(['cli.py'],
             pathex=[qax_root, bin_dir],
             binaries=[],
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[hooks_dir],
             runtime_hooks=['install/hooks.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='qax',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='QAX.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='qax')
