# -*- mode: python ; coding: utf-8 -*-
# BUILD CMD: python -m PyInstaller --log-level=ERROR ./client.spec

a = Analysis(
    ['client.py'],
    pathex=[],
    binaries=[('vpn/windows/windows_vpn.dll','vpn/windows/')],
    datas=[('data/images/load.zip', 'data/images/load.zip'), ('data/block/', 'data/block/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
