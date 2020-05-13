# -*- mode: python ; coding: utf-8 -*-

import os


spec_root = os.path.abspath(SPECPATH)
qax_root = os.path.abspath(os.path.join(SPECPATH, '..'))

conda_prefix = os.environ['CONDA_PREFIX']
epsg_data = os.path.abspath(os.path.join(conda_prefix , 'Library\\share\\epsg'))
bin_dir = os.path.abspath(os.path.join(conda_prefix , 'Library\\bin'))
hooks_dir = os.path.join(spec_root ,'hooks')

block_cipher = None

a = Analysis(['cli.py'],
             pathex=[qax_root, bin_dir],
             binaries=[],
             datas=[(epsg_data ,"Library\\share\\.")],
             hiddenimports=['PySide2.QtPrintSupport','PySide2.QtWebChannel','PySide2.QtWebEngineCore', 'pyproj', 'hyo2.abc', 'hyo2.mate','hyo2.qax','hyo2.mate.qax.plugin', 'hyo2.qax.plugins.test'],
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
