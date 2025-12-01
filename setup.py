"""
py2app 설정 파일 - MarkdownPro macOS 앱 빌드
사용법: python setup.py py2app
"""

from setuptools import setup

APP = ['markdown_editor.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'MarkdownPro',
        'CFBundleDisplayName': 'MarkdownPro',
        'CFBundleIdentifier': 'com.markdownpro.app',
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
    ],
    'excludes': ['tkinter', 'test'],
    'resources': [],
}

setup(
    name='MarkdownPro',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
