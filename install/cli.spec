# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['cli.py'],
             pathex=['C:\\Users\\lachlan\\qax'],
             binaries=[],
             datas=[("C:\\Users\\lachlan\\Miniconda3\\envs\\qaxenv\\Library\\share\\epsg","Library\\share\\.")],
             hiddenimports=['PySide2.QtPrintSupport', 'pyproj', 'hyo2.abc', 'hyo2.mate','hyo2.qax','hyo2.mate.qax.plugin', 'hyo2.qax.plugins.test'],
             hookspath=["hooks"],
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
