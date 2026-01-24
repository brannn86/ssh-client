# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for SSH Client
Builds a portable executable with all dependencies bundled
Config files (policies.json, totp_secrets.json, zt_ssh.db) are stored in the working directory
"""

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('policies.json', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'paramiko',
        'pyotp',
        'qrcode',
        'PIL',
        'db.db',
        'backend.auth',
        'backend.ssh_client',
        'gui.main_window',
        'gui.config',
        'gui.history_viewer',
        'models.policy',
        'cryptography',
        'bcrypt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ssh-client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)