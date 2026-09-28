#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nebula Note - Pure & Sexy Markdown Editor
Features: Mermaid 전체 지원, 포커스 모드, 문서 개요, 통계, 스니펫, 다국어(ko/en/ja/zh) 등
"""

import atexit
import base64
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QPlainTextEdit, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QDialog, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit, QListWidget, QListWidgetItem,
    QTabWidget, QGridLayout, QScrollArea, QCompleter, QDialogButtonBox,
    QGroupBox, QCheckBox, QSlider, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QTreeView, QStyle, QInputDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QUrl, QEvent, QLocale, QTranslator, QLibraryInfo, QFileInfo,
    pyqtSignal, QRegularExpression, QDir
)
from PyQt6.QtGui import (
    QFont, QAction, QActionGroup, QKeySequence, QTextCharFormat, QSyntaxHighlighter,
    QColor, QTextCursor, QShortcut, QTextDocument, QFileSystemModel, QIcon
)

import file_io
from app_paths import resource_path, user_file
from file_io import FileAccessError
from i18n import (
    LANGUAGE_NAMES, SUPPORTED_LANGUAGES, current_language, detect_system_language,
    set_language, tr
)
from localized_content import (
    FEATURED_MERMAID_IDS, autocomplete_items, default_snippets, example_templates, mermaid_examples
)
from markdown_tools import format_markdown_tables
from mermaid_utils import extract_mermaid_blocks
from preview_html import (
    build_mermaid_viewer_shell, build_preview_shell, build_standalone_html, inline_local_images,
    markdown_to_html, mermaid_show_script, preview_render_script
)
from version import APP_NAME, __version__
from web_view import WebView

CONFIG_FILE = user_file(".markdownpro_config.json")
BACKUP_DIR = user_file(".markdownpro_backups")
SNIPPETS_FILE = user_file(".markdownpro_snippets.json")

# Static HTML shell pages for the web views are written here once per launch.
SHELL_DIR = tempfile.mkdtemp(prefix="nebula-note-")
atexit.register(shutil.rmtree, SHELL_DIR, True)


def bundled_assets():
    """file:// URLs of the vendored JavaScript libraries (works offline and inside the sandbox).

    They are copied next to the shell pages because a sandboxed WKWebView can only read the
    folder of the page it loads, not the app bundle.
    """
    urls = {}
    for key, name in (("mermaid", "mermaid.min.js"), ("mathjax", "tex-svg.js")):
        target = os.path.join(SHELL_DIR, name)
        if not os.path.exists(target):
            shutil.copyfile(resource_path(os.path.join("assets", "vendor", name)), target)
        urls[key] = QUrl.fromLocalFile(target).toString()
    return urls


def write_shell(name, html):
    path = os.path.join(SHELL_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def native_shortcut(sequence):
    """Shortcut text as the platform shows it (e.g. ⌘S on macOS, Ctrl+S elsewhere)."""
    return QKeySequence(sequence).toString(QKeySequence.SequenceFormat.NativeText)


def copy_labels():
    return {"copy": tr("preview.copy"), "copied": tr("preview.copied"), "failed": tr("preview.copy_failed")}


def apply_native_appearance(dark_mode):
    """Match the macOS title bar and native dialogs to the app theme."""
    if sys.platform != "darwin":
        return
    try:
        from AppKit import NSApp, NSAppearance, NSAppearanceNameAqua, NSAppearanceNameDarkAqua
    except ImportError:
        return
    if NSApp() is not None:
        name = NSAppearanceNameDarkAqua if dark_mode else NSAppearanceNameAqua
        NSApp().setAppearance_(NSAppearance.appearanceNamed_(name))


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

# 스타일
LIGHT_STYLE = """
QMainWindow, QWidget { background-color: #ffffff; color: #333333; }
QPlainTextEdit, QTextEdit { background-color: #fafafa; color: #333333; border: 1px solid #e0e0e0; border-radius: 4px; font-family: 'Menlo', 'Consolas', monospace; font-size: 14px; padding: 10px; selection-background-color: #007AFF; }
QToolBar { background-color: #f5f5f5; border-bottom: 1px solid #e0e0e0; spacing: 5px; padding: 5px; }
QToolBar QToolButton { background-color: transparent; border: none; border-radius: 4px; padding: 6px 10px; }
QToolBar QToolButton:hover { background-color: #e0e0e0; }
QMenuBar { background-color: #f5f5f5; border-bottom: 1px solid #e0e0e0; }
QMenuBar::item:selected { background-color: #e0e0e0; }
QMenu { background-color: #ffffff; border: 1px solid #e0e0e0; }
QMenu::item:selected { background-color: #007AFF; color: white; }
QStatusBar { background-color: #f5f5f5; border-top: 1px solid #e0e0e0; }
QSplitter::handle { background-color: #e0e0e0; }
QPushButton { background-color: #007AFF; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background-color: #0056b3; }
QComboBox, QSpinBox, QLineEdit { border: 1px solid #e0e0e0; border-radius: 4px; padding: 6px; background-color: white; }
QListWidget, QTreeWidget { border: 1px solid #e0e0e0; border-radius: 4px; background-color: white; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #007AFF; color: white; }
QTabWidget::pane { border: 1px solid #e0e0e0; }
QTabBar::tab { background-color: #f0f0f0; border: 1px solid #e0e0e0; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background-color: white; }
QSlider::groove:horizontal { height: 6px; background: #e0e0e0; border-radius: 3px; }
QSlider::handle:horizontal { background: #007AFF; width: 16px; margin: -5px 0; border-radius: 8px; }
QProgressBar { border: 1px solid #e0e0e0; border-radius: 4px; text-align: center; }
QProgressBar::chunk { background-color: #007AFF; border-radius: 3px; }
QGroupBox { font-weight: bold; border: 1px solid #e0e0e0; border-radius: 4px; margin-top: 10px; padding-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
"""

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
QPlainTextEdit, QTextEdit { background-color: #252526; color: #d4d4d4; border: 1px solid #3c3c3c; border-radius: 4px; font-family: 'Menlo', 'Consolas', monospace; font-size: 14px; padding: 10px; selection-background-color: #264f78; }
QToolBar { background-color: #2d2d2d; border-bottom: 1px solid #3c3c3c; spacing: 5px; padding: 5px; }
QToolBar QToolButton { background-color: transparent; color: #d4d4d4; border: none; border-radius: 4px; padding: 6px 10px; }
QToolBar QToolButton:hover { background-color: #3c3c3c; }
QMenuBar { background-color: #2d2d2d; border-bottom: 1px solid #3c3c3c; }
QMenuBar::item:selected { background-color: #3c3c3c; }
QMenu { background-color: #2d2d2d; border: 1px solid #3c3c3c; }
QMenu::item:selected { background-color: #264f78; color: white; }
QStatusBar { background-color: #2d2d2d; border-top: 1px solid #3c3c3c; }
QSplitter::handle { background-color: #3c3c3c; }
QPushButton { background-color: #0e639c; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background-color: #1177bb; }
QComboBox, QSpinBox, QLineEdit { border: 1px solid #3c3c3c; border-radius: 4px; padding: 6px; background-color: #3c3c3c; color: #d4d4d4; }
QListWidget, QTreeWidget { border: 1px solid #3c3c3c; border-radius: 4px; background-color: #252526; color: #d4d4d4; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #264f78; color: white; }
QTabWidget::pane { border: 1px solid #3c3c3c; }
QTabBar::tab { background-color: #2d2d2d; border: 1px solid #3c3c3c; color: #d4d4d4; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #1e1e1e; }
QSlider::groove:horizontal { height: 6px; background: #3c3c3c; border-radius: 3px; }
QSlider::handle:horizontal { background: #0e639c; width: 16px; margin: -5px 0; border-radius: 8px; }
QProgressBar { border: 1px solid #3c3c3c; border-radius: 4px; text-align: center; background: #252526; color: #d4d4d4; }
QProgressBar::chunk { background-color: #0e639c; border-radius: 3px; }
QGroupBox { font-weight: bold; border: 1px solid #3c3c3c; border-radius: 4px; margin-top: 10px; padding-top: 10px; color: #d4d4d4; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
"""

# 포커스 모드 스타일
FOCUS_STYLE_LIGHT = """
QMainWindow { background-color: #f8f8f8; }
QPlainTextEdit { background-color: #f8f8f8; color: #333; border: none; font-size: 18px; padding: 50px; max-width: 700px; }
"""

FOCUS_STYLE_DARK = """
QMainWindow { background-color: #1a1a1a; }
QPlainTextEdit { background-color: #1a1a1a; color: #ccc; border: none; font-size: 18px; padding: 50px; max-width: 700px; }
"""


# 이모지 (카테고리 키는 i18n의 emoji.cat.* 와 매칭)
def emoji_display_name(emoji: str) -> str:
    """Return a readable name for a (possibly multi-codepoint) emoji."""
    parts = []
    for ch in emoji:
        try:
            name = unicodedata.name(ch)
        except ValueError:
            name = ""
        if name and "VARIATION SELECTOR" not in name:
            parts.append(name)
    return " ".join(parts).title()


EMOJI_LIST = {
    "smileys": ["😀", "😃", "😄", "😁", "😅", "😂", "🤣", "😊", "😇", "🙂", "😉", "😍", "🥰", "😎", "🤔", "😴"],
    "gestures": ["👍", "👎", "👌", "✌️", "🤞", "🤝", "👏", "🙌", "💪", "🙏", "👋", "✋", "🤚", "🖐️", "👆", "👇"],
    "symbols": ["❤️", "🧡", "💛", "💚", "💙", "💜", "⭐", "🌟", "✨", "💫", "🔥", "💯", "✅", "❌", "⚠️", "💡"],
    "objects": ["📁", "📂", "📄", "📝", "✏️", "📊", "📈", "📉", "🗓️", "⏰", "🔗", "🔒", "🔓", "🔑", "💾", "💿"],
    "arrows": ["➡️", "⬅️", "⬆️", "⬇️", "↗️", "↘️", "↙️", "↖️", "↕️", "↔️", "🔄", "🔃", "◀️", "▶️", "🔼", "🔽"],
}


# ============== 유틸리티 클래스 ==============

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setup_formats()

    def setup_formats(self):
        self.formats = {}
        colors = {
            'header': '#569cd6' if self.dark_mode else '#0066cc',
            'bold': '#ce9178' if self.dark_mode else '#9c27b0',
            'italic': '#b5cea8' if self.dark_mode else '#2e7d32',
            'code': '#d7ba7d' if self.dark_mode else '#d84315',
            'link': '#4ec9b0' if self.dark_mode else '#0277bd',
            'list': '#c586c0' if self.dark_mode else '#6a1b9a',
            'mermaid': '#dcdcaa' if self.dark_mode else '#795548',
        }

        for name, color in colors.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if name in ['header', 'mermaid']:
                fmt.setFontWeight(QFont.Weight.Bold)
            if name == 'italic':
                fmt.setFontItalic(True)
            self.formats[name] = fmt

        self.rules = [
            (QRegularExpression(pattern), fmt_name) for pattern, fmt_name in [
                (r'^#{1,6}\s.*$', 'header'),
                (r'\*\*[^*]+\*\*', 'bold'),
                (r'(?<!\*)\*(?!\*)[^*]+\*(?!\*)', 'italic'),
                (r'`[^`]+`', 'code'),
                (r'\[([^\]]+)\]\([^)]+\)', 'link'),
                (r'^\s*[-*+]\s', 'list'),
                (r'^\s*\d+\.\s', 'list'),
                (r'^```mermaid', 'mermaid'),
                (r'^```.*$', 'code'),
            ]
        ]

    def highlightBlock(self, text):
        for regex, fmt_name in self.rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(),
                               self.formats.get(fmt_name, QTextCharFormat()))


class DocumentStats:
    """문서 통계 계산"""

    @staticmethod
    def calculate(text):
        lines = text.split('\n')
        words = text.split()
        chars = len(text)
        chars_no_space = len(text.replace(' ', '').replace('\n', ''))

        # 읽기 시간 (평균 200단어/분)
        read_time = max(1, len(words) // 200)

        return {
            'lines': len(lines),
            'words': len(words),
            'chars': chars,
            'chars_no_space': chars_no_space,
            'paragraphs': len([p for p in text.split('\n\n') if p.strip()]),
            'headers': len(re.findall(r'^#{1,6}\s', text, re.MULTILINE)),
            'links': len(re.findall(r'\[([^\]]+)\]\([^)]+\)', text)),
            'images': len(re.findall(r'!\[([^\]]*)\]\([^)]+\)', text)),
            'code_blocks': len(re.findall(r'```[\s\S]*?```', text)),
            'mermaid_blocks': len(re.findall(r'```mermaid[\s\S]*?```', text)),
            'read_time': read_time,
        }


def ok_cancel_buttons(dialog):
    btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    btns.accepted.connect(dialog.accept)
    btns.rejected.connect(dialog.reject)
    return btns


# ============== 다이얼로그 ==============

class TableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("table.title"))
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        grid = QGridLayout()
        grid.addWidget(QLabel(tr("table.rows")), 0, 0)
        self.rows = QSpinBox()
        self.rows.setRange(1, 20)
        self.rows.setValue(3)
        grid.addWidget(self.rows, 0, 1)

        grid.addWidget(QLabel(tr("table.cols")), 1, 0)
        self.cols = QSpinBox()
        self.cols.setRange(1, 10)
        self.cols.setValue(3)
        grid.addWidget(self.cols, 1, 1)
        layout.addLayout(grid)

        self.header_check = QCheckBox(tr("table.include_header"))
        self.header_check.setChecked(True)
        layout.addWidget(self.header_check)

        self.align_combo = QComboBox()
        self.align_combo.addItems([tr("table.align_left"), tr("table.align_center"), tr("table.align_right")])
        layout.addWidget(self.align_combo)

        layout.addWidget(ok_cancel_buttons(self))

    def get_markdown(self):
        r, c = self.rows.value(), self.cols.value()
        sep = [":------", ":------:", "------:"][self.align_combo.currentIndex()]

        lines = []
        if self.header_check.isChecked():
            lines.append("| " + " | ".join([tr("table.header_cell", index=i + 1) for i in range(c)]) + " |")
            lines.append("| " + " | ".join([sep for _ in range(c)]) + " |")
            r -= 1
        for _ in range(r):
            lines.append("| " + " | ".join(["     " for _ in range(c)]) + " |")
        return "\n".join(lines)


class LinkDialog(QDialog):
    def __init__(self, parent=None, selected=""):
        super().__init__(parent)
        self.setWindowTitle(tr("link.title"))
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("link.text")))
        self.text_edit = QLineEdit(selected)
        layout.addWidget(self.text_edit)

        layout.addWidget(QLabel(tr("link.url")))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://")
        layout.addWidget(self.url_edit)

        layout.addWidget(QLabel(tr("link.tooltip")))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(tr("link.tooltip_placeholder"))
        layout.addWidget(self.title_edit)

        layout.addWidget(ok_cancel_buttons(self))

    def get_markdown(self):
        text = self.text_edit.text() or tr("link.default_text")
        url = self.url_edit.text() or "#"
        title = self.title_edit.text()
        if title:
            return f'[{text}]({url} "{title}")'
        return f"[{text}]({url})"


class ImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("image.title"))
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(tr("image.alt")))
        self.alt = QLineEdit()
        layout.addWidget(self.alt)

        layout.addWidget(QLabel(tr("image.path")))
        url_layout = QHBoxLayout()
        self.url = QLineEdit()
        url_layout.addWidget(self.url)
        browse = QPushButton(tr("image.browse"))
        browse.clicked.connect(self.browse)
        url_layout.addWidget(browse)
        layout.addLayout(url_layout)

        layout.addWidget(QLabel(tr("image.size")))
        size_layout = QHBoxLayout()
        self.width = QSpinBox()
        self.width.setRange(0, 2000)
        self.width.setSpecialValueText(tr("common.auto"))
        size_layout.addWidget(QLabel(tr("image.width")))
        size_layout.addWidget(self.width)
        self.height = QSpinBox()
        self.height.setRange(0, 2000)
        self.height.setSpecialValueText(tr("common.auto"))
        size_layout.addWidget(QLabel(tr("image.height")))
        size_layout.addWidget(self.height)
        layout.addLayout(size_layout)

        layout.addWidget(ok_cancel_buttons(self))

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("image.select_title"), "", tr("image.filter"))
        if path:
            self.url.setText(path)

    def get_markdown(self):
        alt = self.alt.text() or tr("image.default_alt")
        url = self.url.text() or "image.png"
        md = f"![{alt}]({url})"

        # HTML 크기 지정
        w, h = self.width.value(), self.height.value()
        if w > 0 or h > 0:
            style = []
            if w > 0:
                style.append(f"width: {w}px")
            if h > 0:
                style.append(f"height: {h}px")
            md = f'<img src="{url}" alt="{alt}" style="{"; ".join(style)}">'
        return md


class EmojiDialog(QDialog):
    emoji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("emoji.title"))
        self.setMinimumSize(400, 350)
        layout = QVBoxLayout(self)

        # 검색
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("emoji.search"))
        self.search.textChanged.connect(self.filter_emoji)
        layout.addWidget(self.search)

        tabs = QTabWidget()
        self.emoji_buttons = []

        for cat_key, emojis in EMOJI_LIST.items():
            cat = tr(f"emoji.cat.{cat_key}")
            w = QWidget()
            grid = QGridLayout(w)
            grid.setContentsMargins(8, 8, 8, 8)
            grid.setSpacing(8)
            for i, e in enumerate(emojis):
                btn = QPushButton(e)
                btn.setFixedSize(56, 56)
                btn.setFont(QFont("", 28))
                btn.setStyleSheet("padding: 6px 4px;")
                name = emoji_display_name(e)
                btn.setToolTip(f"{e} {name or cat}")
                btn.setProperty("emoji_name", name.lower())
                btn.setProperty("emoji_category", f"{cat} {cat_key}".lower())
                btn.clicked.connect(lambda _, em=e: self.select(em))
                grid.addWidget(btn, i // 8, i % 8)
                self.emoji_buttons.append(btn)
            tabs.addTab(w, cat)
        layout.addWidget(tabs)

    def filter_emoji(self, text):
        query = text.strip().lower()
        for btn in self.emoji_buttons:
            name = btn.property("emoji_name") or ""
            category = btn.property("emoji_category") or ""
            visible = not query or query in btn.text() or query in name or query in category
            btn.setVisible(visible)

    def select(self, emoji):
        self.emoji_selected.emit(emoji)
        self.accept()


class SnippetDialog(QDialog):
    def __init__(self, snippets, parent=None):
        super().__init__(parent)
        self.snippets = snippets
        self.setWindowTitle(tr("snippet.title"))
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout(self)

        # 스니펫 목록
        h_layout = QHBoxLayout()

        self.list = QListWidget()
        self.update_list()
        self.list.currentItemChanged.connect(self.on_select)
        h_layout.addWidget(self.list)

        # 편집 영역
        edit_layout = QVBoxLayout()

        edit_layout.addWidget(QLabel(tr("snippet.trigger")))
        self.trigger_edit = QLineEdit()
        edit_layout.addWidget(self.trigger_edit)

        edit_layout.addWidget(QLabel(tr("snippet.content")))
        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Menlo", 11))
        edit_layout.addWidget(self.content_edit)

        btn_layout = QHBoxLayout()
        for label, slot in [(tr("common.save"), self.save_snippet),
                            (tr("common.delete"), self.delete_snippet),
                            (tr("common.new"), self.new_snippet)]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_layout.addWidget(btn)

        edit_layout.addLayout(btn_layout)
        h_layout.addLayout(edit_layout)

        layout.addLayout(h_layout)

        close_btn = QPushButton(tr("common.close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def update_list(self):
        self.list.clear()
        for trigger in sorted(self.snippets.keys()):
            self.list.addItem(trigger)

    def on_select(self, current, prev):
        if current:
            trigger = current.text()
            self.trigger_edit.setText(trigger)
            self.content_edit.setPlainText(self.snippets.get(trigger, ""))

    def save_snippet(self):
        trigger = self.trigger_edit.text().strip()
        if trigger:
            self.snippets[trigger] = self.content_edit.toPlainText()
            self.update_list()

    def delete_snippet(self):
        trigger = self.trigger_edit.text().strip()
        if trigger in self.snippets:
            del self.snippets[trigger]
            self.update_list()
            self.trigger_edit.clear()
            self.content_edit.clear()

    def new_snippet(self):
        self.trigger_edit.clear()
        self.content_edit.clear()
        self.trigger_edit.setFocus()


class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle(tr("find.title"))
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)

        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel(tr("find.find")))
        self.find_edit = QLineEdit()
        self.find_edit.returnPressed.connect(self.find_next)
        find_layout.addWidget(self.find_edit)
        layout.addLayout(find_layout)

        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel(tr("find.replace")))
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)

        opt_layout = QHBoxLayout()
        self.case_check = QCheckBox(tr("find.case"))
        opt_layout.addWidget(self.case_check)
        self.whole_check = QCheckBox(tr("find.whole"))
        opt_layout.addWidget(self.whole_check)
        self.regex_check = QCheckBox(tr("find.regex"))
        opt_layout.addWidget(self.regex_check)
        layout.addLayout(opt_layout)

        btn_layout = QHBoxLayout()
        for label, slot in [(tr("find.next"), self.find_next),
                            (tr("find.prev"), self.find_prev),
                            (tr("find.replace_one"), self.replace_one),
                            (tr("find.replace_all"), self.replace_all)]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    def find_next(self):
        self._find(backward=False)

    def find_prev(self):
        self._find(backward=True)

    def _find(self, backward=False):
        text = self.find_edit.text()
        if not text:
            return

        flags = QTextDocument.FindFlag(0)
        if self.case_check.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_check.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        if backward:
            flags |= QTextDocument.FindFlag.FindBackward

        found = self.editor.find(text, flags)
        if not found:
            cursor = self.editor.textCursor()
            if backward:
                cursor.movePosition(QTextCursor.MoveOperation.End)
            else:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, flags)

        self.result_label.setText(tr("find.found") if found else tr("find.not_found"))

    def replace_one(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self):
        text = self.find_edit.text()
        if not text:
            return

        content = self.editor.toPlainText()

        if self.regex_check.isChecked():
            flags = 0 if self.case_check.isChecked() else re.IGNORECASE
            try:
                new_content, count = re.subn(text, self.replace_edit.text(), content, flags=flags)
            except re.error as e:
                self.result_label.setText(str(e))
                return
        elif self.case_check.isChecked():
            count = content.count(text)
            new_content = content.replace(text, self.replace_edit.text())
        else:
            pattern = re.compile(re.escape(text), re.IGNORECASE)
            count = len(pattern.findall(content))
            new_content = pattern.sub(lambda _m: self.replace_edit.text(), content)

        self.editor.setPlainText(new_content)
        self.result_label.setText(tr("find.replaced", count=count))


class StatsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("stats.title"))
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)

        groups = [
            (tr("stats.basic"), [
                (tr("stats.lines"), stats['lines']),
                (tr("stats.words"), stats['words']),
                (tr("stats.chars"), stats['chars']),
                (tr("stats.chars_no_space"), stats['chars_no_space']),
                (tr("stats.paragraphs"), stats['paragraphs']),
                (tr("stats.read_time"), tr("stats.minutes", count=stats['read_time'])),
            ]),
            (tr("stats.markdown"), [
                (tr("stats.headers"), stats['headers']),
                (tr("stats.links"), stats['links']),
                (tr("stats.images"), stats['images']),
                (tr("stats.code_blocks"), stats['code_blocks']),
                (tr("stats.mermaid"), stats['mermaid_blocks']),
            ]),
        ]
        for title, items in groups:
            group = QGroupBox(title)
            grid = QGridLayout(group)
            for i, (label, value) in enumerate(items):
                grid.addWidget(QLabel(label + ":"), i, 0)
                grid.addWidget(QLabel(str(value)), i, 1)
            layout.addWidget(group)

        close_btn = QPushButton(tr("common.close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ============== Mermaid 뷰어 ==============

class MermaidViewer(QMainWindow):
    """Mermaid 다이어그램 전용 뷰어 - 확대/축소, 전체화면, 내보내기"""

    def __init__(self, mermaid_code="", dark_mode=False, parent=None, mermaid_blocks=None, current_index=0):
        super().__init__(parent)
        self.mermaid_blocks = mermaid_blocks or []
        self.current_index = current_index
        self.mermaid_code = mermaid_code
        self.dark_mode = dark_mode
        self.zoom_level = 100
        self.is_fullscreen = False
        self.pending_save_path = None
        self.setup_ui()
        self.load_shell()
        self.set_mermaid_blocks(self.mermaid_blocks, self.current_index, fallback_code=self.mermaid_code)

    def setup_ui(self):
        self.setWindowTitle(tr("viewer.title"))
        self.setMinimumSize(1000, 750)
        self.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QWidget()
        toolbar.setFixedHeight(55)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(15, 8, 15, 8)

        # 다이어그램 이동
        self.prev_btn = QPushButton(tr("viewer.prev"))
        self.prev_btn.clicked.connect(self.prev_diagram)
        tb_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("0/0")
        self.page_label.setFixedWidth(70)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(self.page_label)

        self.next_btn = QPushButton(tr("viewer.next"))
        self.next_btn.clicked.connect(self.next_diagram)
        tb_layout.addWidget(self.next_btn)

        tb_layout.addSpacing(10)

        # 줌 컨트롤
        zoom_out = QPushButton("-")
        zoom_out.setFixedSize(36, 36)
        zoom_out.setStyleSheet("padding: 0; font-size: 18px;")
        zoom_out.clicked.connect(self.zoom_out)
        tb_layout.addWidget(zoom_out)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(180)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        tb_layout.addWidget(self.zoom_slider)

        zoom_in = QPushButton("+")
        zoom_in.setFixedSize(36, 36)
        zoom_in.setStyleSheet("padding: 0; font-size: 18px;")
        zoom_in.clicked.connect(self.zoom_in)
        tb_layout.addWidget(zoom_in)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(55)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(self.zoom_label)

        tb_layout.addSpacing(15)

        fit_btn = QPushButton(tr("viewer.fit"))
        fit_btn.setToolTip(tr("viewer.fit_tip"))
        fit_btn.clicked.connect(self.fit_to_view)
        tb_layout.addWidget(fit_btn)

        actual_btn = QPushButton("1:1")
        actual_btn.setToolTip(tr("viewer.actual_tip"))
        actual_btn.clicked.connect(lambda: self.zoom_slider.setValue(100))
        tb_layout.addWidget(actual_btn)

        zoom_50 = QPushButton("50%")
        zoom_50.clicked.connect(lambda: self.zoom_slider.setValue(50))
        tb_layout.addWidget(zoom_50)

        zoom_200 = QPushButton("200%")
        zoom_200.clicked.connect(lambda: self.zoom_slider.setValue(200))
        tb_layout.addWidget(zoom_200)

        tb_layout.addStretch()

        self.fullscreen_btn = QPushButton(tr("viewer.fullscreen"))
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        tb_layout.addWidget(self.fullscreen_btn)

        tb_layout.addSpacing(15)

        svg_btn = QPushButton("💾 SVG")
        svg_btn.clicked.connect(self.export_svg)
        tb_layout.addWidget(svg_btn)

        png_btn = QPushButton("🖼 PNG")
        png_btn.clicked.connect(lambda: self.export_png())
        tb_layout.addWidget(png_btn)

        png_2x_btn = QPushButton("🖼 PNG @2x")
        png_2x_btn.setToolTip(tr("viewer.png2x_tip"))
        png_2x_btn.clicked.connect(lambda: self.export_png(scale=2))
        tb_layout.addWidget(png_2x_btn)

        layout.addWidget(toolbar)

        self.web_view = WebView()
        self.web_view.message_received.connect(self.on_web_message)
        layout.addWidget(self.web_view)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def load_shell(self):
        html = build_mermaid_viewer_shell(self.dark_mode, bundled_assets(), WebView.BRIDGE_HEAD)
        name = "viewer-dark.html" if self.dark_mode else "viewer-light.html"
        self.web_view.load_file(write_shell(name, html))

    @staticmethod
    def default_mermaid_code():
        return "flowchart TD\n    A[Start] --> B[End]"

    def set_mermaid_blocks(self, blocks, index=0, fallback_code=""):
        if blocks:
            self.mermaid_blocks = blocks
            self.current_index = max(0, min(index, len(blocks) - 1))
            self.mermaid_code = self.mermaid_blocks[self.current_index]
        else:
            self.mermaid_blocks = []
            self.current_index = 0
            self.mermaid_code = fallback_code.strip() or self.default_mermaid_code()
        self.update_navigation_state()
        self.render_mermaid()

    def update_navigation_state(self):
        total = len(self.mermaid_blocks) if self.mermaid_blocks else 1
        current = self.current_index + 1 if self.mermaid_blocks else 1
        self.page_label.setText(f"{current}/{total}")
        self.prev_btn.setEnabled(bool(self.mermaid_blocks) and self.current_index > 0)
        self.next_btn.setEnabled(bool(self.mermaid_blocks) and self.current_index < len(self.mermaid_blocks) - 1)

    def _show_index(self, index):
        self.current_index = index
        self.mermaid_code = self.mermaid_blocks[self.current_index]
        self.update_navigation_state()
        self.render_mermaid()

    def prev_diagram(self):
        if self.mermaid_blocks and self.current_index > 0:
            self._show_index(self.current_index - 1)

    def next_diagram(self):
        if self.mermaid_blocks and self.current_index < len(self.mermaid_blocks) - 1:
            self._show_index(self.current_index + 1)

    def render_mermaid(self):
        self.web_view.run_js(mermaid_show_script(self.mermaid_code))
        self.web_view.run_js(f"setZoom({self.zoom_level})")

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self.setStyleSheet(DARK_STYLE if dark_mode else LIGHT_STYLE)
        self.load_shell()
        self.render_mermaid()

    def on_zoom_changed(self, value):
        self.zoom_level = value
        self.zoom_label.setText(f"{value}%")
        self.web_view.run_js(f"setZoom({value})")

    def zoom_in(self):
        self.zoom_slider.setValue(min(self.zoom_level + 25, 500))

    def zoom_out(self):
        self.zoom_slider.setValue(max(self.zoom_level - 25, 10))

    def fit_to_view(self):
        self.web_view.run_js("fitToView()", lambda v: self.zoom_slider.setValue(int(v)) if v else None)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_btn.setText(tr("viewer.fullscreen"))
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText(tr("viewer.windowed"))
        self.is_fullscreen = not self.is_fullscreen

    def export_svg(self):
        path, _ = QFileDialog.getSaveFileName(self, tr("viewer.save_svg"), "diagram.svg", "SVG (*.svg)")
        if path:
            self.pending_save_path = path
            self.web_view.run_js("exportSVG()")

    def export_png(self, scale=1):
        suffix = "@2x" if scale == 2 else ""
        path, _ = QFileDialog.getSaveFileName(self, tr("viewer.save_png"), f"diagram{suffix}.png", "PNG (*.png)")
        if path:
            self.pending_save_path = path
            self.web_view.run_js(f"exportPNG({scale})")

    def on_web_message(self, name, data):
        if name == "svg":
            self.save_svg_data(data)
        elif name == "png":
            self.save_png_data(data)

    def save_svg_data(self, data):
        if self.pending_save_path and data:
            try:
                file_io.write_text(self.pending_save_path, data)
                self.status_bar.showMessage(tr("common.saved_to", path=self.pending_save_path), 3000)
            except OSError as e:
                QMessageBox.critical(self, tr("common.error"), str(e))
        self.pending_save_path = None

    def save_png_data(self, data):
        if self.pending_save_path and data:
            try:
                if data.startswith("data:image/png;base64,"):
                    data = data[22:]
                file_io.write_bytes(self.pending_save_path, base64.b64decode(data))
                self.status_bar.showMessage(tr("common.saved_to", path=self.pending_save_path), 3000)
            except (OSError, ValueError) as e:
                QMessageBox.critical(self, tr("common.error"), str(e))
        self.pending_save_path = None

    def update_mermaid(self, code):
        self.set_mermaid_blocks([code.strip()] if code else [], 0, fallback_code=code)

    def update_mermaid_blocks(self, blocks, index=0):
        self.set_mermaid_blocks(blocks, index=index)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        elif event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key.Key_0:
            self.zoom_slider.setValue(100)
        else:
            super().keyPressEvent(event)


# ============== 사이드 패널 ==============

def panel_title(text):
    title = QLabel(text)
    title.setFont(QFont("", 13, QFont.Weight.Bold))
    return title


class OutlinePanel(QWidget):
    """문서 개요 (TOC) 패널"""
    heading_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(panel_title(tr("panel.outline")))

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

    def update_outline(self, text):
        self.tree.clear()
        stack = [(None, -1)]  # (item, level)
        in_fence = False

        for i, line in enumerate(text.split('\n')):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            match = None if in_fence else re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                item = QTreeWidgetItem([match.group(2)])
                item.setData(0, Qt.ItemDataRole.UserRole, i)

                while stack and stack[-1][1] >= level:
                    stack.pop()

                if stack and stack[-1][0]:
                    stack[-1][0].addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

                stack.append((item, level))

        self.tree.expandAll()

    def on_item_clicked(self, item, column):
        line_num = item.data(0, Qt.ItemDataRole.UserRole)
        if line_num is not None:
            self.heading_clicked.emit(line_num)


class ExamplePanel(QWidget):
    template_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(panel_title(tr("panel.examples")))

        self.list = QListWidget()
        for template_id, name, _body in example_templates(current_language()):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, template_id)
            self.list.addItem(item)
        self.list.itemDoubleClicked.connect(self.insert)
        layout.addWidget(self.list)

        btn = QPushButton(tr("panel.insert"))
        btn.clicked.connect(self.insert)
        layout.addWidget(btn)

    def insert(self):
        item = self.list.currentItem()
        if item:
            template_id = item.data(Qt.ItemDataRole.UserRole)
            # 날짜가 들어가는 템플릿을 위해 삽입 시점에 생성
            templates = {tid: body for tid, _name, body in example_templates(current_language())}
            self.template_selected.emit(templates.get(template_id, ""))


class MermaidPanel(QWidget):
    template_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.examples = {example_id: code for example_id, _name, code in mermaid_examples(current_language())}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(panel_title(tr("panel.mermaid")))

        info = QLabel(tr("panel.mermaid_count", count=len(self.examples)))
        info.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info)

        self.list = QListWidget()
        for example_id, name, _code in mermaid_examples(current_language()):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, example_id)
            self.list.addItem(item)
        self.list.itemDoubleClicked.connect(self.insert)
        self.list.currentItemChanged.connect(self.show_preview)
        layout.addWidget(self.list)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(100)
        self.preview.setFont(QFont("Menlo", 9))
        layout.addWidget(self.preview)

        btn = QPushButton(tr("panel.insert"))
        btn.clicked.connect(self.insert)
        layout.addWidget(btn)

    def show_preview(self, current, prev):
        if current:
            code = self.examples.get(current.data(Qt.ItemDataRole.UserRole), "")
            # 처음 몇 줄만 표시
            self.preview.setPlainText('\n'.join(code.split('\n')[:8]) + '\n...')

    def insert(self):
        item = self.list.currentItem()
        if item:
            self.template_selected.emit(self.examples.get(item.data(Qt.ItemDataRole.UserRole), ""))


class FileExplorerPanel(QWidget):
    file_clicked = pyqtSignal(str)
    folder_opened = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tool_layout = QHBoxLayout()
        tool_layout.setContentsMargins(5, 5, 5, 0)

        self.path_label = QLabel(tr("explorer.title"))
        self.path_label.setStyleSheet("font-weight: bold; color: #666;")
        tool_layout.addWidget(self.path_label)

        tool_layout.addStretch()

        # 버튼 스타일 (투명 배경, 아이콘만 표시)
        btn_style = """
            QPushButton { background-color: transparent; border: none; padding: 4px; }
            QPushButton:hover { background-color: rgba(0, 0, 0, 0.1); border-radius: 4px; }
        """

        for icon, tip, slot in [(QStyle.StandardPixmap.SP_DirOpenIcon, tr("explorer.open_folder"), self.open_directory),
                                (QStyle.StandardPixmap.SP_BrowserReload, tr("explorer.refresh"), self.refresh)]:
            btn = QPushButton()
            btn.setIcon(self.style().standardIcon(icon))
            btn.setFixedSize(30, 30)
            btn.setToolTip(tip)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(slot)
            tool_layout.addWidget(btn)

        layout.addLayout(tool_layout)

        self.hint_label = QLabel(tr("explorer.choose_folder"))
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(self.hint_label)

        self.model = QFileSystemModel()
        self.model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files)
        self.model.setNameFilters(["*.md", "*.markdown", "*.txt", "*.py", "*.js", "*.html", "*.css",
                                   "*.json", "*.xml", "*.yaml", "*.yml"])
        self.model.setNameFilterDisables(False)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        for column in (1, 2, 3):  # Size, Type, Date
            self.tree.setColumnHidden(column, True)
        self.tree.setHeaderHidden(True)
        self.tree.doubleClicked.connect(self.on_double_click)
        self.tree.hide()
        layout.addWidget(self.tree)

        self.root_path = ""

    def open_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, tr("explorer.open_folder"), self.root_path or QDir.homePath())
        if dir_path:
            self.set_root_path(dir_path)
            self.folder_opened.emit(dir_path)

    def set_root_path(self, path):
        if not path or not QFileInfo(path).isDir():
            return
        self.root_path = path
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))
        self.path_label.setText(os.path.basename(path) or path)
        self.hint_label.hide()
        self.tree.show()

    def refresh(self):
        if self.root_path:
            self.set_root_path(self.root_path)

    def on_double_click(self, index):
        file_path = self.model.filePath(index)
        if not self.model.isDir(index):
            self.file_clicked.emit(file_path)


class CheatSheetPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(panel_title(tr("panel.guide")))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cl = QVBoxLayout(content)

        text = tr("guide.sample.text")
        items = [
            (tr("guide.heading"), "# H1  ## H2  ### H3"),
            (tr("guide.bold"), f"**{text}**"),
            (tr("guide.italic"), f"*{text}*"),
            (tr("guide.strike"), f"~~{text}~~"),
            (tr("guide.inline_code"), f"`{tr('guide.sample.code')}`"),
            (tr("guide.code_block"), f"```{tr('guide.sample.lang')}\\n{tr('guide.sample.code')}\\n```"),
            (tr("guide.link"), f"[{text}](URL)"),
            (tr("guide.image"), f"![{tr('guide.sample.alt')}](URL)"),
            (tr("guide.list"), f"- {tr('guide.sample.item')}  {tr('guide.sample.or')}  1. {tr('guide.sample.item')}"),
            (tr("guide.checklist"), f"- [ ] {tr('guide.sample.todo')}  - [x] {tr('guide.sample.done')}"),
            (tr("guide.quote"), f"> {tr('guide.sample.quote')}"),
            (tr("guide.table"), "| A | B |\\n|---|---|\\n| 1 | 2 |"),
            (tr("guide.hr"), "---"),
            ("Mermaid", "```mermaid\\nflowchart TD\\n```"),
            ("Math", "$E = mc^2$"),
        ]

        for title, sample in items:
            group = QGroupBox(title)
            gl = QVBoxLayout(group)
            lbl = QLabel(sample)
            lbl.setFont(QFont("Menlo", 10))
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setWordWrap(True)
            gl.addWidget(lbl)
            cl.addWidget(group)

        scroll.setWidget(content)
        layout.addWidget(scroll)


# ============== 메인 에디터 ==============

class MarkdownEditor(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        self.dark_mode = False
        self.focus_mode = False
        self.custom_css_path = ""
        self.recent_files = []
        self.language_setting = "system"
        self.explorer_root = ""
        self.mermaid_viewer = None
        self.snippets = default_snippets(current_language())
        self.word_goal = 0
        self.auto_save_timer = QTimer()
        self._preview_size = 500
        self._normal_style = ""
        self._disk_state = None
        self._suspend_file_check = False
        self._external_prompt_active = False
        self._focus_prev = {}
        self._preview_shell_key = None
        self.file_check_timer = QTimer()
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(350)
        self.preview_timer.timeout.connect(self.update_preview)

        self.load_settings(config if config is not None else load_config())
        self.load_snippets()
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_auto_save()
        self.setup_file_check()
        self.apply_theme()
        self.update_title()
        self.restore_explorer()

        # 초기화 과정에서 발생했을 수 있는 변경 상태 리셋
        self.is_modified = False
        self.update_title()

    def load_settings(self, cfg):
        self.dark_mode = cfg.get('dark_mode', False)
        self.recent_files = cfg.get('recent_files', [])
        self.word_goal = cfg.get('word_goal', 0)
        self.custom_css_path = cfg.get('custom_css_path', "")
        self.language_setting = cfg.get('language', "system")
        self.explorer_root = cfg.get('explorer_root', "")

    def save_settings(self):
        self.recent_files = self.recent_files[:10]
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'dark_mode': self.dark_mode,
                    'recent_files': self.recent_files,
                    'word_goal': self.word_goal,
                    'custom_css_path': self.custom_css_path,
                    'language': self.language_setting,
                    'explorer_root': self.explorer_root,
                }, f)
        except OSError:
            pass

    def load_snippets(self):
        try:
            if os.path.exists(SNIPPETS_FILE):
                with open(SNIPPETS_FILE, 'r', encoding='utf-8') as f:
                    self.snippets.update(json.load(f))
        except (OSError, ValueError):
            pass

    def save_snippets(self):
        try:
            with open(SNIPPETS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.snippets, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def setup_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1100, 720)
        self.resize(1300, 850)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 사이드 패널
        self.side_panel = QTabWidget()
        self.side_panel.setMaximumWidth(320)
        self.side_panel.setMinimumWidth(250)

        self.file_panel = FileExplorerPanel()
        self.file_panel.file_clicked.connect(self.open_file)
        self.file_panel.folder_opened.connect(self.on_explorer_folder_opened)
        self.add_side_tab(self.file_panel, tr("tab.explorer"))

        self.outline_panel = OutlinePanel()
        self.outline_panel.heading_clicked.connect(self.goto_line)
        self.add_side_tab(self.outline_panel, tr("tab.outline"))

        self.example_panel = ExamplePanel()
        self.example_panel.template_selected.connect(self.insert_template)
        self.add_side_tab(self.example_panel, tr("tab.examples"))

        self.mermaid_panel = MermaidPanel()
        self.mermaid_panel.template_selected.connect(self.insert_at_cursor)
        self.add_side_tab(self.mermaid_panel, tr("tab.mermaid"))

        self.cheatsheet = CheatSheetPanel()
        self.add_side_tab(self.cheatsheet, tr("tab.guide"))

        main_layout.addWidget(self.side_panel)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 에디터
        editor_w = QWidget()
        el = QVBoxLayout(editor_w)
        el.setContentsMargins(5, 5, 5, 5)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(tr("editor.placeholder"))
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_cursor_pos)
        self.editor.verticalScrollBar().valueChanged.connect(self.sync_scroll)

        # 탭 키 처리 (스니펫)
        self.editor.installEventFilter(self)

        self.highlighter = MarkdownHighlighter(self.editor.document(), self.dark_mode)

        self.completer = QCompleter(autocomplete_items(current_language()))
        self.completer.setWidget(self.editor)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)

        el.addWidget(self.editor)

        # 워드 목표 프로그레스
        self.goal_progress = QProgressBar()
        self.goal_progress.setMaximumHeight(8)
        self.goal_progress.setTextVisible(False)
        self.goal_progress.hide()
        el.addWidget(self.goal_progress)

        self.editor_container = editor_w
        self.splitter.addWidget(editor_w)

        # 미리보기
        preview_w = QWidget()
        pl = QVBoxLayout(preview_w)
        pl.setContentsMargins(5, 5, 5, 5)

        self.preview = WebView()
        self.preview.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.preview.message_received.connect(self.on_preview_message)
        pl.addWidget(self.preview)

        self.preview_container = preview_w
        self.splitter.addWidget(preview_w)
        self.splitter.setSizes([550, 550])

        main_layout.addWidget(self.splitter)

        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.word_label = QLabel(tr("status.words", count=0))
        self.status_bar.addPermanentWidget(self.word_label)

        self.char_label = QLabel(tr("status.chars", count=0))
        self.status_bar.addPermanentWidget(self.char_label)

        self.read_time_label = QLabel(tr("status.read_time", count=1))
        self.status_bar.addPermanentWidget(self.read_time_label)

        self.pos_label = QLabel(tr("status.position", line=1, col=1))
        self.status_bar.addPermanentWidget(self.pos_label)

    def add_side_tab(self, widget, label):
        """Icon-only tab (labels like '📂 Files' get cut off in CJK); the name moves to the tooltip."""
        icon, _, name = label.partition(" ")
        index = self.side_panel.addTab(widget, icon)
        self.side_panel.setTabToolTip(index, name or label)

    def eventFilter(self, obj, event):
        """탭 키로 스니펫 확장"""
        if obj == self.editor and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                cursor = self.editor.textCursor()
                cursor.select(QTextCursor.SelectionType.WordUnderCursor)
                word = cursor.selectedText()

                if word in self.snippets:
                    # $1 등의 플레이스홀더 처리
                    snippet = self.snippets[word].replace('$1', '').replace('$2', '')
                    cursor.insertText(snippet)
                    return True
        return super().eventFilter(obj, event)

    def _add_action(self, menu, text, slot, shortcut=None, role=None):
        act = QAction(text, self)
        if shortcut is not None:
            act.setShortcut(shortcut)
        if role is not None:
            act.setMenuRole(role)
        act.triggered.connect(slot)
        menu.addAction(act)
        return act

    def setup_menu(self):
        menubar = self.menuBar()
        no_role = QAction.MenuRole.NoRole

        # ===== 파일 =====
        file_menu = menubar.addMenu(tr("menu.file"))
        self._add_action(file_menu, tr("file.new"), self.new_file, QKeySequence.StandardKey.New)
        self._add_action(file_menu, tr("file.open"), lambda: self.open_file(), QKeySequence.StandardKey.Open)
        self._add_action(file_menu, tr("file.reload"), lambda: self.reload_file(), QKeySequence("F5"))

        self.recent_menu = file_menu.addMenu(tr("file.recent"))
        self.update_recent_menu()

        file_menu.addSeparator()
        self._add_action(file_menu, tr("file.save"), self.save_file, QKeySequence.StandardKey.Save)
        self._add_action(file_menu, tr("file.save_as"), self.save_file_as, QKeySequence("Ctrl+Shift+S"))
        file_menu.addSeparator()

        export_menu = file_menu.addMenu(tr("file.export"))
        self._add_action(export_menu, tr("file.export_html"), self.export_html)
        self._add_action(export_menu, tr("file.export_pdf"), self.print_preview, QKeySequence.StandardKey.Print)

        file_menu.addSeparator()
        self._add_action(file_menu, tr("file.backup"), self.create_backup)
        file_menu.addSeparator()
        self._add_action(file_menu, tr("file.quit"), self.close, QKeySequence.StandardKey.Quit,
                         role=QAction.MenuRole.QuitRole)

        # ===== 편집 =====
        edit_menu = menubar.addMenu(tr("menu.edit"))
        self._add_action(edit_menu, tr("edit.undo"), self.editor.undo, QKeySequence.StandardKey.Undo)
        self._add_action(edit_menu, tr("edit.redo"), self.editor.redo, QKeySequence.StandardKey.Redo)
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("edit.cut"), self.editor.cut, QKeySequence.StandardKey.Cut)
        self._add_action(edit_menu, tr("edit.copy"), self.handle_copy, QKeySequence.StandardKey.Copy)
        self._add_action(edit_menu, tr("edit.paste"), self.handle_paste, QKeySequence.StandardKey.Paste)
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("edit.find"), self.show_find_dialog, QKeySequence.StandardKey.Find)
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("edit.snippets"), self.manage_snippets, role=no_role)

        # ===== 삽입 =====
        insert_menu = menubar.addMenu(tr("menu.insert"))
        self._add_action(insert_menu, tr("insert.table"), self.insert_table)
        self._add_action(insert_menu, tr("insert.link"), self.insert_link)
        self._add_action(insert_menu, tr("insert.image"), self.insert_image)
        self._add_action(insert_menu, tr("insert.emoji"), self.insert_emoji)
        insert_menu.addSeparator()
        self._add_action(insert_menu, tr("insert.toc"), lambda: self.insert_text("[TOC]\n\n"))
        self._add_action(insert_menu, tr("insert.date"),
                         lambda: self.insert_text(datetime.now().strftime("%Y-%m-%d")))
        self._add_action(insert_menu, tr("insert.time"),
                         lambda: self.insert_text(datetime.now().strftime("%H:%M")))
        insert_menu.addSeparator()

        examples = mermaid_examples(current_language())
        mermaid_menu = insert_menu.addMenu(tr("insert.mermaid"))
        for _example_id, name, code in examples:
            self._add_action(mermaid_menu, name, lambda _, c=code: self.insert_at_cursor(c))

        # ===== Mermaid =====
        mermaid_main = menubar.addMenu(tr("menu.mermaid"))
        self._add_action(mermaid_main, tr("mermaid.open_viewer"), self.open_mermaid_viewer)
        mermaid_main.addSeparator()
        for example_id, name, code in examples:
            if example_id in FEATURED_MERMAID_IDS:
                self._add_action(mermaid_main, tr("mermaid.insert_named", name=name),
                                 lambda _, c=code: self.insert_at_cursor(c))

        # ===== 보기 =====
        view_menu = menubar.addMenu(tr("menu.view"))

        self.preview_act = self._add_action(view_menu, tr("view.preview"), self.toggle_preview)
        self.preview_act.setCheckable(True)
        self.preview_act.setChecked(True)

        self.sidebar_act = self._add_action(view_menu, tr("view.sidebar"), self.toggle_sidebar)
        self.sidebar_act.setCheckable(True)
        self.sidebar_act.setChecked(True)

        view_menu.addSeparator()
        self.focus_act = self._add_action(view_menu, tr("view.focus"), self.toggle_focus_mode, QKeySequence("F11"))
        self.focus_act.setCheckable(True)

        view_menu.addSeparator()
        self.dark_act = self._add_action(view_menu, tr("view.dark"), self.toggle_dark_mode)
        self.dark_act.setCheckable(True)
        self.dark_act.setChecked(self.dark_mode)

        view_menu.addSeparator()
        self._add_action(view_menu, tr("view.custom_css"), self.set_custom_css, role=no_role)
        self._add_action(view_menu, tr("view.clear_css"), self.clear_custom_css, role=no_role)
        self._add_action(view_menu, tr("view.stats"), self.show_stats)

        view_menu.addSeparator()
        language_menu = view_menu.addMenu(tr("view.language"))
        language_group = QActionGroup(self)
        language_group.setExclusive(True)
        for code, label in [("system", tr("view.language_system"))] + [
                (code, LANGUAGE_NAMES[code]) for code in SUPPORTED_LANGUAGES]:
            act = self._add_action(language_menu, label, lambda _, c=code: self.change_language(c), role=no_role)
            act.setCheckable(True)
            act.setChecked(code == self.language_setting)
            language_group.addAction(act)

        # ===== 도구 =====
        tools_menu = menubar.addMenu(tr("menu.tools"))
        self._add_action(tools_menu, tr("tools.word_goal"), self.set_word_goal, role=no_role)
        tools_menu.addSeparator()
        self._add_action(tools_menu, tr("tools.format_tables"), self.format_tables)
        self._add_action(tools_menu, tr("tools.sort_lines"), self.sort_selected_lines)
        self._add_action(tools_menu, tr("tools.remove_empty"), self.remove_empty_lines)

        # ===== 도움말 =====
        help_menu = menubar.addMenu(tr("menu.help"))
        self._add_action(help_menu, tr("help.about"), self.show_about, role=QAction.MenuRole.AboutRole)
        self._add_action(help_menu, tr("help.shortcuts"), self.show_shortcuts, role=no_role)

    def setup_toolbar(self):
        toolbar = QToolBar(tr("toolbar.name"))
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        buttons = [
            ("H1", lambda: self.insert_at_line_start("# "), "tip.h1"),
            ("H2", lambda: self.insert_at_line_start("## "), "tip.h2"),
            ("H3", lambda: self.insert_at_line_start("### "), "tip.h3"),
            ("|", None, None),
            ("B", lambda: self.wrap_selection("**"), "tip.bold"),
            ("I", lambda: self.wrap_selection("*"), "tip.italic"),
            ("S", lambda: self.wrap_selection("~~"), "tip.strike"),
            ("C", lambda: self.wrap_selection("`"), "tip.code"),
            ("|", None, None),
            ("•", lambda: self.insert_at_line_start("- "), "tip.bullet"),
            ("1.", lambda: self.insert_at_line_start("1. "), "tip.numbered"),
            ("☐", lambda: self.insert_at_line_start("- [ ] "), "tip.check"),
            ("☑", lambda: self.insert_at_line_start("- [x] "), "tip.done"),
            ("|", None, None),
            ("🔗", self.insert_link, "tip.link"),
            ("🖼", self.insert_image, "tip.image"),
            ("📊", self.insert_table, "tip.table"),
            ("😀", self.insert_emoji, "tip.emoji"),
            ("|", None, None),
            ("📈", self.open_mermaid_viewer, "tip.mermaid"),
            ("🎯", self.toggle_focus_mode, "tip.focus"),
            ("🔄", lambda: self.reload_file(), "tip.reload"),
        ]

        for text, action, tooltip_key in buttons:
            if text == "|":
                toolbar.addSeparator()
                continue
            btn = toolbar.addAction(text)
            btn.setToolTip(tr(tooltip_key))
            btn.triggered.connect(action)

    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+1", lambda: self.insert_at_line_start("# ")),
            ("Ctrl+2", lambda: self.insert_at_line_start("## ")),
            ("Ctrl+3", lambda: self.insert_at_line_start("### ")),
            ("Ctrl+4", lambda: self.insert_at_line_start("#### ")),
            ("Ctrl+B", lambda: self.wrap_selection("**")),
            ("Ctrl+I", lambda: self.wrap_selection("*")),
            ("Ctrl+K", self.insert_link),
            ("Ctrl+M", self.open_mermaid_viewer),
            ("Ctrl+D", lambda: self.insert_text(datetime.now().strftime("%Y-%m-%d"))),
            ("Ctrl+Shift+C", lambda: self.insert_text("```\n\n```")),
            ("Escape", self.exit_focus_mode),
        ]
        for key, cb in shortcuts:
            s = QShortcut(QKeySequence(key), self)
            s.activated.connect(cb)

    def setup_auto_save(self):
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)

    def setup_file_check(self):
        self.file_check_timer.timeout.connect(self.check_external_file_change)
        self.file_check_timer.start(2000)

    def restore_explorer(self):
        if self.explorer_root:
            self.file_panel.set_root_path(self.explorer_root)

    def on_explorer_folder_opened(self, path):
        self.explorer_root = path
        self.save_settings()

    def apply_theme(self):
        style = DARK_STYLE if self.dark_mode else LIGHT_STYLE
        apply_native_appearance(self.dark_mode)
        self._normal_style = style
        if not self.focus_mode:
            self.setStyleSheet(style)
        self.highlighter.dark_mode = self.dark_mode
        self.highlighter.setup_formats()
        self.highlighter.rehighlight()
        self.update_preview()

    def on_text_changed(self):
        self.is_modified = True
        self.update_title()
        self.update_stats()
        self.outline_panel.update_outline(self.editor.toPlainText())
        self.preview_timer.start()

    def update_title(self):
        title = APP_NAME
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.setWindowTitle(title)
        self.setWindowFilePath(self.current_file or "")
        self.setWindowModified(self.is_modified)

    def update_stats(self):
        stats = DocumentStats.calculate(self.editor.toPlainText())

        self.word_label.setText(tr("status.words", count=stats['words']))
        self.char_label.setText(tr("status.chars", count=stats['chars']))
        self.read_time_label.setText(tr("status.read_time", count=stats['read_time']))

        # 워드 목표
        if self.word_goal > 0:
            self.goal_progress.show()
            progress = min(100, int(stats['words'] / self.word_goal * 100))
            self.goal_progress.setValue(progress)
            self.goal_progress.setToolTip(tr("status.goal", words=stats['words'], goal=self.word_goal, percent=progress))
        else:
            self.goal_progress.hide()

    def sync_scroll(self, value):
        if not self.preview.isVisible():
            return
        max_val = self.editor.verticalScrollBar().maximum()
        if max_val > 0:
            self.preview.run_js(f"setScroll({value / max_val})")

    def update_cursor_pos(self):
        cursor = self.editor.textCursor()
        self.pos_label.setText(tr("status.position", line=cursor.blockNumber() + 1, col=cursor.columnNumber() + 1))

    def handle_copy(self):
        if self.preview.has_web_focus():
            self.preview.copy()
            return
        self.editor.copy()

    def handle_paste(self):
        if self.focus_mode:
            self.status_bar.showMessage(tr("msg.paste_blocked"), 2000)
            return
        self.editor.setFocus()
        self.editor.paste()

    def on_preview_message(self, name, data):
        if name == "copy":
            QApplication.clipboard().setText(data)

    def _read_custom_css(self):
        if self.custom_css_path:
            try:
                return file_io.read_text(self.custom_css_path)
            except (OSError, UnicodeDecodeError):
                pass
        return ""

    def _document_base_url(self):
        if not self.current_file:
            return ""
        return QUrl.fromLocalFile(os.path.dirname(os.path.abspath(self.current_file)) + os.sep).toString()

    def ensure_preview_shell(self):
        """(Re)load the static preview page when theme, CSS or language changes."""
        custom_css = self._read_custom_css()
        key = (self.dark_mode, custom_css, current_language())
        if key == self._preview_shell_key:
            return
        self._preview_shell_key = key
        html = build_preview_shell(self.dark_mode, bundled_assets(), copy_labels(),
                                   bridge_head=WebView.BRIDGE_HEAD, custom_css=custom_css)
        self.preview.load_file(write_shell("preview.html", html))

    def update_preview(self):
        self.ensure_preview_shell()
        content = markdown_to_html(self.editor.toPlainText())
        if self.current_file:
            denied = []

            def read_image(path):
                try:
                    return file_io.read_bytes(path)
                except FileAccessError as e:
                    if e.permission_denied:
                        denied.append(path)
                    raise

            content = inline_local_images(content, os.path.dirname(os.path.abspath(self.current_file)),
                                          reader=read_image)
            if denied:
                self.status_bar.showMessage(tr("msg.images_need_folder"), 8000)
        self.preview.run_js(preview_render_script(content, self._document_base_url()))

    def update_recent_menu(self):
        self.recent_menu.clear()
        for f in self.recent_files[:10]:
            act = QAction(os.path.basename(f), self)
            act.setToolTip(f)
            act.triggered.connect(lambda _, p=f: self.open_file(p))
            self.recent_menu.addAction(act)

        if self.recent_files:
            self.recent_menu.addSeparator()
            clear = QAction(tr("file.recent_clear"), self)
            clear.triggered.connect(self.clear_recent_files)
            self.recent_menu.addAction(clear)

    def clear_recent_files(self):
        self.recent_files = []
        self.update_recent_menu()
        self.save_settings()

    def add_to_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.update_recent_menu()
        self.save_settings()

    def goto_line(self, line_num):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.MoveAnchor, line_num)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setFocus()

    # ===== 파일 작업 =====
    def new_file(self):
        if self.check_save():
            self.editor.clear()
            self.current_file = None
            self.is_modified = False
            self._disk_state = None
            self.update_title()

    def open_file(self, path=None, ask_to_save=True):
        if ask_to_save and not self.check_save():
            return

        if not path:
            path, _ = QFileDialog.getOpenFileName(self, tr("dialog.open"), "", tr("filter.open"))
            if not path:
                return

        # 샌드박스에서는 Qt 파일 엔진이 보안 범위 접근 권한(북마크)을 관리하므로 file_io(QFile)로만 접근
        if not file_io.exists(path):
            QMessageBox.warning(self, tr("common.error"), tr("msg.file_missing", path=path))
            return

        self._suspend_file_check = True
        try:
            self.editor.setPlainText(file_io.read_text(path))
            self.current_file = path
            self.is_modified = False
            self._disk_state = self._get_disk_state(path)
            self.update_title()
            self.add_to_recent(path)
            self.update_preview()
        except FileAccessError as e:
            if e.permission_denied:
                QMessageBox.warning(self, tr("common.error"), tr("msg.file_access"))
            else:
                QMessageBox.critical(self, tr("common.error"), str(e))
        except (OSError, UnicodeDecodeError) as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
        finally:
            self._suspend_file_check = False

    def save_file(self):
        if self.current_file:
            return self._save(self.current_file)
        return self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, tr("dialog.save"), "", tr("filter.save"))
        if path:
            return self._save(path)
        return False

    def _save(self, path):
        self._suspend_file_check = True
        try:
            file_io.write_text(path, self.editor.toPlainText())
            self.current_file = path
            self.is_modified = False
            self._disk_state = self._get_disk_state(path)
            self.update_title()
            self.add_to_recent(path)
            self.status_bar.showMessage(tr("msg.saved", path=path), 3000)
            return True
        except OSError as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
            return False
        finally:
            self._suspend_file_check = False

    def auto_save(self):
        if self.current_file and self.is_modified:
            self._save(self.current_file)

    def check_save(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self, APP_NAME, tr("msg.save_changes"),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                return self.save_file()
            if reply == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def _get_disk_state(self, path):
        return file_io.file_state(path)

    def check_external_file_change(self):
        if self._suspend_file_check or self._external_prompt_active:
            return
        if not self.current_file or not file_io.exists(self.current_file):
            return
        disk_state = self._get_disk_state(self.current_file)
        if disk_state is None:
            return
        if self._disk_state is None:
            self._disk_state = disk_state
            return
        if disk_state == self._disk_state:
            return

        self._external_prompt_active = True
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle(tr("msg.external_title"))
            msg.setText(tr("msg.external_text"))
            msg.setInformativeText(tr("msg.external_modified") if self.is_modified else tr("msg.external_reload_q"))
            reload_btn = msg.addButton(tr("msg.reload"), QMessageBox.ButtonRole.AcceptRole)
            msg.addButton(tr("msg.keep"), QMessageBox.ButtonRole.RejectRole)
            msg.setDefaultButton(reload_btn)
            msg.exec()

            if msg.clickedButton() == reload_btn:
                self.reload_file(force=True)
            else:
                self._disk_state = disk_state
                self.status_bar.showMessage(tr("msg.external_ignored"), 3000)
        finally:
            self._external_prompt_active = False

    def reload_file(self, force=False):
        if not self.current_file:
            self.status_bar.showMessage(tr("msg.no_file"), 2000)
            return
        if not force and self.is_modified:
            reply = QMessageBox.question(
                self, tr("msg.reload_title"), tr("msg.reload_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._suspend_file_check = True
        try:
            self.editor.setPlainText(file_io.read_text(self.current_file))
            self.is_modified = False
            self._disk_state = self._get_disk_state(self.current_file)
            self.update_title()
            self.status_bar.showMessage(tr("msg.reloaded"), 2000)
        except (OSError, UnicodeDecodeError) as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
        finally:
            self._suspend_file_check = False

    def create_backup(self):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = os.path.basename(self.current_file) if self.current_file else "untitled"
            backup_path = os.path.join(BACKUP_DIR, f"{name}_{timestamp}.md")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
        except OSError as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
            return
        self.status_bar.showMessage(tr("msg.backup_created", path=backup_path), 3000)

    def export_html(self):
        default_name = os.path.splitext(os.path.basename(self.current_file))[0] + ".html" if self.current_file else ""
        path, _ = QFileDialog.getSaveFileName(self, tr("msg.export_html"), default_name, "HTML (*.html)")
        if not path:
            return
        title = os.path.splitext(os.path.basename(path))[0]
        html = build_standalone_html(markdown_to_html(self.editor.toPlainText()), self.dark_mode, copy_labels(),
                                     custom_css=self._read_custom_css(), title=title, lang=current_language())
        try:
            file_io.write_text(path, html)
        except OSError as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
            return
        self.status_bar.showMessage(tr("msg.exported", path=path), 3000)

    def print_preview(self):
        if not self.preview.print_document(self):
            QMessageBox.warning(self, tr("common.notice"), tr("msg.print_unavailable"))

    # ===== 편집 =====
    def insert_text(self, text):
        self.editor.textCursor().insertText(text)
        self.editor.setFocus()

    def insert_at_cursor(self, text):
        self.editor.textCursor().insertText("\n" + text + "\n")
        self.editor.setFocus()

    def insert_at_line_start(self, text):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText(text)
        self.editor.setFocus()

    def wrap_selection(self, wrapper):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        if selected:
            cursor.insertText(f"{wrapper}{selected}{wrapper}")
        else:
            cursor.insertText(f"{wrapper}{wrapper}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=len(wrapper))
            self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def insert_completion(self, text):
        self.editor.textCursor().insertText(text)

    def insert_template(self, content):
        if self.check_save():
            self.editor.setPlainText(content)
            self.current_file = None
            self.is_modified = True
            self.update_title()

    def insert_table(self):
        dlg = TableDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.insert_at_cursor(dlg.get_markdown())

    def insert_link(self):
        cursor = self.editor.textCursor()
        dlg = LinkDialog(self, cursor.selectedText())
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if cursor.hasSelection():
                cursor.insertText(dlg.get_markdown())
            else:
                self.insert_text(dlg.get_markdown())

    def insert_image(self):
        dlg = ImageDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.insert_text(dlg.get_markdown())

    def insert_emoji(self):
        dlg = EmojiDialog(self)
        dlg.emoji_selected.connect(self.insert_text)
        dlg.exec()

    def show_find_dialog(self):
        dlg = FindReplaceDialog(self.editor, self)
        dlg.show()

    def manage_snippets(self):
        dlg = SnippetDialog(self.snippets, self)
        dlg.exec()
        self.save_snippets()

    # ===== 도구 =====
    def set_custom_css(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("msg.css_select"), "", "CSS (*.css)")
        if path:
            self.custom_css_path = path
            self.save_settings()
            self.update_preview()
            self.status_bar.showMessage(tr("msg.css_applied", path=path), 3000)

    def clear_custom_css(self):
        self.custom_css_path = ""
        self.save_settings()
        self.update_preview()
        self.status_bar.showMessage(tr("msg.css_cleared"), 3000)

    def set_word_goal(self):
        goal, ok = QInputDialog.getInt(self, tr("msg.goal_title"), tr("msg.goal_prompt"),
                                       self.word_goal, 0, 100000, 100)
        if ok:
            self.word_goal = goal
            self.update_stats()
            self.save_settings()

    def format_tables(self):
        new_text, count = format_markdown_tables(self.editor.toPlainText())
        if count == 0:
            self.status_bar.showMessage(tr("msg.tables_none"), 2000)
            return
        cursor = self.editor.textCursor()
        position = cursor.position()
        # 되돌리기(Undo)가 가능하도록 전체 선택 후 교체
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(new_text)
        cursor.setPosition(min(position, len(new_text)))
        self.editor.setTextCursor(cursor)
        self.status_bar.showMessage(tr("msg.tables_formatted", count=count), 2000)

    def sort_selected_lines(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            lines = cursor.selectedText().split(' ')  # QTextEdit의 줄바꿈
            lines.sort()
            cursor.insertText('\n'.join(lines))

    def remove_empty_lines(self):
        lines = [line for line in self.editor.toPlainText().split('\n') if line.strip()]
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText('\n'.join(lines))

    def show_stats(self):
        StatsDialog(DocumentStats.calculate(self.editor.toPlainText()), self).exec()

    def change_language(self, code):
        if code == self.language_setting:
            return
        self.language_setting = code
        self.save_settings()
        QMessageBox.information(self, tr("msg.language_title"), tr("msg.language_restart"))

    # ===== Mermaid =====
    def open_mermaid_viewer(self):
        blocks = extract_mermaid_blocks(self.editor.toPlainText())
        if not blocks:
            blocks = [MermaidViewer.default_mermaid_code()]

        if self.mermaid_viewer is None or not self.mermaid_viewer.isVisible():
            self.mermaid_viewer = MermaidViewer(blocks[0], self.dark_mode, self,
                                                mermaid_blocks=blocks, current_index=0)
            self.mermaid_viewer.show()
        else:
            self.mermaid_viewer.update_mermaid_blocks(blocks, index=0)
            self.mermaid_viewer.raise_()
            self.mermaid_viewer.activateWindow()

    # ===== 보기 =====

    def toggle_preview(self):
        sizes = self.splitter.sizes()
        if sizes[1] > 0:
            self._preview_size = sizes[1]
            self.splitter.setSizes([sizes[0] + sizes[1], 0])
        else:
            self.splitter.setSizes([sizes[0] - self._preview_size, self._preview_size])

    def toggle_sidebar(self):
        self.side_panel.setVisible(not self.side_panel.isVisible())

    def toggle_focus_mode(self):
        self.focus_mode = not self.focus_mode
        self.focus_act.setChecked(self.focus_mode)

        if self.focus_mode:
            toolbar = self.findChild(QToolBar)
            self._focus_prev = {
                'side_visible': self.side_panel.isVisible(),
                'editor_visible': self.editor_container.isVisible(),
                'preview_visible': self.preview_container.isVisible(),
                'splitter_sizes': self.splitter.sizes(),
                'menu_visible': self.menuBar().isVisible(),
                'status_visible': self.statusBar().isVisible(),
                'toolbar_visible': toolbar.isVisible(),
            }
            self.side_panel.hide()
            self.editor_container.hide()
            self.preview_container.show()
            self.splitter.setSizes([0, 1])
            self.menuBar().hide()
            self.statusBar().hide()
            toolbar.hide()

            self.setStyleSheet(self._normal_style)
            self.showFullScreen()
        else:
            self.exit_focus_mode()

    def exit_focus_mode(self):
        if not self.focus_mode:
            return
        self.focus_mode = False
        self.focus_act.setChecked(False)
        prev = self._focus_prev or {}
        toolbar = self.findChild(QToolBar)

        for widget, key in [(self.side_panel, 'side_visible'),
                            (self.editor_container, 'editor_visible'),
                            (self.preview_container, 'preview_visible'),
                            (self.menuBar(), 'menu_visible'),
                            (self.statusBar(), 'status_visible'),
                            (toolbar, 'toolbar_visible')]:
            widget.setVisible(prev.get(key, True))
        sizes = prev.get('splitter_sizes')
        if sizes:
            self.splitter.setSizes(sizes)

        self.setStyleSheet(self._normal_style)
        self.showNormal()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.dark_act.setChecked(self.dark_mode)
        self.apply_theme()
        self.save_settings()

        if self.mermaid_viewer and self.mermaid_viewer.isVisible():
            self.mermaid_viewer.set_dark_mode(self.dark_mode)

    # ===== 도움말 =====
    def show_about(self):
        features = [tr("about.f_preview"), tr("about.f_mermaid", count=len(mermaid_examples(current_language()))),
                    tr("about.f_math"), tr("about.f_focus"), tr("about.f_outline"), tr("about.f_snippets"),
                    tr("about.f_dark"), tr("about.f_languages")]
        items = "".join(f"<li>{feature}</li>" for feature in features)
        QMessageBox.about(self, APP_NAME,
                          f"<h2>{APP_NAME} {__version__}</h2>"
                          f"<p>{tr('about.subtitle')}</p><hr>"
                          f"<p><b>{tr('about.features')}:</b></p><ul>{items}</ul>"
                          f"<p style='color:#888;font-size:11px'>{tr('about.licenses')}</p>")

    def show_shortcuts(self):
        rows = [
            ("Ctrl+N", "shortcuts.new"), ("Ctrl+O", "shortcuts.open"), ("Ctrl+S", "shortcuts.save"),
            ("Ctrl+F", "shortcuts.find"), (None, "shortcuts.headings"), ("Ctrl+B", "shortcuts.bold"),
            ("Ctrl+I", "shortcuts.italic"), ("Ctrl+K", "shortcuts.link"), ("Ctrl+M", "shortcuts.mermaid"),
            ("Ctrl+D", "shortcuts.date"), ("F11", "shortcuts.focus"), ("Tab", "shortcuts.snippet"),
            ("Esc", "shortcuts.exit_focus"),
        ]
        headings = "/".join(native_shortcut(f"Ctrl+{n}") for n in range(1, 5))
        table = "".join(
            f"<tr><td><b>{native_shortcut(key) if key else headings}</b></td><td>{tr(label)}</td></tr>"
            for key, label in rows
        )
        QMessageBox.information(self, tr("help.shortcuts"), f"<h3>{tr('shortcuts.title')}</h3><table>{table}</table>")

    def closeEvent(self, event):
        if not self.check_save():
            event.ignore()
            return
        self.save_settings()
        self.save_snippets()
        if self.mermaid_viewer is not None:
            self.mermaid_viewer.close()
        event.accept()


class NebulaApplication(QApplication):
    """Handles macOS 'Open With' / Finder double-click, which arrive as FileOpen events, not argv."""

    def __init__(self, argv):
        super().__init__(argv)
        self.window = None
        self.pending_files = []

    def event(self, event):
        if event.type() == QEvent.Type.FileOpen:
            path = event.file()
            if path:
                if self.window is None:
                    self.pending_files.append(path)
                else:
                    self.window.open_file(path)
            return True
        return super().event(event)


def install_translations(app, language):
    """Localize Qt's built-in strings (standard buttons, input dialogs) to match the UI language."""
    qt_locale = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh_CN"}[language]
    QLocale.setDefault(QLocale(qt_locale))
    translator = QTranslator(app)
    if translator.load(f"qtbase_{qt_locale}", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(translator)
    app._qt_translator = translator


def main():
    # Windows Taskbar Icon Fix
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('nebulanote.editor')

    app = NebulaApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName(APP_NAME)
    if sys.platform != "darwin":
        # macOS는 번들의 .icns 아이콘을 사용
        app.setWindowIcon(QIcon(resource_path("icon.ico")))

    config = load_config()
    language_setting = config.get("language", "system")
    if language_setting in SUPPORTED_LANGUAGES:
        set_language(language_setting)
    else:
        set_language(detect_system_language(QLocale.system().uiLanguages()))
    install_translations(app, current_language())

    window = MarkdownEditor(config)
    app.window = window
    window.show()

    # Close splash screen if it exists (PyInstaller)
    try:
        import pyi_splash
        pyi_splash.close()
    except ImportError:
        pass

    initial_files = list(app.pending_files)
    if len(sys.argv) > 1 and file_io.exists(sys.argv[1]):
        initial_files.append(sys.argv[1])
    app.pending_files = []
    if initial_files:
        # 초기 파일 열기 시 저장 프롬프트 방지
        QTimer.singleShot(100, lambda: window.open_file(initial_files[-1], ask_to_save=False))

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
