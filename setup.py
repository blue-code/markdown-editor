"""
py2app 설정 파일 - Nebula Note macOS 앱 빌드
사용법: python setup.py py2app   (보통 build_dmg.sh / build_mas.sh 가 호출)
"""

import os
import glob

import zlib

from setuptools import setup

from app_version import APP_NAME, APP_VERSION, BUILD_NUMBER

APP = ['markdown_editor.py']
BUNDLE_ID = os.environ.get('NEBULA_BUNDLE_ID', 'com.blueCode.NebulaNote')
# build_mas.sh sets this after inspecting the bundled binaries; 12.0 is the floor for WKWebView printing APIs.
MIN_MACOS = os.environ.get('NEBULA_MIN_MACOS', '12.0')

if not hasattr(zlib, '__file__'):
    # python-build-standalone links zlib into the interpreter. py2app copies zlib's extension module
    # only so the zipped stdlib can be imported, which a built-in zlib already covers.
    from py2app.build_app import py2app as _py2app_command

    zlib.__file__ = None
    _original_copy_file = _py2app_command.copy_file

    def _copy_file(self, src, *args, **kwargs):
        if src is None:
            return (None, 0)
        return _original_copy_file(self, src, *args, **kwargs)

    _py2app_command.copy_file = _copy_file

LPROJ_DIRS = sorted(glob.glob('mas/lproj/*.lproj'))

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': BUNDLE_ID,
        'CFBundleVersion': BUILD_NUMBER,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleDevelopmentRegion': 'en',
        'CFBundleLocalizations': ['en', 'ko', 'ja', 'zh-Hans'],
        'CFBundleAllowMixedLocalizations': True,
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'LSMinimumSystemVersion': MIN_MACOS,
        'NSHumanReadableCopyright': 'Copyright © 2026 Byoungho Kim. All rights reserved.',
        'ITSAppUsesNonExemptEncryption': False,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # 다크 모드 지원
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Markdown Document',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': ['net.daringfireball.markdown'],
                'LSHandlerRank': 'Default',
                'CFBundleTypeExtensions': ['md', 'markdown', 'mdown', 'mkd'],
            },
            {
                'CFBundleTypeName': 'Text Document',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': ['public.plain-text'],
                'LSHandlerRank': 'Alternate',
            },
        ],
        'UTImportedTypeDeclarations': [
            {
                'UTTypeIdentifier': 'net.daringfireball.markdown',
                'UTTypeDescription': 'Markdown Document',
                'UTTypeConformsTo': ['public.plain-text'],
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['md', 'markdown', 'mdown', 'mkd'],
                    'public.mime-type': ['text/markdown'],
                },
            },
        ],
    },
    'packages': ['markdown', 'pygments'],
    'includes': [
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.QtPrintSupport',
        'PyQt6.sip',
        'objc',
        'Foundation',
        'AppKit',
        'WebKit',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'html.entities',
        'html.parser',
    ],
    # Qt WebEngine (Chromium) is rejected by the Mac App Store; macOS uses WKWebView instead.
    'excludes': ['tkinter', 'test', 'unittest', 'PIL', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
                 'PyQt6.QtWebChannel', 'PyQt6.QtNetwork', 'PyQt6.QtBluetooth', 'PyQt6.QtMultimedia',
                 'PyQt6.QtPositioning', 'PyQt6.QtSensors', 'PyQt6.QtQml', 'PyQt6.QtQuick'],
    # assets/ (Mermaid, MathJax) is copied whole into Contents/Resources/assets.
    'resources': ['icon.ico', 'assets'] + LPROJ_DIRS,
}

setup(
    name=APP_NAME,
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
