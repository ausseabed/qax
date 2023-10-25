# -*- mode: python ; coding: utf-8 -*-

import os


spec_root = os.path.abspath(SPECPATH)
qax_root = os.path.abspath(os.path.join(SPECPATH, '..'))

print(os.environ)

conda_prefix = os.path.join(os.path.expanduser("~"), "miniconda", "envs", "build-qax")
# epsg_data = os.path.abspath(os.path.join(conda_prefix , 'Library\\share\\epsg'))  # this dir doesn't exist
proj_data = os.path.abspath(os.path.join(conda_prefix , 'Library\\share\\proj'))

qt_platforms = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\platforms'))
qt_webengine_res = os.path.abspath(os.path.join(conda_prefix , 'Library\\resources\\*'))
qt_webengine = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin\\QtWebEngineProcess.exe'))
qt_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin\\*.dll'))
qml_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\qml'))
pyside2_libs = os.path.abspath(os.path.join(conda_prefix , 'Lib\\site-packages\\PySide2'))
styles_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\styles'))
platformthemes_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\platformthemes'))
geoservices_libs = os.path.abspath(os.path.join(conda_prefix , 'Library\\plugins\\geoservices'))

bin_dir = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin'))
hooks_dir = os.path.join(spec_root ,'hooks')

block_cipher = None

a = Analysis(['cli.py'],
             pathex=[qax_root, bin_dir],
             binaries=[],
             datas=[
                 (proj_data ,"Library\\share\\proj"),
                 (qt_platforms ,"platforms"),
                 (qt_webengine_res ,"."),
                 (qt_webengine ,"."),
                 (qt_libs ,"."),
                 (qml_libs ,"."),
                 (pyside2_libs, "PySide2"),
                 (styles_libs, "styles"),
                 (platformthemes_libs, "plugins\\platformthemes"),
                 (geoservices_libs, "geoservices"),
                 (r'..\version.txt', "."),
                 (r'..\docs\_build\html', "docs\_build\html"),
             ],
             hiddenimports=['PySide2.QtPrintSupport','PySide2.QtWebChannel','PySide2.QtWebEngineCore','PySide2.QtQuick', 'pyproj', 'hyo2.abc', 'hyo2.mate','hyo2.qax','hyo2.mate.qax.plugin', 'hyo2.qax.plugins.test', 'hyo2.qax.plugins.placeholder', 'ausseabed.mbesgc', 'ausseabed.mbesgc.qax.plugin', 'ausseabed.findergc', 'ausseabed.findergc.qax.plugin'],
             hookspath=[hooks_dir],
             runtime_hooks=[],
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
