# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file per RTMP Server GUI
Crea un eseguibile standalone per Windows
"""

block_cipher = None

a = Analysis(
    ['rtmp_server_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pyngrok',
        'pyngrok.conf',
        'pyngrok.ngrok',
        'server.server_manager',
        'server.ngrok_manager',
        'utils.helpers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'PIL', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RTMPServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Nasconde console, mostra solo GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
