# -*- mode: python ; coding: utf-8 -*-

import os

spec_root = os.path.abspath(SPECPATH)

for k,v in os.environ.items():
    print(f"{k}={v}")

hooks_dir = os.path.join(spec_root, "hooks")
runtime_hooks = [os.path.join(spec_root, "hooks.py")]

a = Analysis(
    ["cli.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[hooks_dir],
    runtime_hooks=runtime_hooks,
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="qax",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon="QAX.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="qax",
)
