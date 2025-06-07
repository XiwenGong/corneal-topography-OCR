# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['d:\\biyesheji\\corneal-topography-OCR\\onefile_scripts\\edit_all_in_one.py'],
    pathex=[],
    binaries=[],
    datas=[('d:\\biyesheji\\corneal-topography-OCR\\mu_ban', 'mu_ban'), ('d:\\biyesheji\\corneal-topography-OCR\\lin_shi', 'lin_shi')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='edit_all_in_one',
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
