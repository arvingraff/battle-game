# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['battlegame.py'],
    pathex=[],
    binaries=[],
    datas=[('321go.mp3', '.'), ('scary-scream.mp3', '.'), ('lala.mp3', '.'), ('coin.mp3', '.'), ('coolwav.mp3', '.'), ('fart.mp3', '.'), ('funk.mp3', '.'), ('playmusic.mp3', '.'), ('ball.jpg', '.'), ('cutevideo.mp4', '.'), ('grandma.mp4', '.'), ('icon.png', '.'), ('network.py', '.'), ('survival_highscores.json', '.'), ('mom_mode_highscores.json', '.')],
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
    [],
    exclude_binaries=True,
    name='BattleGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.png'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='BattleGame',
)

app = BUNDLE(
    coll,
    name='BattleGame.app',
    icon='icon.png',
    bundle_identifier=None,
)
