"""
py2app 설정 파일 - MarkdownPro macOS 앱 빌드
사용법: python setup.py py2app
"""

from setuptools import setup
import os

APP = ['markdown_editor.py']

LIBFFI_CANDIDATES = [
    '/opt/homebrew/opt/libffi/lib/libffi.8.dylib',
    '/usr/local/opt/libffi/lib/libffi.8.dylib',
]
LIBFFI_FRAMEWORKS = [p for p in LIBFFI_CANDIDATES if os.path.exists(p)]

# assets/ 는 OPTIONS.resources 로 통째 복사 — DATA_FILES 에 다시 넣으면 이중 번들
DATA_FILES = ['icon.ico']

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'Nebula Note',
        'CFBundleDisplayName': 'Nebula Note',
        'CFBundleIdentifier': 'com.nebulanote.app',
        'CFBundleVersion': '3.0.0',
        'CFBundleShortVersionString': '3.0.0',
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # 다크 모드 지원
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Markdown Document',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': ['net.daringfireball.markdown'],
                'LSHandlerRank': 'Owner',
                'CFBundleTypeExtensions': ['md', 'markdown', 'mdown', 'mkd'],
            },
            {
                'CFBundleTypeName': 'Text Document',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': ['public.plain-text'],
                'LSHandlerRank': 'Alternate',
            },
        ],
        'UTExportedTypeDeclarations': [
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
    'packages': ['PyQt6', 'markdown', 'pygments'],
    'includes': [
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebChannel',
        'PyQt6.QtPrintSupport',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'importlib.util',
        'importlib',
        'html.entities',
        'html.parser',
        'html',
    ],
    'excludes': ['tkinter', 'test'],
    'frameworks': LIBFFI_FRAMEWORKS,
    'resources': ['icon.ico', 'assets'],
}

setup(
    name='Nebula Note',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
