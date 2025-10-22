# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Get all media files
media_files = [
    ('ball.jpg', '.'),
    ('coin.mp3', '.'),
    ('fart.mp3', '.'),
    ('playmusic.mp3', '.'),
    ('scary-scream.mp3', '.'),
    ('coolwav.mp3', '.'),
    ('321go.mp3', '.'),
    ('funk.mp3', '.'),
    ('lala.mp3', '.'),
    ('cutevideo.mp4', '.'),
    ('grandma.mp4', '.'),
    ('fart.MP4', '.'),
    ('survival_highscores.json', '.'),
]

a = Analysis(
    ['battlegame.py'],
    pathex=[],
    binaries=[],
    datas=media_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='BattleGame',
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

app = BUNDLE(
    exe,
    name='BattleGame.app',
    icon=None,
    bundle_identifier=None,
)
