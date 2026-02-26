# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for RTMP Streaming Server
Creates a standalone Windows executable with all dependencies bundled
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all submodules that might be needed
hiddenimports = [
    # Our modules
    'server.server_manager',
    'server.ngrok_manager',
    'server.ndi_manager',
    'server.config_manager',
    'server.logger',
    'utils.helpers',
    # Dependencies
    'pyngrok',
    'pyngrok.conf',
    'pyngrok.ngrok',
    'customtkinter',
    'yaml',
    'av',
    'numpy',
]

# Try to add cyndilib hidden imports
try:
    hiddenimports += collect_submodules('cyndilib')
except Exception:
    hiddenimports.append('cyndilib')
    hiddenimports.append('cyndilib.sender')
    hiddenimports.append('cyndilib.video_frame')
    hiddenimports.append('cyndilib.wrapper')

# Collect customtkinter data files (themes, etc.)
datas = []
try:
    datas += collect_data_files('customtkinter')
except Exception:
    pass

a = Analysis(
    ['rtmp_server_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'PIL', 'pytest', 'scipy', 'sklearn'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)
