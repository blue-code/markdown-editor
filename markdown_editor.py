#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkdownPro - 고급 마크다운 에디터 (Mermaid 지원)
기능: 실시간 미리보기, 자동완성, 예제, 테마, Mermaid 다이어그램 등
"""

import sys
import os
import json
import re
import base64
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QPlainTextEdit, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QDialog, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit, QListWidget, QListWidgetItem,
    QTabWidget, QGridLayout, QFrame, QScrollArea, QMenu,
    QMenuBar, QInputDialog, QCompleter, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QGroupBox, QCheckBox, QTextBrowser,
    QSlider, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QStringListModel, QUrl, QSettings,
    pyqtSignal, QThread, QRegularExpression, QByteArray, QObject, pyqtSlot
)
from PyQt6.QtGui import (
    QFont, QIcon, QAction, QKeySequence, QTextCharFormat,
    QSyntaxHighlighter, QColor, QTextCursor, QPalette,
    QDesktopServices, QShortcut, QTextDocument, QPixmap
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

import markdown
from markdown.extensions import tables, fenced_code, codehilite, toc

CONFIG_FILE = os.path.expanduser("~/.markdownpro_config.json")

LIGHT_STYLE = """
QMainWindow, QWidget { background-color: #ffffff; color: #333333; }
QPlainTextEdit, QTextEdit { background-color: #fafafa; color: #333333; border: 1px solid #e0e0e0; border-radius: 4px; font-family: 'SF Mono', 'Consolas', monospace; font-size: 14px; padding: 10px; selection-background-color: #007AFF; }
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
QListWidget { border: 1px solid #e0e0e0; border-radius: 4px; background-color: white; }
QListWidget::item:selected { background-color: #007AFF; color: white; }
QTabWidget::pane { border: 1px solid #e0e0e0; }
QTabBar::tab { background-color: #f0f0f0; border: 1px solid #e0e0e0; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background-color: white; }
QSlider::groove:horizontal { height: 6px; background: #e0e0e0; border-radius: 3px; }
QSlider::handle:horizontal { background: #007AFF; width: 16px; margin: -5px 0; border-radius: 8px; }
"""

DARK_STYLE = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
QPlainTextEdit, QTextEdit { background-color: #252526; color: #d4d4d4; border: 1px solid #3c3c3c; border-radius: 4px; font-family: 'SF Mono', 'Consolas', monospace; font-size: 14px; padding: 10px; selection-background-color: #264f78; }
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
QListWidget { border: 1px solid #3c3c3c; border-radius: 4px; background-color: #252526; color: #d4d4d4; }
QListWidget::item:selected { background-color: #264f78; color: white; }
QTabWidget::pane { border: 1px solid #3c3c3c; }
QTabBar::tab { background-color: #2d2d2d; border: 1px solid #3c3c3c; color: #d4d4d4; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #1e1e1e; }
QSlider::groove:horizontal { height: 6px; background: #3c3c3c; border-radius: 3px; }
QSlider::handle:horizontal { background: #0e639c; width: 16px; margin: -5px 0; border-radius: 8px; }
"""

MERMAID_EXAMPLES = {
    "플로우차트 (Flowchart)": """```mermaid
flowchart TD
    A[시작] --> B{조건 확인}
    B -->|Yes| C[처리 1]
    B -->|No| D[처리 2]
    C --> E[결과]
    D --> E
    E --> F[종료]
```""",
    "시퀀스 다이어그램": """```mermaid
sequenceDiagram
    participant 사용자
    participant 서버
    participant DB
    
    사용자->>서버: 로그인 요청
    서버->>DB: 사용자 조회
    DB-->>서버: 사용자 정보
    서버-->>사용자: 로그인 성공
```""",
    "클래스 다이어그램": """```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +String color
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```""",
    "상태 다이어그램": """```mermaid
stateDiagram-v2
    [*] --> 대기
    대기 --> 처리중: 시작
    처리중 --> 완료: 성공
    처리중 --> 실패: 오류
    완료 --> [*]
    실패 --> 대기: 재시도
```""",
    "ER 다이어그램": """```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER { string name; string email }
    ORDER { int orderNumber; date created }
```""",
    "간트 차트": """```mermaid
gantt
    title 프로젝트 일정
    dateFormat YYYY-MM-DD
    section 기획
    요구사항 분석 :a1, 2024-01-01, 7d
    설계 :a2, after a1, 5d
    section 개발
    백엔드 개발 :b1, after a2, 14d
    프론트엔드 :b2, after a2, 14d
```""",
    "파이 차트": """```mermaid
pie title 브라우저 점유율
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 10
    "Edge" : 6
```""",
    "마인드맵": """```mermaid
mindmap
  root((프로젝트))
    기획
      요구사항
      일정
    개발
      프론트엔드
      백엔드
    테스트
```""",
    "Git 그래프": """```mermaid
gitGraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Feature A"
    checkout main
    merge develop
    commit id: "Release"
```""",
}

EXAMPLE_TEMPLATES = {
    "기본 문서": "# 제목\n\n이것은 기본 마크다운 문서입니다.\n\n## 부제목\n\n**굵게** 또는 *기울임*으로 강조할 수 있습니다.\n\n- 항목 1\n- 항목 2\n- 항목 3",
    "README 템플릿": "# 프로젝트 이름\n\n프로젝트 설명\n\n## 📦 설치\n\n```bash\nnpm install project-name\n```\n\n## 🚀 사용법\n\n```javascript\nconst project = require('project-name');\n```\n\n## 📄 라이선스\n\nMIT License",
    "회의록": f"# 회의록\n\n**날짜:** {datetime.now().strftime('%Y년 %m월 %d일')}\n**참석자:** 홍길동, 김철수\n\n## 📌 안건\n\n1. 프로젝트 진행 상황\n2. 다음 단계\n\n## 📝 논의 내용\n\n### 진행 상황\n\n- [x] 기획 완료\n- [ ] 개발 진행중\n\n## ✅ 결정 사항\n\n1. 주간 회의 유지",
    "Mermaid 문서": "# 시스템 설계\n\n## 시스템 흐름\n\n```mermaid\nflowchart LR\n    A[클라이언트] --> B[서버]\n    B --> C[(DB)]\n```\n\n## 시퀀스\n\n```mermaid\nsequenceDiagram\n    User->>Server: Request\n    Server-->>User: Response\n```",
}

AUTOCOMPLETE_ITEMS = [
    "# ", "## ", "### ", "**굵게**", "*기울임*", "`코드`",
    "[링크](url)", "![이미지](url)", "- ", "1. ", "- [ ] ",
    "```\n```", "```python\n```", "```mermaid\n```",
    "> ", "---", "| 헤더 |\n|---|\n| 내용 |",
]

EMOJI_LIST = {
    "표정": ["😀", "😃", "😄", "😁", "😅", "😂", "🤣", "😊", "😇", "🙂"],
    "제스처": ["👍", "👎", "👌", "✌️", "🤞", "🤝", "👏", "🙌", "💪", "🙏"],
    "심볼": ["❤️", "⭐", "🌟", "✨", "💫", "🔥", "💯", "✅", "❌", "💡"],
}


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
            'code': '#d7ba7d' if self.dark_mode else '#d84315',
            'link': '#4ec9b0' if self.dark_mode else '#0277bd',
            'mermaid': '#c586c0' if self.dark_mode else '#6a1b9a',
        }
        
        for name, color in colors.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if name == 'header':
                fmt.setFontWeight(QFont.Weight.Bold)
            self.formats[name] = fmt
        
        self.rules = [
            (r'^#{1,6}\s.*$', 'header'),
            (r'\*\*[^*]+\*\*', 'bold'),
            (r'`[^`]+`', 'code'),
            (r'\[([^\]]+)\]\([^)]+\)', 'link'),
            (r'^```mermaid', 'mermaid'),
            (r'^```.*$', 'code'),
        ]
    
    def highlightBlock(self, text):
        for pattern, fmt_name in self.rules:
            regex = QRegularExpression(pattern)
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.formats.get(fmt_name, QTextCharFormat()))


class WebBridge(QObject):
    svg_ready = pyqtSignal(str)
    png_ready = pyqtSignal(str)
    
    @pyqtSlot(str)
    def receiveSvg(self, svg_data):
        self.svg_ready.emit(svg_data)
    
    @pyqtSlot(str)
    def receivePng(self, png_data):
        self.png_ready.emit(png_data)


class MermaidViewer(QMainWindow):
    """Mermaid 다이어그램 전용 뷰어 - 확대/축소, 전체화면, 내보내기 지원"""
    
    def __init__(self, mermaid_code="", dark_mode=False, parent=None):
        super().__init__(parent)
        self.mermaid_code = mermaid_code
        self.dark_mode = dark_mode
        self.zoom_level = 100
        self.is_fullscreen = False
        self.bridge = WebBridge()
        self.bridge.svg_ready.connect(self.save_svg_data)
        self.bridge.png_ready.connect(self.save_png_data)
        self.pending_save_path = None
        self.setup_ui()
        self.render_mermaid()
    
    def setup_ui(self):
        self.setWindowTitle("Mermaid 다이어그램 뷰어")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 툴바
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(10, 5, 10, 5)
        
        # 줌 컨트롤
        zoom_out = QPushButton("−")
        zoom_out.setFixedSize(36, 36)
        zoom_out.clicked.connect(self.zoom_out)
        tb_layout.addWidget(zoom_out)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        tb_layout.addWidget(self.zoom_slider)
        
        zoom_in = QPushButton("+")
        zoom_in.setFixedSize(36, 36)
        zoom_in.clicked.connect(self.zoom_in)
        tb_layout.addWidget(zoom_in)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        tb_layout.addWidget(self.zoom_label)
        
        tb_layout.addSpacing(20)
        
        fit_btn = QPushButton("📐 화면 맞춤")
        fit_btn.clicked.connect(self.fit_to_view)
        tb_layout.addWidget(fit_btn)
        
        actual_btn = QPushButton("1:1 실제 크기")
        actual_btn.clicked.connect(lambda: self.zoom_slider.setValue(100))
        tb_layout.addWidget(actual_btn)
        
        tb_layout.addStretch()
        
        self.fullscreen_btn = QPushButton("⛶ 전체 화면")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        tb_layout.addWidget(self.fullscreen_btn)
        
        tb_layout.addSpacing(20)
        
        svg_btn = QPushButton("💾 SVG 저장")
        svg_btn.clicked.connect(self.export_svg)
        tb_layout.addWidget(svg_btn)
        
        png_btn = QPushButton("🖼 PNG 저장")
        png_btn.clicked.connect(self.export_png)
        tb_layout.addWidget(png_btn)
        
        layout.addWidget(toolbar)
        
        # 웹뷰
        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        layout.addWidget(self.web_view)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def render_mermaid(self):
        bg = "#1e1e1e" if self.dark_mode else "#ffffff"
        theme = "dark" if self.dark_mode else "default"
        
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;overflow:auto;background:{bg}}}
#container{{display:flex;justify-content:center;align-items:center;min-height:100%;padding:20px}}
#diagram{{transform-origin:center;transition:transform 0.2s}}
</style></head><body>
<div id="container"><div id="diagram" class="mermaid">
{self.mermaid_code}
</div></div>
<script>
mermaid.initialize({{startOnLoad:true,theme:'{theme}',securityLevel:'loose',flowchart:{{useMaxWidth:false}},sequence:{{useMaxWidth:false}}}});
var bridge=null;
new QWebChannel(qt.webChannelTransport,function(c){{bridge=c.objects.bridge}});
function setZoom(s){{document.getElementById('diagram').style.transform='scale('+(s/100)+')'}}
function fitToView(){{
  var c=document.getElementById('container'),d=document.getElementById('diagram'),svg=d.querySelector('svg');
  if(svg){{var sw=svg.getBoundingClientRect().width,sh=svg.getBoundingClientRect().height;
  var scale=Math.min((c.clientWidth-40)/sw,(c.clientHeight-40)/sh,1)*100;return Math.round(scale)}}return 100}}
function exportSVG(){{var svg=document.querySelector('#diagram svg');if(svg&&bridge)bridge.receiveSvg(new XMLSerializer().serializeToString(svg))}}
function exportPNG(){{var svg=document.querySelector('#diagram svg');if(svg&&bridge){{
  var data=new XMLSerializer().serializeToString(svg),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),img=new Image();
  var blob=new Blob([data],{{type:'image/svg+xml'}}),url=URL.createObjectURL(blob);
  img.onload=function(){{canvas.width=img.width*2;canvas.height=img.height*2;ctx.scale(2,2);ctx.fillStyle='{bg}';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0);URL.revokeObjectURL(url);bridge.receivePng(canvas.toDataURL('image/png'))}};img.src=url}}}}
</script></body></html>"""
        self.web_view.setHtml(html)
    
    def on_zoom_changed(self, value):
        self.zoom_level = value
        self.zoom_label.setText(f"{value}%")
        self.web_view.page().runJavaScript(f"setZoom({value})")
    
    def zoom_in(self):
        self.zoom_slider.setValue(min(self.zoom_level + 25, 400))
    
    def zoom_out(self):
        self.zoom_slider.setValue(max(self.zoom_level - 25, 25))
    
    def fit_to_view(self):
        self.web_view.page().runJavaScript("fitToView()", lambda v: self.zoom_slider.setValue(int(v)) if v else None)
    
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_btn.setText("⛶ 전체 화면")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("⛶ 창 모드")
        self.is_fullscreen = not self.is_fullscreen
    
    def export_svg(self):
        path, _ = QFileDialog.getSaveFileName(self, "SVG 저장", "diagram.svg", "SVG (*.svg)")
        if path:
            self.pending_save_path = path
            self.web_view.page().runJavaScript("exportSVG()")
    
    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "PNG 저장", "diagram.png", "PNG (*.png)")
        if path:
            self.pending_save_path = path
            self.web_view.page().runJavaScript("exportPNG()")
    
    def save_svg_data(self, data):
        if self.pending_save_path and data:
            try:
                with open(self.pending_save_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                self.status_bar.showMessage(f"저장 완료: {self.pending_save_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "오류", str(e))
        self.pending_save_path = None
    
    def save_png_data(self, data):
        if self.pending_save_path and data:
            try:
                if data.startswith("data:image/png;base64,"):
                    data = data[22:]
                with open(self.pending_save_path, 'wb') as f:
                    f.write(base64.b64decode(data))
                self.status_bar.showMessage(f"저장 완료: {self.pending_save_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "오류", str(e))
        self.pending_save_path = None
    
    def update_mermaid(self, code):
        self.mermaid_code = code
        self.render_mermaid()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)


class TableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("테이블 삽입")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        
        grid = QGridLayout()
        grid.addWidget(QLabel("행:"), 0, 0)
        self.rows = QSpinBox()
        self.rows.setRange(1, 20)
        self.rows.setValue(3)
        grid.addWidget(self.rows, 0, 1)
        
        grid.addWidget(QLabel("열:"), 1, 0)
        self.cols = QSpinBox()
        self.cols.setRange(1, 10)
        self.cols.setValue(3)
        grid.addWidget(self.cols, 1, 1)
        layout.addLayout(grid)
        
        self.header_check = QCheckBox("헤더 포함")
        self.header_check.setChecked(True)
        layout.addWidget(self.header_check)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def get_markdown(self):
        r, c = self.rows.value(), self.cols.value()
        lines = []
        if self.header_check.isChecked():
            lines.append("| " + " | ".join([f"헤더{i+1}" for i in range(c)]) + " |")
            lines.append("| " + " | ".join(["------" for _ in range(c)]) + " |")
            r -= 1
        for _ in range(r):
            lines.append("| " + " | ".join(["내용" for _ in range(c)]) + " |")
        return "\n".join(lines)


class LinkDialog(QDialog):
    def __init__(self, parent=None, selected=""):
        super().__init__(parent)
        self.setWindowTitle("링크 삽입")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("표시 텍스트:"))
        self.text_edit = QLineEdit(selected)
        layout.addWidget(self.text_edit)
        
        layout.addWidget(QLabel("URL:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://")
        layout.addWidget(self.url_edit)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def get_markdown(self):
        return f"[{self.text_edit.text() or '링크'}]({self.url_edit.text() or '#'})"


class ImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이미지 삽입")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("대체 텍스트:"))
        self.alt = QLineEdit()
        layout.addWidget(self.alt)
        
        layout.addWidget(QLabel("경로/URL:"))
        url_layout = QHBoxLayout()
        self.url = QLineEdit()
        url_layout.addWidget(self.url)
        browse = QPushButton("찾기")
        browse.clicked.connect(self.browse)
        url_layout.addWidget(browse)
        layout.addLayout(url_layout)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "이미지 (*.png *.jpg *.gif *.svg)")
        if path:
            self.url.setText(path)
    
    def get_markdown(self):
        return f"![{self.alt.text() or '이미지'}]({self.url.text() or 'image.png'})"


class EmojiDialog(QDialog):
    emoji_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이모지")
        self.setMinimumSize(350, 300)
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        for cat, emojis in EMOJI_LIST.items():
            w = QWidget()
            grid = QGridLayout(w)
            for i, e in enumerate(emojis):
                btn = QPushButton(e)
                btn.setFixedSize(36, 36)
                btn.clicked.connect(lambda _, em=e: self.select(em))
                grid.addWidget(btn, i // 6, i % 6)
            tabs.addTab(w, cat)
        layout.addWidget(tabs)
    
    def select(self, emoji):
        self.emoji_selected.emit(emoji)
        self.accept()


class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("찾기/바꾸기")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("찾기:"))
        self.find_edit = QLineEdit()
        h1.addWidget(self.find_edit)
        layout.addLayout(h1)
        
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("바꾸기:"))
        self.replace_edit = QLineEdit()
        h2.addWidget(self.replace_edit)
        layout.addLayout(h2)
        
        self.case_check = QCheckBox("대소문자 구분")
        layout.addWidget(self.case_check)
        
        btn_layout = QHBoxLayout()
        find_btn = QPushButton("다음 찾기")
        find_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(find_btn)
        
        replace_btn = QPushButton("바꾸기")
        replace_btn.clicked.connect(self.replace_one)
        btn_layout.addWidget(replace_btn)
        
        replace_all = QPushButton("모두 바꾸기")
        replace_all.clicked.connect(self.replace_all)
        btn_layout.addWidget(replace_all)
        layout.addLayout(btn_layout)
    
    def find_next(self):
        text = self.find_edit.text()
        if not text:
            return
        flags = QTextDocument.FindFlag(0)
        if self.case_check.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if not self.editor.find(text, flags):
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(text, flags)
    
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
        if self.case_check.isChecked():
            new_content = content.replace(text, self.replace_edit.text())
        else:
            new_content = re.sub(re.escape(text), self.replace_edit.text(), content, flags=re.IGNORECASE)
        self.editor.setPlainText(new_content)


class ExamplePanel(QWidget):
    template_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("📚 예제 템플릿")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.list = QListWidget()
        for name in EXAMPLE_TEMPLATES.keys():
            self.list.addItem(QListWidgetItem(name))
        self.list.itemDoubleClicked.connect(self.insert)
        layout.addWidget(self.list)
        
        btn = QPushButton("에디터에 삽입")
        btn.clicked.connect(self.insert)
        layout.addWidget(btn)
    
    def insert(self):
        item = self.list.currentItem()
        if item:
            self.template_selected.emit(EXAMPLE_TEMPLATES.get(item.text(), ""))


class MermaidPanel(QWidget):
    template_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("📊 Mermaid 다이어그램")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("다이어그램 유형을 선택하세요")
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        self.list = QListWidget()
        for name in MERMAID_EXAMPLES.keys():
            self.list.addItem(QListWidgetItem(name))
        self.list.itemDoubleClicked.connect(self.insert)
        layout.addWidget(self.list)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(120)
        self.preview.setFont(QFont("Consolas", 10))
        layout.addWidget(self.preview)
        
        self.list.currentItemChanged.connect(self.show_preview)
        
        btn = QPushButton("에디터에 삽입")
        btn.clicked.connect(self.insert)
        layout.addWidget(btn)
    
    def show_preview(self, current, prev):
        if current:
            code = MERMAID_EXAMPLES.get(current.text(), "")
            self.preview.setPlainText(code)
    
    def insert(self):
        item = self.list.currentItem()
        if item:
            self.template_selected.emit(MERMAID_EXAMPLES.get(item.text(), ""))


class CheatSheetPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("📖 마크다운 가이드")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cl = QVBoxLayout(content)
        
        items = [
            ("제목", "# H1 / ## H2 / ### H3"),
            ("굵게", "**텍스트**"),
            ("기울임", "*텍스트*"),
            ("코드", "`코드`"),
            ("코드블록", "```언어\n코드\n```"),
            ("링크", "[텍스트](URL)"),
            ("이미지", "![설명](URL)"),
            ("목록", "- 항목 / 1. 항목"),
            ("체크", "- [ ] 할일 / - [x] 완료"),
            ("인용", "> 인용문"),
            ("표", "| A | B |\\n|---|---|"),
            ("Mermaid", "```mermaid\\nflowchart\\n```"),
        ]
        
        for t, s in items:
            g = QGroupBox(t)
            gl = QVBoxLayout(g)
            lbl = QLabel(s)
            lbl.setFont(QFont("Consolas", 10))
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            gl.addWidget(lbl)
            cl.addWidget(g)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)


class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        self.dark_mode = False
        self.recent_files = []
        self.mermaid_viewer = None
        self.auto_save_timer = QTimer()
        self._preview_size = 500
        
        self.load_settings()
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_auto_save()
        self.apply_theme()
        self.update_title()
        self.update_preview()
    
    def load_settings(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    cfg = json.load(f)
                    self.dark_mode = cfg.get('dark_mode', False)
                    self.recent_files = cfg.get('recent_files', [])
        except:
            pass
    
    def save_settings(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'dark_mode': self.dark_mode, 'recent_files': self.recent_files[:10]}, f)
        except:
            pass
    
    def setup_ui(self):
        self.setWindowTitle("MarkdownPro")
        self.setMinimumSize(1200, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 사이드 패널
        self.side_panel = QTabWidget()
        self.side_panel.setMaximumWidth(320)
        self.side_panel.setMinimumWidth(250)
        
        self.example_panel = ExamplePanel()
        self.example_panel.template_selected.connect(self.insert_template)
        self.side_panel.addTab(self.example_panel, "📚 예제")
        
        self.mermaid_panel = MermaidPanel()
        self.mermaid_panel.template_selected.connect(self.insert_at_cursor)
        self.side_panel.addTab(self.mermaid_panel, "📊 Mermaid")
        
        self.cheatsheet = CheatSheetPanel()
        self.side_panel.addTab(self.cheatsheet, "📖 가이드")
        
        main_layout.addWidget(self.side_panel)
        
        # 스플리터
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 에디터
        editor_w = QWidget()
        el = QVBoxLayout(editor_w)
        el.setContentsMargins(5, 5, 5, 5)
        
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("마크다운을 입력하세요...")
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.editor.textChanged.connect(self.on_text_changed)
        
        self.highlighter = MarkdownHighlighter(self.editor.document(), self.dark_mode)
        
        self.completer = QCompleter(AUTOCOMPLETE_ITEMS)
        self.completer.setWidget(self.editor)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)
        
        el.addWidget(self.editor)
        self.splitter.addWidget(editor_w)
        
        # 미리보기
        preview_w = QWidget()
        pl = QVBoxLayout(preview_w)
        pl.setContentsMargins(5, 5, 5, 5)
        
        self.preview = QWebEngineView()
        pl.addWidget(self.preview)
        
        self.splitter.addWidget(preview_w)
        self.splitter.setSizes([500, 500])
        
        main_layout.addWidget(self.splitter)
        
        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.word_label = QLabel("단어: 0 | 문자: 0")
        self.status_bar.addPermanentWidget(self.word_label)
        
        self.pos_label = QLabel("줄: 1, 열: 1")
        self.status_bar.addPermanentWidget(self.pos_label)
        
        self.editor.cursorPositionChanged.connect(self.update_cursor_pos)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # 파일
        file_menu = menubar.addMenu("파일")
        
        new_act = QAction("새 문서", self)
        new_act.setShortcut(QKeySequence.StandardKey.New)
        new_act.triggered.connect(self.new_file)
        file_menu.addAction(new_act)
        
        open_act = QAction("열기...", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.open_file)
        file_menu.addAction(open_act)
        
        self.recent_menu = file_menu.addMenu("최근 파일")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        save_act = QAction("저장", self)
        save_act.setShortcut(QKeySequence.StandardKey.Save)
        save_act.triggered.connect(self.save_file)
        file_menu.addAction(save_act)
        
        save_as = QAction("다른 이름으로 저장...", self)
        save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as)
        
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu("내보내기")
        export_html = QAction("HTML", self)
        export_html.triggered.connect(self.export_html)
        export_menu.addAction(export_html)
        
        file_menu.addSeparator()
        
        exit_act = QAction("종료", self)
        exit_act.setShortcut(QKeySequence.StandardKey.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        # 편집
        edit_menu = menubar.addMenu("편집")
        
        undo = QAction("실행 취소", self)
        undo.setShortcut(QKeySequence.StandardKey.Undo)
        undo.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo)
        
        redo = QAction("다시 실행", self)
        redo.setShortcut(QKeySequence.StandardKey.Redo)
        redo.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo)
        
        edit_menu.addSeparator()
        
        find_act = QAction("찾기/바꾸기...", self)
        find_act.setShortcut(QKeySequence.StandardKey.Find)
        find_act.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_act)
        
        # 삽입
        insert_menu = menubar.addMenu("삽입")
        
        insert_table = QAction("테이블", self)
        insert_table.triggered.connect(self.insert_table)
        insert_menu.addAction(insert_table)
        
        insert_link = QAction("링크", self)
        insert_link.setShortcut(QKeySequence("Ctrl+K"))
        insert_link.triggered.connect(self.insert_link)
        insert_menu.addAction(insert_link)
        
        insert_image = QAction("이미지", self)
        insert_image.triggered.connect(self.insert_image)
        insert_menu.addAction(insert_image)
        
        insert_emoji = QAction("이모지", self)
        insert_emoji.triggered.connect(self.insert_emoji)
        insert_menu.addAction(insert_emoji)
        
        insert_menu.addSeparator()
        
        # Mermaid 서브메뉴
        mermaid_menu = insert_menu.addMenu("Mermaid 다이어그램")
        for name, code in MERMAID_EXAMPLES.items():
            act = QAction(name, self)
            act.triggered.connect(lambda _, c=code: self.insert_at_cursor(c))
            mermaid_menu.addAction(act)
        
        # Mermaid
        mermaid_main = menubar.addMenu("Mermaid")
        
        open_viewer = QAction("🔍 Mermaid 뷰어 열기", self)
        open_viewer.setShortcut(QKeySequence("Ctrl+M"))
        open_viewer.triggered.connect(self.open_mermaid_viewer)
        mermaid_main.addAction(open_viewer)
        
        mermaid_main.addSeparator()
        
        for name, code in list(MERMAID_EXAMPLES.items())[:5]:
            act = QAction(f"삽입: {name}", self)
            act.triggered.connect(lambda _, c=code: self.insert_at_cursor(c))
            mermaid_main.addAction(act)
        
        # 보기
        view_menu = menubar.addMenu("보기")
        
        self.toggle_preview_act = QAction("미리보기 표시", self)
        self.toggle_preview_act.setCheckable(True)
        self.toggle_preview_act.setChecked(True)
        self.toggle_preview_act.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.toggle_preview_act)
        
        self.toggle_sidebar_act = QAction("사이드바 표시", self)
        self.toggle_sidebar_act.setCheckable(True)
        self.toggle_sidebar_act.setChecked(True)
        self.toggle_sidebar_act.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_act)
        
        view_menu.addSeparator()
        
        self.dark_mode_act = QAction("다크 모드", self)
        self.dark_mode_act.setCheckable(True)
        self.dark_mode_act.setChecked(self.dark_mode)
        self.dark_mode_act.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_act)
        
        # 도움말
        help_menu = menubar.addMenu("도움말")
        
        about = QAction("정보", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)
        
        shortcuts = QAction("단축키", self)
        shortcuts.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts)
    
    def setup_toolbar(self):
        toolbar = QToolBar("서식")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        buttons = [
            ("H1", lambda: self.insert_at_line_start("# ")),
            ("H2", lambda: self.insert_at_line_start("## ")),
            ("H3", lambda: self.insert_at_line_start("### ")),
            ("|", None),
            ("B", lambda: self.wrap_selection("**")),
            ("I", lambda: self.wrap_selection("*")),
            ("C", lambda: self.wrap_selection("`")),
            ("|", None),
            ("•", lambda: self.insert_at_line_start("- ")),
            ("1.", lambda: self.insert_at_line_start("1. ")),
            ("☐", lambda: self.insert_at_line_start("- [ ] ")),
            ("|", None),
            ("🔗", self.insert_link),
            ("🖼", self.insert_image),
            ("📊", self.insert_table),
            ("😀", self.insert_emoji),
            ("|", None),
            ("📈", self.open_mermaid_viewer),
        ]
        
        for text, action in buttons:
            if text == "|":
                toolbar.addSeparator()
            else:
                btn = toolbar.addAction(text)
                if action:
                    btn.triggered.connect(action)
    
    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+1", lambda: self.insert_at_line_start("# ")),
            ("Ctrl+2", lambda: self.insert_at_line_start("## ")),
            ("Ctrl+3", lambda: self.insert_at_line_start("### ")),
            ("Ctrl+B", lambda: self.wrap_selection("**")),
            ("Ctrl+I", lambda: self.wrap_selection("*")),
            ("Ctrl+K", self.insert_link),
            ("Ctrl+M", self.open_mermaid_viewer),
        ]
        for key, cb in shortcuts:
            s = QShortcut(QKeySequence(key), self)
            s.activated.connect(cb)
    
    def setup_auto_save(self):
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)
    
    def apply_theme(self):
        self.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)
        self.highlighter.dark_mode = self.dark_mode
        self.highlighter.setup_formats()
        self.highlighter.rehighlight()
        self.update_preview()
    
    def on_text_changed(self):
        self.is_modified = True
        self.update_title()
        self.update_word_count()
        QTimer.singleShot(300, self.update_preview)
    
    def update_title(self):
        title = "MarkdownPro"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def update_word_count(self):
        text = self.editor.toPlainText()
        self.word_label.setText(f"단어: {len(text.split())} | 문자: {len(text)}")
    
    def update_cursor_pos(self):
        cursor = self.editor.textCursor()
        self.pos_label.setText(f"줄: {cursor.blockNumber()+1}, 열: {cursor.columnNumber()+1}")
    
    def update_preview(self):
        text = self.editor.toPlainText()
        
        # Mermaid 블록 추출 및 변환
        mermaid_pattern = r'```mermaid\n([\s\S]*?)```'
        mermaid_blocks = re.findall(mermaid_pattern, text)
        
        # Mermaid를 플레이스홀더로 대체
        placeholder_text = text
        for i, block in enumerate(mermaid_blocks):
            placeholder_text = placeholder_text.replace(
                f'```mermaid\n{block}```',
                f'<div class="mermaid" id="mermaid-{i}">\n{block}\n</div>'
            )
        
        # 마크다운 변환
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br'])
        html_content = md.convert(placeholder_text)
        
        bg = "#1e1e1e" if self.dark_mode else "#ffffff"
        fg = "#d4d4d4" if self.dark_mode else "#333333"
        code_bg = "#2d2d2d" if self.dark_mode else "#f5f5f5"
        theme = "dark" if self.dark_mode else "default"
        
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; background: {bg}; color: {fg}; }}
h1,h2,h3 {{ margin-top: 24px; margin-bottom: 16px; font-weight: 600; }}
h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
code {{ background: {code_bg}; padding: 0.2em 0.4em; border-radius: 3px; font-family: 'Consolas', monospace; }}
pre {{ background: {code_bg}; padding: 16px; border-radius: 6px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; }}
blockquote {{ border-left: 4px solid #007AFF; margin: 0; padding-left: 16px; color: #666; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: {code_bg}; }}
img {{ max-width: 100%; }}
.mermaid {{ background: transparent; text-align: center; }}
</style></head><body>
{html_content}
<script>mermaid.initialize({{ startOnLoad: true, theme: '{theme}' }});</script>
</body></html>"""
        
        self.preview.setHtml(html)
    
    def update_recent_menu(self):
        self.recent_menu.clear()
        for f in self.recent_files[:10]:
            if os.path.exists(f):
                act = QAction(os.path.basename(f), self)
                act.triggered.connect(lambda _, p=f: self.open_file(p))
                self.recent_menu.addAction(act)
    
    def add_to_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.update_recent_menu()
        self.save_settings()
    
    # 파일 작업
    def new_file(self):
        if self.is_modified:
            reply = QMessageBox.question(self, "저장", "변경사항을 저장하시겠습니까?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.update_title()
    
    def open_file(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "열기", "", "마크다운 (*.md *.markdown *.txt);;모든 파일 (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = path
                self.is_modified = False
                self.update_title()
                self.add_to_recent(path)
            except Exception as e:
                QMessageBox.critical(self, "오류", str(e))
    
    def save_file(self):
        if self.current_file:
            self._save(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "저장", "", "마크다운 (*.md);;텍스트 (*.txt)")
        if path:
            self._save(path)
    
    def _save(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = path
            self.is_modified = False
            self.update_title()
            self.add_to_recent(path)
            self.status_bar.showMessage(f"저장됨: {path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))
    
    def auto_save(self):
        if self.current_file and self.is_modified:
            self._save(self.current_file)
    
    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "HTML 내보내기", "", "HTML (*.html)")
        if path:
            text = self.editor.toPlainText()
            md = markdown.Markdown(extensions=['tables', 'fenced_code'])
            html = f"<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>{md.convert(text)}</body></html>"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.status_bar.showMessage(f"내보냄: {path}", 3000)
    
    # 편집 기능
    def insert_text(self, text):
        self.editor.textCursor().insertText(text)
        self.editor.setFocus()
    
    def insert_at_cursor(self, text):
        cursor = self.editor.textCursor()
        cursor.insertText("\n" + text + "\n")
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
        self.editor.setPlainText(content)
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
    
    # Mermaid 뷰어
    def open_mermaid_viewer(self):
        text = self.editor.toPlainText()
        pattern = r'```mermaid\n([\s\S]*?)```'
        matches = re.findall(pattern, text)
        
        if matches:
            code = matches[0].strip()
        else:
            code = "flowchart TD\n    A[시작] --> B[끝]"
        
        if self.mermaid_viewer is None or not self.mermaid_viewer.isVisible():
            self.mermaid_viewer = MermaidViewer(code, self.dark_mode, self)
            self.mermaid_viewer.show()
        else:
            self.mermaid_viewer.update_mermaid(code)
            self.mermaid_viewer.raise_()
            self.mermaid_viewer.activateWindow()
    
    # 보기
    def toggle_preview(self):
        sizes = self.splitter.sizes()
        if sizes[1] > 0:
            self._preview_size = sizes[1]
            self.splitter.setSizes([sizes[0] + sizes[1], 0])
        else:
            self.splitter.setSizes([sizes[0] - self._preview_size, self._preview_size])
    
    def toggle_sidebar(self):
        self.side_panel.setVisible(not self.side_panel.isVisible())
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.dark_mode_act.setChecked(self.dark_mode)
        self.apply_theme()
        self.save_settings()
        
        if self.mermaid_viewer and self.mermaid_viewer.isVisible():
            self.mermaid_viewer.dark_mode = self.dark_mode
            self.mermaid_viewer.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)
            self.mermaid_viewer.render_mermaid()
    
    # 도움말
    def show_about(self):
        QMessageBox.about(self, "MarkdownPro", 
            "<h2>MarkdownPro</h2><p>v2.0 - Mermaid 지원</p>"
            "<p>기능: 실시간 미리보기, 구문강조, Mermaid 다이어그램, 다크모드</p>")
    
    def show_shortcuts(self):
        QMessageBox.information(self, "단축키",
            "<h3>단축키</h3><table>"
            "<tr><td>Ctrl+N</td><td>새 문서</td></tr>"
            "<tr><td>Ctrl+O</td><td>열기</td></tr>"
            "<tr><td>Ctrl+S</td><td>저장</td></tr>"
            "<tr><td>Ctrl+B</td><td>굵게</td></tr>"
            "<tr><td>Ctrl+I</td><td>기울임</td></tr>"
            "<tr><td>Ctrl+K</td><td>링크</td></tr>"
            "<tr><td>Ctrl+M</td><td>Mermaid 뷰어</td></tr>"
            "<tr><td>Ctrl+1/2/3</td><td>제목</td></tr>"
            "</table>")
    
    def closeEvent(self, event):
        if self.is_modified:
            reply = QMessageBox.question(self, "저장", "변경사항을 저장하시겠습니까?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        self.save_settings()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MarkdownPro")
    window = MarkdownEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
