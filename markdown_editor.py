#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkdownPro - 고급 마크다운 에디터
기능: 실시간 미리보기, 자동완성, 예제, 테마, 내보내기 등
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QPlainTextEdit, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QDialog, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit, QListWidget, QListWidgetItem,
    QTabWidget, QGridLayout, QFrame, QScrollArea, QMenu,
    QMenuBar, QInputDialog, QCompleter, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QGroupBox, QCheckBox, QTextBrowser
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QStringListModel, QUrl, QSettings,
    pyqtSignal, QThread, QRegularExpression
)
from PyQt6.QtGui import (
    QFont, QIcon, QAction, QKeySequence, QTextCharFormat,
    QSyntaxHighlighter, QColor, QTextCursor, QPalette,
    QDesktopServices, QShortcut, QTextDocument
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# 마크다운 변환
import markdown
from markdown.extensions import tables, fenced_code, codehilite, toc

# 설정 파일 경로
CONFIG_FILE = os.path.expanduser("~/.markdownpro_config.json")

# 기본 스타일시트
LIGHT_STYLE = """
QMainWindow, QWidget {
    background-color: #ffffff;
    color: #333333;
}
QPlainTextEdit, QTextEdit {
    background-color: #fafafa;
    color: #333333;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    padding: 10px;
    selection-background-color: #007AFF;
    selection-color: white;
}
QToolBar {
    background-color: #f5f5f5;
    border-bottom: 1px solid #e0e0e0;
    spacing: 5px;
    padding: 5px;
}
QToolBar QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 14px;
}
QToolBar QToolButton:hover {
    background-color: #e0e0e0;
}
QToolBar QToolButton:pressed {
    background-color: #d0d0d0;
}
QMenuBar {
    background-color: #f5f5f5;
    border-bottom: 1px solid #e0e0e0;
}
QMenuBar::item:selected {
    background-color: #e0e0e0;
}
QMenu {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
}
QMenu::item:selected {
    background-color: #007AFF;
    color: white;
}
QStatusBar {
    background-color: #f5f5f5;
    border-top: 1px solid #e0e0e0;
}
QSplitter::handle {
    background-color: #e0e0e0;
}
QPushButton {
    background-color: #007AFF;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0056b3;
}
QPushButton:pressed {
    background-color: #004494;
}
QComboBox, QSpinBox, QLineEdit {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}
QListWidget {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: white;
}
QListWidget::item:selected {
    background-color: #007AFF;
    color: white;
}
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #f0f0f0;
    border: 1px solid #e0e0e0;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: white;
    border-bottom: none;
}
"""

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
QPlainTextEdit, QTextEdit {
    background-color: #252526;
    color: #d4d4d4;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    padding: 10px;
    selection-background-color: #264f78;
    selection-color: white;
}
QToolBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3c3c3c;
    spacing: 5px;
    padding: 5px;
}
QToolBar QToolButton {
    background-color: transparent;
    color: #d4d4d4;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 14px;
}
QToolBar QToolButton:hover {
    background-color: #3c3c3c;
}
QToolBar QToolButton:pressed {
    background-color: #4c4c4c;
}
QMenuBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3c3c3c;
}
QMenuBar::item:selected {
    background-color: #3c3c3c;
}
QMenu {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
}
QMenu::item:selected {
    background-color: #264f78;
    color: white;
}
QStatusBar {
    background-color: #2d2d2d;
    border-top: 1px solid #3c3c3c;
}
QSplitter::handle {
    background-color: #3c3c3c;
}
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:pressed {
    background-color: #0d5a8c;
}
QComboBox, QSpinBox, QLineEdit {
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px;
    background-color: #3c3c3c;
    color: #d4d4d4;
}
QListWidget {
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    background-color: #252526;
    color: #d4d4d4;
}
QListWidget::item:selected {
    background-color: #264f78;
    color: white;
}
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    color: #d4d4d4;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e1e1e;
    border-bottom: none;
}
"""

# 마크다운 예제 템플릿
EXAMPLE_TEMPLATES = {
    "기본 문서": """# 제목

이것은 기본 마크다운 문서입니다.

## 부제목

일반 텍스트를 작성합니다. **굵게** 또는 *기울임꼴*로 강조할 수 있습니다.

### 목록

- 첫 번째 항목
- 두 번째 항목
- 세 번째 항목

### 링크와 이미지

[링크 텍스트](https://example.com)

![이미지 설명](image.png)
""",

    "README 템플릿": """# 프로젝트 이름

프로젝트에 대한 간단한 설명을 작성합니다.

## 📦 설치

```bash
npm install project-name
```

## 🚀 사용법

```javascript
const project = require('project-name');
project.init();
```

## ✨ 기능

- 기능 1: 설명
- 기능 2: 설명
- 기능 3: 설명

## 📋 요구사항

- Node.js 16+
- npm 8+

## 🤝 기여

1. Fork
2. Feature Branch (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Pull Request

## 📄 라이선스

MIT License
""",

    "블로그 포스트": """---
title: 블로그 제목
date: {date}
author: 작성자
tags: [태그1, 태그2]
---

# 블로그 제목

![대표 이미지](cover.jpg)

## 소개

여기에 소개 문단을 작성합니다. 독자의 관심을 끌 수 있는 내용으로 시작하세요.

## 본문

### 첫 번째 섹션

내용을 작성합니다.

> 인용문을 사용하여 중요한 내용을 강조할 수 있습니다.

### 두 번째 섹션

코드 예시:

```python
def hello():
    print("Hello, World!")
```

## 결론

마무리 문단을 작성합니다.

---

*읽어주셔서 감사합니다!*
""".format(date=datetime.now().strftime("%Y-%m-%d")),

    "회의록": """# 회의록

**날짜:** {date}  
**참석자:** 홍길동, 김철수, 이영희  
**장소:** 회의실 A

---

## 📌 안건

1. 프로젝트 진행 상황 공유
2. 다음 단계 계획
3. 이슈 논의

## 📝 논의 내용

### 1. 프로젝트 진행 상황

- 현재 진행률: 70%
- 완료된 작업:
  - [x] 기획
  - [x] 디자인
  - [ ] 개발
  - [ ] 테스트

### 2. 다음 단계

| 담당자 | 작업 | 기한 |
|--------|------|------|
| 홍길동 | 백엔드 개발 | 12/15 |
| 김철수 | 프론트엔드 | 12/20 |
| 이영희 | QA 테스트 | 12/25 |

### 3. 이슈

- ⚠️ 일정 지연 가능성
- 💡 추가 리소스 필요

## ✅ 결정 사항

1. 주간 회의 유지
2. 일정 조정 검토

## 📅 다음 회의

**날짜:** 다음 주 같은 시간
""".format(date=datetime.now().strftime("%Y년 %m월 %d일")),

    "기술 문서": """# API 문서

## 개요

이 API는 사용자 관리 기능을 제공합니다.

## 인증

모든 요청에 API 키가 필요합니다:

```
Authorization: Bearer YOUR_API_KEY
```

## 엔드포인트

### 사용자 조회

```http
GET /api/users/{id}
```

**파라미터:**

| 이름 | 타입 | 설명 |
|------|------|------|
| id | string | 사용자 ID |

**응답:**

```json
{
  "id": "123",
  "name": "홍길동",
  "email": "hong@example.com"
}
```

### 사용자 생성

```http
POST /api/users
```

**요청 본문:**

```json
{
  "name": "홍길동",
  "email": "hong@example.com",
  "password": "secure123"
}
```

## 에러 코드

| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 404 | 리소스 없음 |
| 500 | 서버 오류 |
""",

    "체크리스트": """# 체크리스트

## 오늘 할 일

- [ ] 이메일 확인
- [ ] 회의 참석
- [ ] 보고서 작성
- [ ] 코드 리뷰

## 이번 주 목표

- [ ] 프로젝트 A 완료
  - [ ] 기능 1 구현
  - [ ] 기능 2 구현
  - [ ] 테스트 작성
- [ ] 프로젝트 B 시작
  - [ ] 요구사항 분석
  - [ ] 설계 문서 작성

## 완료된 항목

- [x] 환경 설정
- [x] 기초 학습
- [x] 팀 미팅

---

> 💡 **팁:** 작업을 작은 단위로 나누면 진행 상황을 파악하기 쉽습니다.
""",

    "수학 노트": """# 수학 노트

## 기본 공식

### 이차방정식

$$ax^2 + bx + c = 0$$

근의 공식:

$$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$

### 삼각함수

| 함수 | 공식 |
|------|------|
| sin | 대변/빗변 |
| cos | 인접변/빗변 |
| tan | 대변/인접변 |

### 미적분

**미분:**
$$\\frac{d}{dx}(x^n) = nx^{n-1}$$

**적분:**
$$\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$$

## 예제

1. $f(x) = x^2 + 3x + 2$를 미분하시오.

   풀이: $f'(x) = 2x + 3$

2. $\\int (2x + 1) dx$를 구하시오.

   풀이: $x^2 + x + C$
"""
}

# 자동완성 키워드
AUTOCOMPLETE_ITEMS = [
    # 헤더
    "# ", "## ", "### ", "#### ", "##### ", "###### ",
    # 강조
    "**굵게**", "*기울임*", "~~취소선~~", "`인라인 코드`",
    # 링크/이미지
    "[링크텍스트](url)", "![이미지설명](url)",
    # 목록
    "- ", "1. ", "- [ ] ", "- [x] ",
    # 코드블록
    "```\n코드\n```", "```python\n\n```", "```javascript\n\n```",
    "```bash\n\n```", "```json\n\n```",
    # 인용
    "> ", ">> ",
    # 수평선
    "---", "***",
    # 테이블
    "| 헤더1 | 헤더2 |\n|-------|-------|\n| 내용1 | 내용2 |",
    # 특수
    "<!-- 주석 -->", "[^각주]", "~~취소선~~",
]

# 이모지 목록
EMOJI_LIST = {
    "표정": ["😀", "😃", "😄", "😁", "😅", "😂", "🤣", "😊", "😇", "🙂", "😉", "😌", "😍", "🥰", "😘"],
    "제스처": ["👍", "👎", "👌", "✌️", "🤞", "🤝", "👏", "🙌", "👐", "🤲", "💪", "🙏"],
    "심볼": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "⭐", "🌟", "✨", "💫", "🔥", "💯"],
    "화살표": ["➡️", "⬅️", "⬆️", "⬇️", "↗️", "↘️", "↙️", "↖️", "↕️", "↔️"],
    "체크": ["✅", "❌", "⭕", "❗", "❓", "💡", "📌", "🔔", "📢", "🎯"],
    "기타": ["📁", "📂", "📄", "📝", "✏️", "📊", "📈", "📉", "🗓️", "⏰", "🔗", "🔒", "🔓"],
}


class MarkdownHighlighter(QSyntaxHighlighter):
    """마크다운 구문 강조"""
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setup_formats()
    
    def setup_formats(self):
        """포맷 설정"""
        self.formats = {}
        
        # 색상 정의 (다크/라이트 모드)
        if self.dark_mode:
            colors = {
                'header': '#569cd6',
                'bold': '#ce9178',
                'italic': '#b5cea8',
                'code': '#d7ba7d',
                'link': '#4ec9b0',
                'list': '#c586c0',
                'quote': '#6a9955',
                'hr': '#808080',
            }
        else:
            colors = {
                'header': '#0066cc',
                'bold': '#9c27b0',
                'italic': '#2e7d32',
                'code': '#d84315',
                'link': '#0277bd',
                'list': '#6a1b9a',
                'quote': '#558b2f',
                'hr': '#9e9e9e',
            }
        
        # 헤더 (# ~ ######)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(colors['header']))
        header_format.setFontWeight(QFont.Weight.Bold)
        self.formats['header'] = (r'^#{1,6}\s.*$', header_format)
        
        # 굵게 (**text** 또는 __text__)
        bold_format = QTextCharFormat()
        bold_format.setForeground(QColor(colors['bold']))
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.formats['bold'] = (r'\*\*[^*]+\*\*|__[^_]+__', bold_format)
        
        # 기울임 (*text* 또는 _text_)
        italic_format = QTextCharFormat()
        italic_format.setForeground(QColor(colors['italic']))
        italic_format.setFontItalic(True)
        self.formats['italic'] = (r'(?<!\*)\*(?!\*)[^*]+\*(?!\*)|(?<!_)_(?!_)[^_]+_(?!_)', italic_format)
        
        # 인라인 코드 (`code`)
        code_format = QTextCharFormat()
        code_format.setForeground(QColor(colors['code']))
        code_format.setFontFamily('Consolas')
        self.formats['code'] = (r'`[^`]+`', code_format)
        
        # 링크 ([text](url))
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(colors['link']))
        link_format.setFontUnderline(True)
        self.formats['link'] = (r'\[([^\]]+)\]\([^)]+\)', link_format)
        
        # 목록 (-, *, 1.)
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(colors['list']))
        self.formats['list'] = (r'^\s*[-*+]\s|^\s*\d+\.\s', list_format)
        
        # 인용 (>)
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor(colors['quote']))
        quote_format.setFontItalic(True)
        self.formats['quote'] = (r'^>+.*$', quote_format)
        
        # 수평선 (---, ***)
        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor(colors['hr']))
        self.formats['hr'] = (r'^(-{3,}|\*{3,}|_{3,})$', hr_format)
        
        # 코드 블록 시작/끝
        codeblock_format = QTextCharFormat()
        codeblock_format.setForeground(QColor(colors['code']))
        self.formats['codeblock'] = (r'^```.*$', codeblock_format)
    
    def highlightBlock(self, text):
        """블록 하이라이팅"""
        for name, (pattern, fmt) in self.formats.items():
            regex = QRegularExpression(pattern)
            match_iterator = regex.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class TableDialog(QDialog):
    """테이블 삽입 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("테이블 삽입")
        self.setMinimumWidth(300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 행/열 설정
        grid = QGridLayout()
        
        grid.addWidget(QLabel("행 수:"), 0, 0)
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 20)
        self.rows_spin.setValue(3)
        grid.addWidget(self.rows_spin, 0, 1)
        
        grid.addWidget(QLabel("열 수:"), 1, 0)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 10)
        self.cols_spin.setValue(3)
        grid.addWidget(self.cols_spin, 1, 1)
        
        layout.addLayout(grid)
        
        # 헤더 포함 여부
        self.header_check = QCheckBox("헤더 행 포함")
        self.header_check.setChecked(True)
        layout.addWidget(self.header_check)
        
        # 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_table_markdown(self):
        """마크다운 테이블 생성"""
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        has_header = self.header_check.isChecked()
        
        lines = []
        
        if has_header:
            header = "| " + " | ".join([f"헤더{i+1}" for i in range(cols)]) + " |"
            separator = "| " + " | ".join(["------" for _ in range(cols)]) + " |"
            lines.append(header)
            lines.append(separator)
            rows -= 1
        
        for r in range(rows):
            row = "| " + " | ".join([f"내용" for _ in range(cols)]) + " |"
            lines.append(row)
        
        return "\n".join(lines)


class LinkDialog(QDialog):
    """링크 삽입 다이얼로그"""
    
    def __init__(self, parent=None, selected_text=""):
        super().__init__(parent)
        self.setWindowTitle("링크 삽입")
        self.setMinimumWidth(400)
        self.selected_text = selected_text
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 텍스트
        layout.addWidget(QLabel("표시 텍스트:"))
        self.text_edit = QLineEdit()
        self.text_edit.setText(self.selected_text)
        self.text_edit.setPlaceholderText("링크에 표시될 텍스트")
        layout.addWidget(self.text_edit)
        
        # URL
        layout.addWidget(QLabel("URL:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com")
        layout.addWidget(self.url_edit)
        
        # 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_markdown(self):
        text = self.text_edit.text() or "링크"
        url = self.url_edit.text() or "#"
        return f"[{text}]({url})"


class ImageDialog(QDialog):
    """이미지 삽입 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이미지 삽입")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 대체 텍스트
        layout.addWidget(QLabel("대체 텍스트:"))
        self.alt_edit = QLineEdit()
        self.alt_edit.setPlaceholderText("이미지 설명")
        layout.addWidget(self.alt_edit)
        
        # URL/경로
        url_layout = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("이미지 URL 또는 파일 경로")
        url_layout.addWidget(self.url_edit)
        
        browse_btn = QPushButton("찾아보기")
        browse_btn.clicked.connect(self.browse_file)
        url_layout.addWidget(browse_btn)
        
        layout.addWidget(QLabel("이미지 경로/URL:"))
        layout.addLayout(url_layout)
        
        # 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.gif *.svg *.webp)"
        )
        if file_path:
            self.url_edit.setText(file_path)
    
    def get_markdown(self):
        alt = self.alt_edit.text() or "이미지"
        url = self.url_edit.text() or "image.png"
        return f"![{alt}]({url})"


class EmojiDialog(QDialog):
    """이모지 선택 다이얼로그"""
    
    emoji_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이모지 삽입")
        self.setMinimumSize(400, 350)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 탭 위젯
        tabs = QTabWidget()
        
        for category, emojis in EMOJI_LIST.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            container = QWidget()
            grid = QGridLayout(container)
            grid.setSpacing(5)
            
            cols = 8
            for i, emoji in enumerate(emojis):
                btn = QPushButton(emoji)
                btn.setFixedSize(40, 40)
                btn.setFont(QFont("", 18))
                btn.setStyleSheet("QPushButton { border: 1px solid #ddd; border-radius: 4px; }")
                btn.clicked.connect(lambda checked, e=emoji: self.select_emoji(e))
                grid.addWidget(btn, i // cols, i % cols)
            
            scroll.setWidget(container)
            tabs.addTab(scroll, category)
        
        layout.addWidget(tabs)
    
    def select_emoji(self, emoji):
        self.emoji_selected.emit(emoji)
        self.accept()


class FindReplaceDialog(QDialog):
    """찾기/바꾸기 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("찾기 및 바꾸기")
        self.setMinimumWidth(400)
        self.editor = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 찾기
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("찾기:"))
        self.find_edit = QLineEdit()
        find_layout.addWidget(self.find_edit)
        layout.addLayout(find_layout)
        
        # 바꾸기
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("바꾸기:"))
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)
        
        # 옵션
        options_layout = QHBoxLayout()
        self.case_check = QCheckBox("대소문자 구분")
        self.whole_word_check = QCheckBox("전체 단어만")
        options_layout.addWidget(self.case_check)
        options_layout.addWidget(self.whole_word_check)
        layout.addLayout(options_layout)
        
        # 버튼
        btn_layout = QHBoxLayout()
        
        find_btn = QPushButton("다음 찾기")
        find_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(find_btn)
        
        replace_btn = QPushButton("바꾸기")
        replace_btn.clicked.connect(self.replace_one)
        btn_layout.addWidget(replace_btn)
        
        replace_all_btn = QPushButton("모두 바꾸기")
        replace_all_btn.clicked.connect(self.replace_all)
        btn_layout.addWidget(replace_all_btn)
        
        layout.addLayout(btn_layout)
    
    def find_next(self):
        if not self.editor:
            return
        
        text = self.find_edit.text()
        if not text:
            return
        
        editor_widget = self.editor.editor
        flags = QTextDocument.FindFlag(0)
        
        if self.case_check.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_check.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        
        found = editor_widget.find(text, flags)
        if not found:
            # 처음부터 다시 검색
            cursor = editor_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor_widget.setTextCursor(cursor)
            editor_widget.find(text, flags)
    
    def replace_one(self):
        if not self.editor:
            return
        
        editor_widget = self.editor.editor
        cursor = editor_widget.textCursor()
        
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
        
        self.find_next()
    
    def replace_all(self):
        if not self.editor:
            return
        
        text = self.find_edit.text()
        if not text:
            return
        
        editor_widget = self.editor.editor
        content = editor_widget.toPlainText()
        
        if self.case_check.isChecked():
            new_content = content.replace(text, self.replace_edit.text())
        else:
            new_content = re.sub(
                re.escape(text), 
                self.replace_edit.text(), 
                content, 
                flags=re.IGNORECASE
            )
        
        editor_widget.setPlainText(new_content)


class ExamplePanel(QWidget):
    """예제 패널"""
    
    template_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 제목
        title = QLabel("📚 마크다운 예제")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("템플릿을 선택하면 에디터에 삽입됩니다.")
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        # 템플릿 목록
        self.template_list = QListWidget()
        for name in EXAMPLE_TEMPLATES.keys():
            item = QListWidgetItem(name)
            self.template_list.addItem(item)
        
        self.template_list.itemDoubleClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)
        
        # 미리보기
        preview_label = QLabel("미리보기:")
        preview_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(preview_label)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(150)
        layout.addWidget(self.preview)
        
        self.template_list.currentItemChanged.connect(self.show_preview)
        
        # 삽입 버튼
        insert_btn = QPushButton("에디터에 삽입")
        insert_btn.clicked.connect(self.insert_template)
        layout.addWidget(insert_btn)
    
    def show_preview(self, current, previous):
        if current:
            name = current.text()
            content = EXAMPLE_TEMPLATES.get(name, "")
            self.preview.setPlainText(content[:500] + "..." if len(content) > 500 else content)
    
    def on_template_selected(self, item):
        self.insert_template()
    
    def insert_template(self):
        current = self.template_list.currentItem()
        if current:
            name = current.text()
            content = EXAMPLE_TEMPLATES.get(name, "")
            self.template_selected.emit(content)


class CheatSheetPanel(QWidget):
    """마크다운 치트시트 패널"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("📖 마크다운 문법 가이드")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        cheat_sheet = [
            ("제목", "# H1\n## H2\n### H3"),
            ("굵게", "**굵은 텍스트**"),
            ("기울임", "*기울임 텍스트*"),
            ("취소선", "~~취소선~~"),
            ("인라인 코드", "`코드`"),
            ("코드 블록", "```python\ncode\n```"),
            ("링크", "[텍스트](URL)"),
            ("이미지", "![대체텍스트](URL)"),
            ("순서 없는 목록", "- 항목\n- 항목"),
            ("순서 있는 목록", "1. 항목\n2. 항목"),
            ("체크리스트", "- [ ] 할 일\n- [x] 완료"),
            ("인용", "> 인용문"),
            ("수평선", "---"),
            ("테이블", "| A | B |\n|---|---|\n| 1 | 2 |"),
        ]
        
        for title_text, syntax in cheat_sheet:
            group = QGroupBox(title_text)
            group_layout = QVBoxLayout(group)
            
            code = QLabel(syntax)
            code.setFont(QFont("Consolas", 11))
            code.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
            code.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            group_layout.addWidget(code)
            
            content_layout.addWidget(group)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)


class MarkdownEditor(QMainWindow):
    """메인 에디터 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        self.current_file = None
        self.is_modified = False
        self.dark_mode = False
        self.recent_files = []
        self.auto_save_timer = QTimer()
        
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
        """설정 로드"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.dark_mode = config.get('dark_mode', False)
                    self.recent_files = config.get('recent_files', [])
        except Exception:
            pass
    
    def save_settings(self):
        """설정 저장"""
        try:
            config = {
                'dark_mode': self.dark_mode,
                'recent_files': self.recent_files[:10]
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass
    
    def setup_ui(self):
        """UI 설정"""
        self.setWindowTitle("MarkdownPro")
        self.setMinimumSize(1200, 800)
        
        # 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 사이드 패널 (예제/치트시트)
        self.side_panel = QTabWidget()
        self.side_panel.setMaximumWidth(350)
        self.side_panel.setMinimumWidth(250)
        
        # 예제 패널
        self.example_panel = ExamplePanel()
        self.example_panel.template_selected.connect(self.insert_template)
        self.side_panel.addTab(self.example_panel, "📚 예제")
        
        # 치트시트 패널
        self.cheatsheet_panel = CheatSheetPanel()
        self.side_panel.addTab(self.cheatsheet_panel, "📖 가이드")
        
        main_layout.addWidget(self.side_panel)
        
        # 메인 스플리터 (에디터 | 미리보기)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 에디터
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(5, 5, 5, 5)
        
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("마크다운을 입력하세요...")
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.editor.textChanged.connect(self.on_text_changed)
        
        # 구문 강조
        self.highlighter = MarkdownHighlighter(self.editor.document(), self.dark_mode)
        
        # 자동완성
        self.completer = QCompleter(AUTOCOMPLETE_ITEMS)
        self.completer.setWidget(self.editor)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)
        
        editor_layout.addWidget(self.editor)
        self.splitter.addWidget(editor_container)
        
        # 미리보기
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(5, 5, 5, 5)
        
        self.preview = QWebEngineView()
        preview_layout.addWidget(self.preview)
        
        self.splitter.addWidget(preview_container)
        self.splitter.setSizes([500, 500])
        
        main_layout.addWidget(self.splitter)
        
        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.word_count_label = QLabel("단어: 0 | 문자: 0")
        self.status_bar.addPermanentWidget(self.word_count_label)
        
        self.position_label = QLabel("줄: 1, 열: 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        self.editor.cursorPositionChanged.connect(self.update_cursor_position)
    
    def setup_menu(self):
        """메뉴 설정"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        new_action = QAction("새 문서", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("열기...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # 최근 파일 서브메뉴
        self.recent_menu = file_menu.addMenu("최근 파일")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        save_action = QAction("저장", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("다른 이름으로 저장...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 내보내기
        export_menu = file_menu.addMenu("내보내기")
        
        export_html = QAction("HTML로 내보내기", self)
        export_html.triggered.connect(self.export_html)
        export_menu.addAction(export_html)
        
        export_pdf = QAction("PDF로 내보내기", self)
        export_pdf.triggered.connect(self.export_pdf)
        export_menu.addAction(export_pdf)
        
        file_menu.addSeparator()
        
        exit_action = QAction("종료", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 편집 메뉴
        edit_menu = menubar.addMenu("편집")
        
        undo_action = QAction("실행 취소", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("다시 실행", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("잘라내기", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("복사", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("붙여넣기", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("찾기/바꾸기...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # 삽입 메뉴
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
        
        insert_codeblock = QAction("코드 블록", self)
        insert_codeblock.triggered.connect(lambda: self.insert_text("```\n\n```"))
        insert_menu.addAction(insert_codeblock)
        
        insert_quote = QAction("인용문", self)
        insert_quote.triggered.connect(lambda: self.insert_text("> "))
        insert_menu.addAction(insert_quote)
        
        insert_hr = QAction("수평선", self)
        insert_hr.triggered.connect(lambda: self.insert_text("\n---\n"))
        insert_menu.addAction(insert_hr)
        
        # 보기 메뉴
        view_menu = menubar.addMenu("보기")
        
        self.toggle_preview_action = QAction("미리보기 표시/숨기기", self)
        self.toggle_preview_action.setCheckable(True)
        self.toggle_preview_action.setChecked(True)
        self.toggle_preview_action.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.toggle_preview_action)
        
        self.toggle_sidebar_action = QAction("사이드바 표시/숨기기", self)
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.setChecked(True)
        self.toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)
        
        view_menu.addSeparator()
        
        self.dark_mode_action = QAction("다크 모드", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말")
        
        about_action = QAction("MarkdownPro 정보", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("단축키 보기", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
    
    def setup_toolbar(self):
        """툴바 설정"""
        toolbar = QToolBar("서식")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        # 서식 버튼들
        buttons = [
            ("H1", "# ", "제목 1 (Ctrl+1)"),
            ("H2", "## ", "제목 2 (Ctrl+2)"),
            ("H3", "### ", "제목 3 (Ctrl+3)"),
            ("|", None, None),  # 구분선
            ("B", "**", "굵게 (Ctrl+B)"),
            ("I", "*", "기울임 (Ctrl+I)"),
            ("S", "~~", "취소선"),
            ("C", "`", "인라인 코드"),
            ("|", None, None),
            ("•", "- ", "목록"),
            ("1.", "1. ", "번호 목록"),
            ("☐", "- [ ] ", "체크리스트"),
            ("|", None, None),
            ("🔗", "link", "링크 삽입 (Ctrl+K)"),
            ("🖼", "image", "이미지 삽입"),
            ("📊", "table", "테이블 삽입"),
            ("😀", "emoji", "이모지 삽입"),
        ]
        
        for text, action, tooltip in buttons:
            if text == "|":
                toolbar.addSeparator()
            else:
                btn = toolbar.addAction(text)
                if tooltip:
                    btn.setToolTip(tooltip)
                
                if action == "link":
                    btn.triggered.connect(self.insert_link)
                elif action == "image":
                    btn.triggered.connect(self.insert_image)
                elif action == "table":
                    btn.triggered.connect(self.insert_table)
                elif action == "emoji":
                    btn.triggered.connect(self.insert_emoji)
                elif action in ["**", "*", "~~", "`"]:
                    btn.triggered.connect(lambda checked, a=action: self.wrap_selection(a))
                else:
                    btn.triggered.connect(lambda checked, a=action: self.insert_at_line_start(a))
    
    def setup_shortcuts(self):
        """단축키 설정"""
        shortcuts = [
            ("Ctrl+1", lambda: self.insert_at_line_start("# ")),
            ("Ctrl+2", lambda: self.insert_at_line_start("## ")),
            ("Ctrl+3", lambda: self.insert_at_line_start("### ")),
            ("Ctrl+B", lambda: self.wrap_selection("**")),
            ("Ctrl+I", lambda: self.wrap_selection("*")),
            ("Ctrl+K", self.insert_link),
            ("Ctrl+Shift+K", self.insert_image),
            ("Ctrl+`", lambda: self.wrap_selection("`")),
            ("Ctrl+Shift+C", lambda: self.insert_text("```\n\n```")),
        ]
        
        for key, callback in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
    
    def setup_auto_save(self):
        """자동 저장 설정"""
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)  # 1분마다
    
    def apply_theme(self):
        """테마 적용"""
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
            self.highlighter.dark_mode = True
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.highlighter.dark_mode = False
        
        self.highlighter.setup_formats()
        self.highlighter.rehighlight()
        self.update_preview()
    
    def on_text_changed(self):
        """텍스트 변경 시"""
        self.is_modified = True
        self.update_title()
        self.update_word_count()
        
        # 디바운스된 미리보기 업데이트
        QTimer.singleShot(300, self.update_preview)
    
    def update_title(self):
        """창 제목 업데이트"""
        title = "MarkdownPro"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def update_word_count(self):
        """단어 수 업데이트"""
        text = self.editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.word_count_label.setText(f"단어: {words} | 문자: {chars}")
    
    def update_cursor_position(self):
        """커서 위치 업데이트"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.position_label.setText(f"줄: {line}, 열: {col}")
    
    def update_preview(self):
        """미리보기 업데이트"""
        text = self.editor.toPlainText()
        
        # 마크다운 변환
        md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br',
            'sane_lists',
        ])
        
        html_content = md.convert(text)
        
        # 스타일 추가
        if self.dark_mode:
            bg_color = "#1e1e1e"
            text_color = "#d4d4d4"
            code_bg = "#2d2d2d"
            link_color = "#4ec9b0"
            quote_border = "#4ec9b0"
        else:
            bg_color = "#ffffff"
            text_color = "#333333"
            code_bg = "#f5f5f5"
            link_color = "#0066cc"
            quote_border = "#0066cc"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
                h3 {{ font-size: 1.25em; }}
                code {{
                    background-color: {code_bg};
                    padding: 0.2em 0.4em;
                    border-radius: 3px;
                    font-family: 'SF Mono', Consolas, monospace;
                    font-size: 0.9em;
                }}
                pre {{
                    background-color: {code_bg};
                    padding: 16px;
                    border-radius: 6px;
                    overflow-x: auto;
                }}
                pre code {{
                    background: none;
                    padding: 0;
                }}
                blockquote {{
                    border-left: 4px solid {quote_border};
                    margin: 0;
                    padding-left: 16px;
                    color: #666;
                }}
                a {{
                    color: {link_color};
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: {code_bg};
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                ul, ol {{
                    padding-left: 2em;
                }}
                li {{
                    margin: 4px 0;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #ddd;
                    margin: 24px 0;
                }}
                input[type="checkbox"] {{
                    margin-right: 8px;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        self.preview.setHtml(html)
    
    def update_recent_menu(self):
        """최근 파일 메뉴 업데이트"""
        self.recent_menu.clear()
        
        for file_path in self.recent_files[:10]:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, f=file_path: self.open_file(f))
                self.recent_menu.addAction(action)
        
        if self.recent_files:
            self.recent_menu.addSeparator()
            clear_action = QAction("최근 파일 목록 지우기", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_menu.addAction(clear_action)
    
    def add_to_recent(self, file_path):
        """최근 파일에 추가"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]
        self.update_recent_menu()
        self.save_settings()
    
    def clear_recent_files(self):
        """최근 파일 목록 지우기"""
        self.recent_files.clear()
        self.update_recent_menu()
        self.save_settings()
    
    # 파일 작업
    def new_file(self):
        """새 파일"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "저장 확인",
                "변경사항을 저장하시겠습니까?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.update_title()
    
    def open_file(self, file_path=None):
        """파일 열기"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "파일 열기", "",
                "마크다운 파일 (*.md *.markdown *.txt);;모든 파일 (*.*)"
            )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = file_path
                self.is_modified = False
                self.update_title()
                self.add_to_recent(file_path)
                self.status_bar.showMessage(f"파일 열림: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일을 열 수 없습니다:\n{e}")
    
    def save_file(self):
        """파일 저장"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """다른 이름으로 저장"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "저장", "",
            "마크다운 파일 (*.md);;텍스트 파일 (*.txt);;모든 파일 (*.*)"
        )
        
        if file_path:
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path):
        """파일에 저장"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.add_to_recent(file_path)
            self.status_bar.showMessage(f"저장됨: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일을 저장할 수 없습니다:\n{e}")
    
    def auto_save(self):
        """자동 저장"""
        if self.current_file and self.is_modified:
            self._save_to_file(self.current_file)
    
    def export_html(self):
        """HTML로 내보내기"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "HTML로 내보내기", "",
            "HTML 파일 (*.html)"
        )
        
        if file_path:
            try:
                html = self.preview.page().toHtml(lambda html: self._write_html(file_path, html))
            except Exception as e:
                # 대체 방법
                text = self.editor.toPlainText()
                md = markdown.Markdown(extensions=['tables', 'fenced_code'])
                html_content = md.convert(text)
                
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Export</title>
</head>
<body>
{html_content}
</body>
</html>"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                self.status_bar.showMessage(f"HTML로 내보냄: {file_path}", 3000)
    
    def _write_html(self, file_path, html):
        """HTML 파일 쓰기"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.status_bar.showMessage(f"HTML로 내보냄: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"내보내기 실패:\n{e}")
    
    def export_pdf(self):
        """PDF로 내보내기"""
        try:
            from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "PDF로 내보내기", "",
                "PDF 파일 (*.pdf)"
            )
            
            if file_path:
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_path)
                
                self.preview.page().print(printer, lambda ok: self._pdf_done(ok, file_path))
        except ImportError:
            QMessageBox.warning(self, "알림", "PDF 내보내기를 위해 PyQt6-WebEngine이 필요합니다.")
    
    def _pdf_done(self, ok, file_path):
        if ok:
            self.status_bar.showMessage(f"PDF로 내보냄: {file_path}", 3000)
        else:
            QMessageBox.warning(self, "경고", "PDF 내보내기에 실패했습니다.")
    
    # 편집 기능
    def insert_text(self, text):
        """텍스트 삽입"""
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
    
    def insert_at_line_start(self, text):
        """줄 시작에 텍스트 삽입"""
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
    
    def wrap_selection(self, wrapper):
        """선택 텍스트 감싸기"""
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        
        if selected:
            cursor.insertText(f"{wrapper}{selected}{wrapper}")
        else:
            cursor.insertText(f"{wrapper}{wrapper}")
            # 커서를 wrapper 사이로 이동
            cursor.movePosition(QTextCursor.MoveOperation.Left, n=len(wrapper))
            self.editor.setTextCursor(cursor)
        
        self.editor.setFocus()
    
    def insert_completion(self, completion):
        """자동완성 삽입"""
        cursor = self.editor.textCursor()
        cursor.insertText(completion)
        self.editor.setTextCursor(cursor)
    
    def insert_template(self, content):
        """템플릿 삽입"""
        self.editor.setPlainText(content)
        self.is_modified = True
        self.update_title()
    
    def insert_table(self):
        """테이블 삽입"""
        dialog = TableDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.insert_text("\n" + dialog.get_table_markdown() + "\n")
    
    def insert_link(self):
        """링크 삽입"""
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        
        dialog = LinkDialog(self, selected)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if selected:
                cursor.insertText(dialog.get_markdown())
            else:
                self.insert_text(dialog.get_markdown())
    
    def insert_image(self):
        """이미지 삽입"""
        dialog = ImageDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.insert_text(dialog.get_markdown())
    
    def insert_emoji(self):
        """이모지 삽입"""
        dialog = EmojiDialog(self)
        dialog.emoji_selected.connect(self.insert_text)
        dialog.exec()
    
    def show_find_dialog(self):
        """찾기/바꾸기 다이얼로그"""
        dialog = FindReplaceDialog(self)
        dialog.show()
    
    # 보기 기능
    def toggle_preview(self):
        """미리보기 토글"""
        sizes = self.splitter.sizes()
        if sizes[1] > 0:
            self._preview_size = sizes[1]
            self.splitter.setSizes([sizes[0] + sizes[1], 0])
        else:
            self.splitter.setSizes([sizes[0] - self._preview_size, self._preview_size])
    
    def toggle_sidebar(self):
        """사이드바 토글"""
        if self.side_panel.isVisible():
            self.side_panel.hide()
        else:
            self.side_panel.show()
    
    def toggle_dark_mode(self):
        """다크 모드 토글"""
        self.dark_mode = not self.dark_mode
        self.dark_mode_action.setChecked(self.dark_mode)
        self.apply_theme()
        self.save_settings()
    
    # 도움말
    def show_about(self):
        """프로그램 정보"""
        QMessageBox.about(
            self, "MarkdownPro 정보",
            """<h2>MarkdownPro</h2>
            <p>버전 1.0.0</p>
            <p>고급 마크다운 에디터</p>
            <br>
            <p><b>기능:</b></p>
            <ul>
                <li>실시간 미리보기</li>
                <li>구문 강조</li>
                <li>자동완성</li>
                <li>다크 모드</li>
                <li>HTML/PDF 내보내기</li>
                <li>예제 템플릿</li>
            </ul>
            """
        )
    
    def show_shortcuts(self):
        """단축키 안내"""
        shortcuts = """
        <h3>단축키 안내</h3>
        <table>
            <tr><td><b>Ctrl+N</b></td><td>새 문서</td></tr>
            <tr><td><b>Ctrl+O</b></td><td>열기</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>저장</td></tr>
            <tr><td><b>Ctrl+Shift+S</b></td><td>다른 이름으로 저장</td></tr>
            <tr><td><b>Ctrl+F</b></td><td>찾기/바꾸기</td></tr>
            <tr><td><b>Ctrl+1/2/3</b></td><td>제목 1/2/3</td></tr>
            <tr><td><b>Ctrl+B</b></td><td>굵게</td></tr>
            <tr><td><b>Ctrl+I</b></td><td>기울임</td></tr>
            <tr><td><b>Ctrl+K</b></td><td>링크 삽입</td></tr>
            <tr><td><b>Ctrl+`</b></td><td>인라인 코드</td></tr>
            <tr><td><b>Ctrl+Z</b></td><td>실행 취소</td></tr>
            <tr><td><b>Ctrl+Y</b></td><td>다시 실행</td></tr>
        </table>
        """
        
        QMessageBox.information(self, "단축키", shortcuts)
    
    def closeEvent(self, event):
        """종료 이벤트"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "저장 확인",
                "변경사항을 저장하시겠습니까?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        
        self.save_settings()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MarkdownPro")
    app.setOrganizationName("MarkdownPro")
    
    # 기본 폰트 설정
    font = QFont("SF Pro Text", 13)
    app.setFont(font)
    
    window = MarkdownEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
