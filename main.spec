# main.spec
# -*- mode: python ; coding: utf-8 -*-
import re
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[os.path.dirname(os.path.abspath(SPECPATH))],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('core', 'core'),
        ('utils', 'utils'),
        ('resources', 'resources')
    ],
    hiddenimports=[
        'PyQt5.sip', 
        'ui.main_window', 'ui.action_editor', 
        'core.actions', 'core.clipboard_manager', 'core.folder_monitor', 'core.macro_engine',
        'utils.config', 'utils.logger',
        'platform', 'pynput', 'pyperclip', 'pyautogui', 'logging', 'json',
        'watchdog', 'watchdog.observers', 'watchdog.observers.api', 
        'watchdog.observers.polling', 'watchdog.observers.read_directory_changes',
        'watchdog.events', 'encodings.utf_8', 'encodings.cp949'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'tkinter', 'PySide2', 'PyQt6', 'IPython', 'PIL',
             'notebook', 'sphinx', 'docutils', 'pytest', 'unittest'],
    noarchive=False,
    optimize=2,
)


def remove_from_list(list_, patterns):
    for a in list_[:]:
        for pattern in patterns:
            if pattern.search(a[0]):
                list_.remove(a)
                break


qt5_excludes = [
    re.compile(r'PyQt5\.Qt(WebEngine|Location|Positioning|Multimedia|Sensors|WebChannel|WebSockets|XmlPatterns).*'),
    re.compile(r'PyQt5\.QtBluetooth.*'),
    re.compile(r'PyQt5\.QtDBus.*'),
    re.compile(r'PyQt5\.QtDesigner.*'),
    re.compile(r'PyQt5\.QtHelp.*'),
    re.compile(r'PyQt5\.QtMultimedia.*'),
    re.compile(r'PyQt5\.QtOpenGL.*'),
    re.compile(r'PyQt5\.QtPositioning.*'),
    re.compile(r'PyQt5\.QtPrintSupport.*'),
    re.compile(r'PyQt5\.QtQml.*'),
    re.compile(r'PyQt5\.QtQuick.*'),
    re.compile(r'PyQt5\.QtSensors.*'),
    re.compile(r'PyQt5\.QtSerialPort.*'),
    re.compile(r'PyQt5\.QtSql.*'),
    re.compile(r'PyQt5\.QtTest.*'),
    re.compile(r'PyQt5\.QtWebChannel.*'),
    re.compile(r'PyQt5\.QtWebEngine.*'),
    re.compile(r'PyQt5\.QtWebSockets.*'),
]

# 번역 파일 중 한국어와 영어만 유지
def keep_only_ko_en_translations(datas_list):
    result = []
    for entry in datas_list:
        path = entry[0]
        if path.startswith('PyQt5/Qt/translations'):
            if any(lang in path for lang in ['ko', 'en']):
                result.append(entry)
        else:
            result.append(entry)
    return result

remove_from_list(a.binaries, qt5_excludes)
remove_from_list(a.datas, qt5_excludes)

# 한국어와 영어 번역 파일만 유지
a.datas = keep_only_ko_en_translations(a.datas)

# LZMA 압축 사용
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher, name='pyz', compression='lzma')


exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

collect = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)


