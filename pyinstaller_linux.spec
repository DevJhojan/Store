# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('inventory_manager', 'inventory_manager'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'sqlite3',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.platypus',
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'inventory_manager',
        'inventory_manager.config',
        'inventory_manager.domain',
        'inventory_manager.repository',
        'inventory_manager.services',
        'inventory_manager.ui',
        'inventory_manager.sales',
        'inventory_manager.sales.domain',
        'inventory_manager.sales.repository',
        'inventory_manager.sales.services',
        'inventory_manager.sales.ui',
        'inventory_manager.inventory',
        'inventory_manager.inventory.domain',
        'inventory_manager.inventory.repository',
        'inventory_manager.inventory.services',
        'inventory_manager.inventory.ui',
        'inventory_manager.cash_closure',
        'inventory_manager.cash_closure.repository',
        'inventory_manager.cash_closure.services',
        'inventory_manager.cash_closure.ui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='StoreManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola (o True para debug)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

