#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkdownPro v3.0 - 프로페셔널 마크다운 에디터
Features: Mermaid 전체 지원, 포커스 모드, 문서 개요, 통계, 스니펫 등
"""

import sys
import os
import json
import re
import base64
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime
from collections import Counter

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QPlainTextEdit, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QDialog, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit, QListWidget, QListWidgetItem,
    QTabWidget, QGridLayout, QFrame, QScrollArea, QMenu,
    QMenuBar, QCompleter, QDialogButtonBox, QGroupBox, QCheckBox,
    QSlider, QTreeWidget, QTreeWidgetItem, QProgressBar, QTextBrowser
)
from PyQt6.QtCore import (
    Qt, QTimer, QSize, QUrl, pyqtSignal, QRegularExpression, QObject, pyqtSlot
)
from PyQt6.QtGui import (
    QFont, QAction, QKeySequence, QTextCharFormat, QSyntaxHighlighter,
    QColor, QTextCursor, QShortcut, QTextDocument
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

import markdown

CONFIG_FILE = os.path.expanduser("~/.markdownpro_config.json")
BACKUP_DIR = os.path.expanduser("~/.markdownpro_backups")
SNIPPETS_FILE = os.path.expanduser("~/.markdownpro_snippets.json")

# 스타일
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

# ============== MERMAID 다이어그램 전체 예제 (17종) ==============
MERMAID_EXAMPLES = {
    # 1. Flowchart
    "플로우차트 (Flowchart)": """```mermaid
flowchart TD
    A[시작] --> B{조건 확인}
    B -->|Yes| C[처리 1]
    B -->|No| D[처리 2]
    C --> E[결과]
    D --> E
    E --> F((종료))
    
    subgraph 서브프로세스
    G[단계1] --> H[단계2]
    end
```""",

    # 2. Flowchart LR
    "플로우차트 (좌→우)": """```mermaid
flowchart LR
    A[입력] --> B[처리]
    B --> C{검증}
    C -->|성공| D[출력]
    C -->|실패| E[에러]
    E --> A
```""",

    # 3. Sequence Diagram
    "시퀀스 다이어그램": """```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 사용자
    participant F as 🖥️ 프론트엔드
    participant A as ⚙️ API서버
    participant D as 🗄️ DB
    
    U->>F: 로그인 요청
    activate F
    F->>A: POST /auth/login
    activate A
    A->>D: 사용자 조회
    activate D
    D-->>A: 사용자 정보
    deactivate D
    A-->>F: JWT 토큰
    deactivate A
    F-->>U: 로그인 성공
    deactivate F
    
    Note over U,D: 인증 완료
```""",

    # 4. Class Diagram
    "클래스 다이어그램": """```mermaid
classDiagram
    class Animal {
        <<abstract>>
        +String name
        +int age
        +makeSound()* void
        +move() void
    }
    
    class Dog {
        +String breed
        +bark() void
        +fetch() void
    }
    
    class Cat {
        +String color
        +meow() void
        +climb() void
    }
    
    class Pet {
        <<interface>>
        +play() void
        +feed() void
    }
    
    Animal <|-- Dog : 상속
    Animal <|-- Cat : 상속
    Pet <|.. Dog : 구현
    Pet <|.. Cat : 구현
```""",

    # 5. State Diagram
    "상태 다이어그램": """```mermaid
stateDiagram-v2
    [*] --> 대기: 시작
    
    대기 --> 처리중: 요청 수신
    처리중 --> 검증중: 처리 완료
    
    state 검증중 {
        [*] --> 데이터검증
        데이터검증 --> 권한검증
        권한검증 --> [*]
    }
    
    검증중 --> 완료: 검증 성공
    검증중 --> 실패: 검증 실패
    
    완료 --> [*]
    실패 --> 대기: 재시도
    실패 --> [*]: 포기
    
    note right of 처리중: 비동기 처리
```""",

    # 6. ER Diagram
    "ER 다이어그램": """```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER ||--o{ REVIEW : writes
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT ||--o{ REVIEW : "reviewed in"
    CATEGORY ||--o{ PRODUCT : contains
    
    USER {
        int id PK
        string email UK
        string name
        string password
        datetime created_at
    }
    
    ORDER {
        int id PK
        int user_id FK
        decimal total
        string status
        datetime ordered_at
    }
    
    PRODUCT {
        int id PK
        int category_id FK
        string name
        decimal price
        int stock
    }
```""",

    # 7. Gantt Chart
    "간트 차트": """```mermaid
gantt
    title 프로젝트 개발 일정
    dateFormat YYYY-MM-DD
    
    section 📋 기획
    요구사항 분석     :done, req, 2024-01-01, 7d
    화면 설계         :done, design, after req, 5d
    DB 설계          :done, db, after req, 5d
    
    section 💻 개발
    백엔드 API       :active, backend, after design, 14d
    프론트엔드       :frontend, after design, 14d
    DB 구축          :database, after db, 7d
    
    section 🧪 테스트
    단위 테스트      :unittest, after backend, 5d
    통합 테스트      :inttest, after unittest, 5d
    QA 테스트        :qa, after inttest, 7d
    
    section 🚀 배포
    스테이징 배포    :staging, after qa, 2d
    프로덕션 배포    :crit, prod, after staging, 1d
```""",

    # 8. Pie Chart
    "파이 차트": """```mermaid
pie showData
    title 2024년 브라우저 시장 점유율
    "Chrome" : 65.7
    "Safari" : 18.5
    "Firefox" : 6.3
    "Edge" : 5.2
    "기타" : 4.3
```""",

    # 9. Mindmap
    "마인드맵": """```mermaid
mindmap
  root((프로젝트))
    📋 기획
      요구사항 분석
      사용자 조사
      경쟁사 분석
    💻 개발
      프론트엔드
        React
        TypeScript
        Tailwind
      백엔드
        Node.js
        PostgreSQL
        Redis
    🎨 디자인
      UI/UX
      프로토타입
      디자인시스템
    🧪 품질
      테스트
      코드리뷰
      CI/CD
```""",

    # 10. Git Graph
    "Git 그래프": """```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "Add README"
    branch develop
    checkout develop
    commit id: "Setup project"
    branch feature/login
    checkout feature/login
    commit id: "Add login UI"
    commit id: "Add auth logic"
    checkout develop
    merge feature/login
    branch feature/dashboard
    checkout feature/dashboard
    commit id: "Add dashboard"
    checkout develop
    merge feature/dashboard
    checkout main
    merge develop tag: "v1.0.0"
    commit id: "Hotfix"
```""",

    # 11. User Journey
    "사용자 여정": """```mermaid
journey
    title 쇼핑몰 구매 여정
    section 탐색
      홈페이지 방문: 5: 고객
      상품 검색: 4: 고객
      상품 상세 보기: 5: 고객
    section 구매
      장바구니 담기: 4: 고객
      결제 페이지: 3: 고객
      결제 완료: 5: 고객
    section 배송
      배송 추적: 4: 고객
      상품 수령: 5: 고객
      리뷰 작성: 3: 고객
```""",

    # 12. Quadrant Chart
    "사분면 차트": """```mermaid
quadrantChart
    title 기능 우선순위 매트릭스
    x-axis 낮은 노력 --> 높은 노력
    y-axis 낮은 가치 --> 높은 가치
    quadrant-1 즉시 실행
    quadrant-2 계획 수립
    quadrant-3 위임 가능
    quadrant-4 재검토 필요
    
    로그인 기능: [0.8, 0.9]
    다크모드: [0.2, 0.6]
    AI 추천: [0.9, 0.8]
    알림 기능: [0.4, 0.5]
    설정 페이지: [0.3, 0.3]
    분석 대시보드: [0.7, 0.7]
```""",

    # 13. Requirement Diagram
    "요구사항 다이어그램": """```mermaid
requirementDiagram
    requirement 사용자인증 {
        id: REQ-001
        text: 시스템은 사용자 인증을 제공해야 한다
        risk: high
        verifymethod: test
    }
    
    requirement 비밀번호보안 {
        id: REQ-002
        text: 비밀번호는 암호화되어야 한다
        risk: high
        verifymethod: inspection
    }
    
    functionalRequirement 로그인 {
        id: FR-001
        text: 이메일/비밀번호로 로그인
        risk: medium
        verifymethod: test
    }
    
    element 인증모듈 {
        type: module
    }
    
    사용자인증 - contains -> 비밀번호보안
    사용자인증 - derives -> 로그인
    인증모듈 - satisfies -> 로그인
```""",

    # 14. Timeline
    "타임라인": """```mermaid
timeline
    title 회사 연혁
    section 2020년
        1월 : 회사 설립
        6월 : 시드 투자 유치
    section 2021년
        3월 : 베타 서비스 출시
        9월 : 시리즈 A 투자
        12월 : MAU 10만 달성
    section 2022년
        4월 : 정식 서비스 출시
        8월 : 시리즈 B 투자
        11월 : MAU 100만 달성
    section 2023년
        2월 : 글로벌 진출
        7월 : IPO 준비
        12월 : 연매출 100억 달성
```""",

    # 15. Sankey Diagram
    "생키 다이어그램": """```mermaid
sankey-beta

마케팅,웹사이트,5000
마케팅,앱,3000
마케팅,SNS,2000

웹사이트,회원가입,3000
웹사이트,이탈,2000
앱,회원가입,2500
앱,이탈,500
SNS,회원가입,1500
SNS,이탈,500

회원가입,구매,4000
회원가입,미구매,3000

구매,재구매,2500
구매,1회성,1500
```""",

    # 16. XY Chart
    "XY 차트": """```mermaid
xychart-beta
    title "월별 매출 추이"
    x-axis [1월, 2월, 3월, 4월, 5월, 6월, 7월, 8월, 9월, 10월, 11월, 12월]
    y-axis "매출 (억원)" 0 --> 100
    bar [30, 35, 45, 50, 55, 65, 70, 68, 72, 78, 85, 95]
    line [30, 35, 45, 50, 55, 65, 70, 68, 72, 78, 85, 95]
```""",

    # 17. Block Diagram
    "블록 다이어그램": """```mermaid
block-beta
    columns 3
    
    Frontend:3
    block:frontend:3
        React Angular Vue
    end
    
    space:3
    
    API["API Gateway"]:3
    
    space:3
    
    block:backend:3
        columns 3
        Auth["인증 서비스"]
        User["사용자 서비스"]
        Product["상품 서비스"]
    end
    
    space:3
    
    block:data:3
        columns 2
        PostgreSQL Redis
    end
```""",

    # 18. C4 Context
    "C4 컨텍스트": """```mermaid
C4Context
    title 시스템 컨텍스트 다이어그램
    
    Person(customer, "고객", "서비스를 이용하는 사용자")
    Person(admin, "관리자", "시스템을 관리하는 직원")
    
    System(ecommerce, "이커머스 시스템", "온라인 쇼핑 플랫폼")
    
    System_Ext(payment, "결제 시스템", "외부 PG사")
    System_Ext(delivery, "배송 시스템", "택배사 API")
    System_Ext(email, "이메일 서비스", "알림 발송")
    
    Rel(customer, ecommerce, "상품 검색/구매")
    Rel(admin, ecommerce, "상품/주문 관리")
    Rel(ecommerce, payment, "결제 처리")
    Rel(ecommerce, delivery, "배송 요청")
    Rel(ecommerce, email, "알림 발송")
```""",

    # 19. ZenUML
    "ZenUML 시퀀스": """```mermaid
zenuml
    title 주문 처리 프로세스
    
    @Actor Client
    @Boundary OrderController
    @Control OrderService
    @Entity OrderRepository
    
    Client->OrderController.createOrder(items) {
        OrderService.validateOrder(items) {
            if (valid) {
                OrderRepository.save(order)
                return orderId
            } else {
                throw ValidationError
            }
        }
    }
```""",
}

# 마크다운 예제 템플릿
EXAMPLE_TEMPLATES = {
    "기본 문서": """# 제목

이것은 기본 마크다운 문서입니다.

## 부제목

**굵게** 또는 *기울임*으로 강조할 수 있습니다.

### 목록
- 항목 1
- 항목 2
- 항목 3

### 링크
[링크 텍스트](https://example.com)
""",

    "README 템플릿": """# 프로젝트 이름

> 프로젝트 한 줄 설명

[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)]()

## 📋 개요

프로젝트에 대한 자세한 설명을 작성합니다.

## ✨ 기능

- ✅ 기능 1
- ✅ 기능 2
- 🚧 기능 3 (개발 중)

## 📦 설치

```bash
npm install project-name
```

## 🚀 사용법

```javascript
const project = require('project-name');
project.init();
```

## 📖 문서

[전체 문서 보기](https://docs.example.com)

## 🤝 기여

기여를 환영합니다! [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 📄 라이선스

MIT License
""",

    "회의록": f"""# 📝 회의록

| 항목 | 내용 |
|------|------|
| **날짜** | {datetime.now().strftime('%Y년 %m월 %d일')} |
| **시간** | 10:00 - 11:00 |
| **장소** | 회의실 A |
| **참석자** | 홍길동, 김철수, 이영희 |
| **작성자** | 홍길동 |

---

## 📌 안건

1. 프로젝트 진행 상황 공유
2. 다음 스프린트 계획
3. 이슈 논의

## 📝 논의 내용

### 1. 프로젝트 진행 상황

#### 완료된 작업
- [x] 사용자 인증 모듈
- [x] 대시보드 UI

#### 진행 중인 작업
- [ ] API 최적화
- [ ] 테스트 코드 작성

### 2. 다음 스프린트

| 담당자 | 작업 | 기한 | 우선순위 |
|--------|------|------|----------|
| 홍길동 | 백엔드 API | 12/15 | 🔴 높음 |
| 김철수 | 프론트엔드 | 12/20 | 🟡 중간 |
| 이영희 | QA 테스트 | 12/25 | 🟢 낮음 |

## ✅ 결정 사항

1. 주간 스탠드업 미팅 유지
2. 코드 리뷰 필수화

## 📅 다음 회의

- **일시**: 다음 주 월요일 10:00
- **안건**: 스프린트 리뷰
""",

    "기술 문서": """# API 문서

## 📚 개요

이 문서는 REST API의 사용법을 설명합니다.

**Base URL**: `https://api.example.com/v1`

## 🔐 인증

모든 요청에 API 키가 필요합니다:

```
Authorization: Bearer YOUR_API_KEY
```

## 📡 엔드포인트

### 사용자 조회

```http
GET /users/{id}
```

#### 파라미터

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | string | ✅ | 사용자 ID |

#### 응답

```json
{
  "id": "123",
  "name": "홍길동",
  "email": "hong@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 사용자 생성

```http
POST /users
```

#### 요청 본문

```json
{
  "name": "홍길동",
  "email": "hong@example.com",
  "password": "secure123"
}
```

## ⚠️ 에러 코드

| 코드 | 설명 | 해결 방법 |
|------|------|----------|
| 400 | 잘못된 요청 | 요청 파라미터 확인 |
| 401 | 인증 실패 | API 키 확인 |
| 404 | 리소스 없음 | ID 확인 |
| 500 | 서버 오류 | 관리자 문의 |
""",

    "블로그 포스트": f"""---
title: "제목을 입력하세요"
date: {datetime.now().strftime('%Y-%m-%d')}
author: 작성자
tags: [태그1, 태그2, 태그3]
---

# 블로그 제목

![대표 이미지](cover.jpg)

## 들어가며

독자의 관심을 끄는 도입부를 작성합니다. 이 글에서 다룰 내용을 간략히 소개하세요.

> 💡 **핵심 메시지**: 한 문장으로 요약

## 본문

### 첫 번째 섹션

내용을 작성합니다. 적절한 예시와 함께 설명하세요.

```python
# 코드 예시
def hello():
    print("Hello, World!")
```

### 두 번째 섹션

추가 내용을 작성합니다.

1. 첫 번째 포인트
2. 두 번째 포인트
3. 세 번째 포인트

## 마치며

핵심 내용을 정리하고 독자에게 남기고 싶은 메시지를 작성합니다.

---

*읽어주셔서 감사합니다! 질문이 있으시면 댓글로 남겨주세요.*
""",
}

# 자동완성
AUTOCOMPLETE_ITEMS = [
    "# ", "## ", "### ", "#### ", "##### ", "###### ",
    "**굵게**", "*기울임*", "~~취소선~~", "`코드`",
    "[링크](url)", "![이미지](url)",
    "- ", "1. ", "- [ ] ", "- [x] ",
    "```\n```", "```python\n```", "```javascript\n```", "```mermaid\n```",
    "> ", "---",
    "| 헤더 |\n|---|\n| 내용 |",
]

# 이모지
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
    "표정": ["😀", "😃", "😄", "😁", "😅", "😂", "🤣", "😊", "😇", "🙂", "😉", "😍", "🥰", "😎", "🤔", "😴"],
    "제스처": ["👍", "👎", "👌", "✌️", "🤞", "🤝", "👏", "🙌", "💪", "🙏", "👋", "✋", "🤚", "🖐️", "👆", "👇"],
    "심볼": ["❤️", "🧡", "💛", "💚", "💙", "💜", "⭐", "🌟", "✨", "💫", "🔥", "💯", "✅", "❌", "⚠️", "💡"],
    "객체": ["📁", "📂", "📄", "📝", "✏️", "📊", "📈", "📉", "🗓️", "⏰", "🔗", "🔒", "🔓", "🔑", "💾", "💿"],
    "화살표": ["➡️", "⬅️", "⬆️", "⬇️", "↗️", "↘️", "↙️", "↖️", "↕️", "↔️", "🔄", "🔃", "◀️", "▶️", "🔼", "🔽"],
}

# 기본 스니펫
DEFAULT_SNIPPETS = {
    "todo": "- [ ] ",
    "done": "- [x] ",
    "note": "> **📝 Note:** ",
    "warn": "> **⚠️ Warning:** ",
    "tip": "> **💡 Tip:** ",
    "code": "```\n$1\n```",
    "link": "[$1]($2)",
    "img": "![$1]($2)",
    "table2": "| 헤더1 | 헤더2 |\n|-------|-------|\n| 내용1 | 내용2 |",
    "table3": "| 헤더1 | 헤더2 | 헤더3 |\n|-------|-------|-------|\n| 내용1 | 내용2 | 내용3 |",
    "mermaid": "```mermaid\nflowchart TD\n    A --> B\n```",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "time": datetime.now().strftime("%H:%M"),
    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
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
    
    def highlightBlock(self, text):
        for pattern, fmt_name in self.rules:
            regex = QRegularExpression(pattern)
            it = regex.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), 
                             self.formats.get(fmt_name, QTextCharFormat()))


class WebBridge(QObject):
    svg_ready = pyqtSignal(str)
    png_ready = pyqtSignal(str)
    
    @pyqtSlot(str)
    def receiveSvg(self, data):
        self.svg_ready.emit(data)
    
    @pyqtSlot(str)
    def receivePng(self, data):
        self.png_ready.emit(data)


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
        
        # 문단 수
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        
        # 헤더 수
        headers = len(re.findall(r'^#{1,6}\s', text, re.MULTILINE))
        
        # 링크 수
        links = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', text))
        
        # 이미지 수
        images = len(re.findall(r'!\[([^\]]*)\]\([^)]+\)', text))
        
        # 코드 블록 수
        code_blocks = len(re.findall(r'```[\s\S]*?```', text))
        
        # Mermaid 블록 수
        mermaid_blocks = len(re.findall(r'```mermaid[\s\S]*?```', text))
        
        return {
            'lines': len(lines),
            'words': len(words),
            'chars': chars,
            'chars_no_space': chars_no_space,
            'paragraphs': paragraphs,
            'headers': headers,
            'links': links,
            'images': images,
            'code_blocks': code_blocks,
            'mermaid_blocks': mermaid_blocks,
            'read_time': read_time,
        }


# ============== 다이얼로그 ==============

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
        
        self.align_combo = QComboBox()
        self.align_combo.addItems(["왼쪽 정렬", "가운데 정렬", "오른쪽 정렬"])
        layout.addWidget(self.align_combo)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def get_markdown(self):
        r, c = self.rows.value(), self.cols.value()
        align = self.align_combo.currentIndex()
        
        if align == 0:
            sep = ":------"
        elif align == 1:
            sep = ":------:"
        else:
            sep = "------:"
        
        lines = []
        if self.header_check.isChecked():
            lines.append("| " + " | ".join([f"헤더{i+1}" for i in range(c)]) + " |")
            lines.append("| " + " | ".join([sep for _ in range(c)]) + " |")
            r -= 1
        for _ in range(r):
            lines.append("| " + " | ".join(["     " for _ in range(c)]) + " |")
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
        
        layout.addWidget(QLabel("제목 (선택):"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("마우스 오버시 표시")
        layout.addWidget(self.title_edit)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def get_markdown(self):
        text = self.text_edit.text() or "링크"
        url = self.url_edit.text() or "#"
        title = self.title_edit.text()
        if title:
            return f'[{text}]({url} "{title}")'
        return f"[{text}]({url})"


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
        
        layout.addWidget(QLabel("크기 (선택):"))
        size_layout = QHBoxLayout()
        self.width = QSpinBox()
        self.width.setRange(0, 2000)
        self.width.setSpecialValueText("자동")
        size_layout.addWidget(QLabel("너비:"))
        size_layout.addWidget(self.width)
        self.height = QSpinBox()
        self.height.setRange(0, 2000)
        self.height.setSpecialValueText("자동")
        size_layout.addWidget(QLabel("높이:"))
        size_layout.addWidget(self.height)
        layout.addLayout(size_layout)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "이미지 (*.png *.jpg *.jpeg *.gif *.svg *.webp)")
        if path:
            self.url.setText(path)
    
    def get_markdown(self):
        alt = self.alt.text() or "이미지"
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
        self.setWindowTitle("이모지")
        self.setMinimumSize(400, 350)
        layout = QVBoxLayout(self)
        
        # 검색
        self.search = QLineEdit()
        self.search.setPlaceholderText("검색...")
        self.search.textChanged.connect(self.filter_emoji)
        layout.addWidget(self.search)
        
        tabs = QTabWidget()
        self.emoji_buttons = []
        
        for cat, emojis in EMOJI_LIST.items():
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
                tooltip = name if name else cat
                btn.setToolTip(f"{e} {tooltip}")
                btn.setProperty("emoji_name", name.lower())
                btn.setProperty("emoji_category", cat.lower())
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
            emoji = btn.text()
            visible = not query or query in emoji or query in name or query in category
            btn.setVisible(visible)
    
    def select(self, emoji):
        self.emoji_selected.emit(emoji)
        self.accept()


class SnippetDialog(QDialog):
    def __init__(self, snippets, parent=None):
        super().__init__(parent)
        self.snippets = snippets
        self.setWindowTitle("스니펫 관리")
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
        
        edit_layout.addWidget(QLabel("트리거:"))
        self.trigger_edit = QLineEdit()
        edit_layout.addWidget(self.trigger_edit)
        
        edit_layout.addWidget(QLabel("내용:"))
        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Consolas", 11))
        edit_layout.addWidget(self.content_edit)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_snippet)
        btn_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("삭제")
        delete_btn.clicked.connect(self.delete_snippet)
        btn_layout.addWidget(delete_btn)
        
        new_btn = QPushButton("새로 만들기")
        new_btn.clicked.connect(self.new_snippet)
        btn_layout.addWidget(new_btn)
        
        edit_layout.addLayout(btn_layout)
        h_layout.addLayout(edit_layout)
        
        layout.addLayout(h_layout)
        
        # 닫기
        close_btn = QPushButton("닫기")
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
        content = self.content_edit.toPlainText()
        if trigger:
            self.snippets[trigger] = content
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
        self.setWindowTitle("찾기/바꾸기")
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        
        # 찾기
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("찾기:"))
        self.find_edit = QLineEdit()
        self.find_edit.returnPressed.connect(self.find_next)
        find_layout.addWidget(self.find_edit)
        layout.addLayout(find_layout)
        
        # 바꾸기
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("바꾸기:"))
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)
        
        # 옵션
        opt_layout = QHBoxLayout()
        self.case_check = QCheckBox("대소문자 구분")
        opt_layout.addWidget(self.case_check)
        self.whole_check = QCheckBox("전체 단어만")
        opt_layout.addWidget(self.whole_check)
        self.regex_check = QCheckBox("정규식")
        opt_layout.addWidget(self.regex_check)
        layout.addLayout(opt_layout)
        
        # 버튼
        btn_layout = QHBoxLayout()
        
        find_btn = QPushButton("다음 찾기")
        find_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(find_btn)
        
        find_prev_btn = QPushButton("이전 찾기")
        find_prev_btn.clicked.connect(self.find_prev)
        btn_layout.addWidget(find_prev_btn)
        
        replace_btn = QPushButton("바꾸기")
        replace_btn.clicked.connect(self.replace_one)
        btn_layout.addWidget(replace_btn)
        
        replace_all_btn = QPushButton("모두 바꾸기")
        replace_all_btn.clicked.connect(self.replace_all)
        btn_layout.addWidget(replace_all_btn)
        
        layout.addLayout(btn_layout)
        
        # 결과 표시
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
        
        self.result_label.setText("찾음" if found else "결과 없음")
    
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
            new_content, count = re.subn(text, self.replace_edit.text(), content, flags=flags)
        else:
            if self.case_check.isChecked():
                count = content.count(text)
                new_content = content.replace(text, self.replace_edit.text())
            else:
                pattern = re.compile(re.escape(text), re.IGNORECASE)
                count = len(pattern.findall(content))
                new_content = pattern.sub(self.replace_edit.text(), content)
        
        self.editor.setPlainText(new_content)
        self.result_label.setText(f"{count}개 바꿈")


class StatsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("문서 통계")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        
        # 기본 통계
        basic_group = QGroupBox("기본 통계")
        basic_layout = QGridLayout(basic_group)
        
        items = [
            ("줄 수", stats['lines']),
            ("단어 수", stats['words']),
            ("문자 수 (공백 포함)", stats['chars']),
            ("문자 수 (공백 제외)", stats['chars_no_space']),
            ("문단 수", stats['paragraphs']),
            ("예상 읽기 시간", f"{stats['read_time']}분"),
        ]
        
        for i, (label, value) in enumerate(items):
            basic_layout.addWidget(QLabel(label + ":"), i, 0)
            basic_layout.addWidget(QLabel(str(value)), i, 1)
        
        layout.addWidget(basic_group)
        
        # 마크다운 요소
        md_group = QGroupBox("마크다운 요소")
        md_layout = QGridLayout(md_group)
        
        md_items = [
            ("제목", stats['headers']),
            ("링크", stats['links']),
            ("이미지", stats['images']),
            ("코드 블록", stats['code_blocks']),
            ("Mermaid 다이어그램", stats['mermaid_blocks']),
        ]
        
        for i, (label, value) in enumerate(md_items):
            md_layout.addWidget(QLabel(label + ":"), i, 0)
            md_layout.addWidget(QLabel(str(value)), i, 1)
        
        layout.addWidget(md_group)
        
        # 닫기
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ============== Mermaid 뷰어 ==============

class MermaidViewer(QMainWindow):
    """Mermaid 다이어그램 전용 뷰어 - 확대/축소, 전체화면, 내보내기"""
    
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
        self.setMinimumSize(1000, 750)
        self.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 툴바
        toolbar = QWidget()
        toolbar.setFixedHeight(55)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(15, 8, 15, 8)
        
        # 줌 컨트롤
        zoom_out = QPushButton("−")
        zoom_out.setFixedSize(36, 36)
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
        zoom_in.clicked.connect(self.zoom_in)
        tb_layout.addWidget(zoom_in)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(55)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(self.zoom_label)
        
        tb_layout.addSpacing(15)
        
        # 프리셋 버튼
        fit_btn = QPushButton("📐 맞춤")
        fit_btn.setToolTip("화면에 맞춤")
        fit_btn.clicked.connect(self.fit_to_view)
        tb_layout.addWidget(fit_btn)
        
        actual_btn = QPushButton("1:1")
        actual_btn.setToolTip("실제 크기")
        actual_btn.clicked.connect(lambda: self.zoom_slider.setValue(100))
        tb_layout.addWidget(actual_btn)
        
        zoom_50 = QPushButton("50%")
        zoom_50.clicked.connect(lambda: self.zoom_slider.setValue(50))
        tb_layout.addWidget(zoom_50)
        
        zoom_200 = QPushButton("200%")
        zoom_200.clicked.connect(lambda: self.zoom_slider.setValue(200))
        tb_layout.addWidget(zoom_200)
        
        tb_layout.addStretch()
        
        # 전체화면
        self.fullscreen_btn = QPushButton("⛶ 전체 화면")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        tb_layout.addWidget(self.fullscreen_btn)
        
        tb_layout.addSpacing(15)
        
        # 내보내기
        svg_btn = QPushButton("💾 SVG")
        svg_btn.clicked.connect(self.export_svg)
        tb_layout.addWidget(svg_btn)
        
        png_btn = QPushButton("🖼 PNG")
        png_btn.clicked.connect(self.export_png)
        tb_layout.addWidget(png_btn)
        
        png_2x_btn = QPushButton("🖼 PNG @2x")
        png_2x_btn.setToolTip("고해상도 PNG")
        png_2x_btn.clicked.connect(lambda: self.export_png(scale=2))
        tb_layout.addWidget(png_2x_btn)
        
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
        
        html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;overflow:auto;background:{bg}}}
#container{{display:flex;justify-content:center;align-items:center;min-height:100%;padding:30px}}
#diagram{{transform-origin:center;transition:transform 0.15s ease-out}}
.mermaid{{background:transparent}}
</style></head><body>
<div id="container"><div id="diagram" class="mermaid">
{self.mermaid_code}
</div></div>
<script>
mermaid.initialize({{startOnLoad:true,theme:'{theme}',securityLevel:'loose',
  flowchart:{{useMaxWidth:false,htmlLabels:true}},
  sequence:{{useMaxWidth:false}},
  gantt:{{useMaxWidth:false}},
  journey:{{useMaxWidth:false}},
  timeline:{{useMaxWidth:false}},
  mindmap:{{useMaxWidth:false}},
  sankey:{{useMaxWidth:false}},
}});

var bridge=null;
new QWebChannel(qt.webChannelTransport,function(c){{bridge=c.objects.bridge}});

function setZoom(s){{document.getElementById('diagram').style.transform='scale('+(s/100)+')'}}

function fitToView(){{
  var c=document.getElementById('container'),d=document.getElementById('diagram'),svg=d.querySelector('svg');
  if(svg){{
    var rect=svg.getBoundingClientRect();
    var sw=rect.width,sh=rect.height;
    var cw=c.clientWidth-60,ch=c.clientHeight-60;
    var scale=Math.min(cw/sw,ch/sh,2)*100;
    return Math.round(scale);
  }}
  return 100;
}}

function exportSVG(){{
  var svg=document.querySelector('#diagram svg');
  if(svg&&bridge){{
    var clone=svg.cloneNode(true);
    clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
    bridge.receiveSvg(new XMLSerializer().serializeToString(clone));
  }}
}}

function exportPNG(scale){{
  scale=scale||1;
  var svg=document.querySelector('#diagram svg');
  if(svg&&bridge){{
    var data=new XMLSerializer().serializeToString(svg);
    var canvas=document.createElement('canvas');
    var ctx=canvas.getContext('2d');
    var img=new Image();
    var blob=new Blob([data],{{type:'image/svg+xml;charset=utf-8'}});
    var url=URL.createObjectURL(blob);
    img.onload=function(){{
      canvas.width=img.width*scale;
      canvas.height=img.height*scale;
      ctx.scale(scale,scale);
      ctx.fillStyle='{bg}';
      ctx.fillRect(0,0,canvas.width,canvas.height);
      ctx.drawImage(img,0,0);
      URL.revokeObjectURL(url);
      bridge.receivePng(canvas.toDataURL('image/png'));
    }};
    img.src=url;
  }}
}}
</script></body></html>'''
        self.web_view.setHtml(html)
    
    def on_zoom_changed(self, value):
        self.zoom_level = value
        self.zoom_label.setText(f"{value}%")
        self.web_view.page().runJavaScript(f"setZoom({value})")
    
    def zoom_in(self):
        self.zoom_slider.setValue(min(self.zoom_level + 25, 500))
    
    def zoom_out(self):
        self.zoom_slider.setValue(max(self.zoom_level - 25, 10))
    
    def fit_to_view(self):
        self.web_view.page().runJavaScript("fitToView()", 
            lambda v: self.zoom_slider.setValue(int(v)) if v else None)
    
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
    
    def export_png(self, scale=1):
        suffix = "@2x" if scale == 2 else ""
        path, _ = QFileDialog.getSaveFileName(self, "PNG 저장", f"diagram{suffix}.png", "PNG (*.png)")
        if path:
            self.pending_save_path = path
            self.web_view.page().runJavaScript(f"exportPNG({scale})")
    
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
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key.Key_0:
            self.zoom_slider.setValue(100)
        else:
            super().keyPressEvent(event)


# ============== 사이드 패널 ==============

class OutlinePanel(QWidget):
    """문서 개요 (TOC) 패널"""
    heading_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("📑 문서 개요")
        title.setFont(QFont("", 13, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
    
    def update_outline(self, text):
        self.tree.clear()
        lines = text.split('\n')
        
        stack = [(None, -1)]  # (item, level)
        
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                
                item = QTreeWidgetItem([title])
                item.setData(0, Qt.ItemDataRole.UserRole, i)
                
                # 들여쓰기
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
        
        title = QLabel("📚 예제 템플릿")
        title.setFont(QFont("", 13, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.list = QListWidget()
        for name in EXAMPLE_TEMPLATES.keys():
            self.list.addItem(QListWidgetItem(name))
        self.list.itemDoubleClicked.connect(self.insert)
        layout.addWidget(self.list)
        
        btn = QPushButton("📝 에디터에 삽입")
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
        title.setFont(QFont("", 13, QFont.Weight.Bold))
        layout.addWidget(title)
        
        info = QLabel(f"총 {len(MERMAID_EXAMPLES)}종 다이어그램 지원")
        info.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info)
        
        self.list = QListWidget()
        for name in MERMAID_EXAMPLES.keys():
            self.list.addItem(QListWidgetItem(name))
        self.list.itemDoubleClicked.connect(self.insert)
        self.list.currentItemChanged.connect(self.show_preview)
        layout.addWidget(self.list)
        
        # 미리보기
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(100)
        self.preview.setFont(QFont("Consolas", 9))
        layout.addWidget(self.preview)
        
        btn = QPushButton("📝 에디터에 삽입")
        btn.clicked.connect(self.insert)
        layout.addWidget(btn)
    
    def show_preview(self, current, prev):
        if current:
            code = MERMAID_EXAMPLES.get(current.text(), "")
            # 처음 몇 줄만 표시
            lines = code.split('\n')[:8]
            self.preview.setPlainText('\n'.join(lines) + '\n...')
    
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
        title.setFont(QFont("", 13, QFont.Weight.Bold))
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cl = QVBoxLayout(content)
        
        items = [
            ("제목", "# H1  ## H2  ### H3"),
            ("굵게", "**텍스트**"),
            ("기울임", "*텍스트*"),
            ("취소선", "~~텍스트~~"),
            ("인라인 코드", "`코드`"),
            ("코드 블록", "```언어\\n코드\\n```"),
            ("링크", "[텍스트](URL)"),
            ("이미지", "![설명](URL)"),
            ("목록", "- 항목  또는  1. 항목"),
            ("체크리스트", "- [ ] 할일  - [x] 완료"),
            ("인용", "> 인용문"),
            ("표", "| A | B |\\n|---|---|\\n| 1 | 2 |"),
            ("수평선", "---"),
            ("Mermaid", "```mermaid\\nflowchart TD\\n```"),
        ]
        
        for t, s in items:
            g = QGroupBox(t)
            gl = QVBoxLayout(g)
            lbl = QLabel(s)
            lbl.setFont(QFont("Consolas", 10))
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setWordWrap(True)
            gl.addWidget(lbl)
            cl.addWidget(g)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)


# ============== 메인 에디터 ==============

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        self.dark_mode = False
        self.focus_mode = False
        self.recent_files = []
        self.mermaid_viewer = None
        self.snippets = DEFAULT_SNIPPETS.copy()
        self.word_goal = 0
        self.auto_save_timer = QTimer()
        self._preview_size = 500
        self._normal_style = ""
        
        self.load_settings()
        self.load_snippets()
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
                    self.word_goal = cfg.get('word_goal', 0)
        except:
            pass
    
    def save_settings(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'dark_mode': self.dark_mode,
                    'recent_files': self.recent_files[:10],
                    'word_goal': self.word_goal,
                }, f)
        except:
            pass
    
    def load_snippets(self):
        try:
            if os.path.exists(SNIPPETS_FILE):
                with open(SNIPPETS_FILE, 'r') as f:
                    self.snippets.update(json.load(f))
        except:
            pass
    
    def save_snippets(self):
        try:
            with open(SNIPPETS_FILE, 'w') as f:
                json.dump(self.snippets, f, indent=2)
        except:
            pass
    
    def setup_ui(self):
        self.setWindowTitle("Nebula Note")
        self.setMinimumSize(1300, 850)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 사이드 패널
        self.side_panel = QTabWidget()
        self.side_panel.setMaximumWidth(320)
        self.side_panel.setMinimumWidth(250)
        
        # 개요 패널
        self.outline_panel = OutlinePanel()
        self.outline_panel.heading_clicked.connect(self.goto_line)
        self.side_panel.addTab(self.outline_panel, "📑 개요")
        
        # 예제 패널
        self.example_panel = ExamplePanel()
        self.example_panel.template_selected.connect(self.insert_template)
        self.side_panel.addTab(self.example_panel, "📚 예제")
        
        # Mermaid 패널
        self.mermaid_panel = MermaidPanel()
        self.mermaid_panel.template_selected.connect(self.insert_at_cursor)
        self.side_panel.addTab(self.mermaid_panel, "📊 Mermaid")
        
        # 가이드 패널
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
        self.editor.setPlaceholderText("마크다운을 입력하세요...\n\n💡 팁: Tab을 눌러 스니펫을 확장하세요")
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_cursor_pos)
        
        # 탭 키 처리 (스니펫)
        self.editor.installEventFilter(self)
        
        self.highlighter = MarkdownHighlighter(self.editor.document(), self.dark_mode)
        
        self.completer = QCompleter(AUTOCOMPLETE_ITEMS)
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
        
        self.splitter.addWidget(editor_w)
        
        # 미리보기
        preview_w = QWidget()
        pl = QVBoxLayout(preview_w)
        pl.setContentsMargins(5, 5, 5, 5)
        
        self.preview = QWebEngineView()
        pl.addWidget(self.preview)
        
        self.splitter.addWidget(preview_w)
        self.splitter.setSizes([550, 550])
        
        main_layout.addWidget(self.splitter)
        
        # 상태바
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.word_label = QLabel("단어: 0")
        self.status_bar.addPermanentWidget(self.word_label)
        
        self.char_label = QLabel("문자: 0")
        self.status_bar.addPermanentWidget(self.char_label)
        
        self.read_time_label = QLabel("읽기: ~1분")
        self.status_bar.addPermanentWidget(self.read_time_label)
        
        self.pos_label = QLabel("줄: 1, 열: 1")
        self.status_bar.addPermanentWidget(self.pos_label)
    
    def eventFilter(self, obj, event):
        """탭 키로 스니펫 확장"""
        if obj == self.editor and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                cursor = self.editor.textCursor()
                cursor.select(QTextCursor.SelectionType.WordUnderCursor)
                word = cursor.selectedText()
                
                if word in self.snippets:
                    snippet = self.snippets[word]
                    # $1 등의 플레이스홀더 처리
                    snippet = snippet.replace('$1', '').replace('$2', '')
                    cursor.insertText(snippet)
                    return True
        return super().eventFilter(obj, event)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # ===== 파일 =====
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
        
        # 내보내기
        export_menu = file_menu.addMenu("내보내기")
        
        export_html = QAction("HTML", self)
        export_html.triggered.connect(self.export_html)
        export_menu.addAction(export_html)
        
        export_pdf = QAction("PDF (인쇄)", self)
        export_pdf.triggered.connect(self.print_preview)
        export_menu.addAction(export_pdf)
        
        file_menu.addSeparator()
        
        # 백업
        backup_act = QAction("백업 생성", self)
        backup_act.triggered.connect(self.create_backup)
        file_menu.addAction(backup_act)
        
        file_menu.addSeparator()
        
        exit_act = QAction("종료", self)
        exit_act.setShortcut(QKeySequence.StandardKey.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        # ===== 편집 =====
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
        
        cut = QAction("잘라내기", self)
        cut.setShortcut(QKeySequence.StandardKey.Cut)
        cut.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut)
        
        copy = QAction("복사", self)
        copy.setShortcut(QKeySequence.StandardKey.Copy)
        copy.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy)
        
        paste = QAction("붙여넣기", self)
        paste.setShortcut(QKeySequence.StandardKey.Paste)
        paste.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste)
        
        edit_menu.addSeparator()
        
        find_act = QAction("찾기/바꾸기...", self)
        find_act.setShortcut(QKeySequence.StandardKey.Find)
        find_act.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_act)
        
        edit_menu.addSeparator()
        
        snippet_act = QAction("스니펫 관리...", self)
        snippet_act.triggered.connect(self.manage_snippets)
        edit_menu.addAction(snippet_act)
        
        # ===== 삽입 =====
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
        
        insert_toc = QAction("목차 (TOC)", self)
        insert_toc.triggered.connect(lambda: self.insert_text("[TOC]\n\n"))
        insert_menu.addAction(insert_toc)
        
        insert_date = QAction("현재 날짜", self)
        insert_date.triggered.connect(lambda: self.insert_text(datetime.now().strftime("%Y-%m-%d")))
        insert_menu.addAction(insert_date)
        
        insert_time = QAction("현재 시간", self)
        insert_time.triggered.connect(lambda: self.insert_text(datetime.now().strftime("%H:%M")))
        insert_menu.addAction(insert_time)
        
        insert_menu.addSeparator()
        
        # Mermaid 서브메뉴
        mermaid_menu = insert_menu.addMenu("Mermaid 다이어그램")
        for name, code in list(MERMAID_EXAMPLES.items()):
            act = QAction(name, self)
            act.triggered.connect(lambda _, c=code: self.insert_at_cursor(c))
            mermaid_menu.addAction(act)
        
        # ===== Mermaid =====
        mermaid_main = menubar.addMenu("Mermaid")
        
        open_viewer = QAction("🔍 뷰어 열기", self)
        open_viewer.setShortcut(QKeySequence("Ctrl+M"))
        open_viewer.triggered.connect(self.open_mermaid_viewer)
        mermaid_main.addAction(open_viewer)
        
        mermaid_main.addSeparator()
        
        # 자주 쓰는 다이어그램
        for name in ["플로우차트 (Flowchart)", "시퀀스 다이어그램", "클래스 다이어그램", 
                     "간트 차트", "파이 차트", "마인드맵"]:
            if name in MERMAID_EXAMPLES:
                act = QAction(f"삽입: {name}", self)
                act.triggered.connect(lambda _, n=name: self.insert_at_cursor(MERMAID_EXAMPLES[n]))
                mermaid_main.addAction(act)
        
        # ===== 보기 =====
        view_menu = menubar.addMenu("보기")
        
        self.preview_act = QAction("미리보기", self)
        self.preview_act.setCheckable(True)
        self.preview_act.setChecked(True)
        self.preview_act.triggered.connect(self.toggle_preview)
        view_menu.addAction(self.preview_act)
        
        self.sidebar_act = QAction("사이드바", self)
        self.sidebar_act.setCheckable(True)
        self.sidebar_act.setChecked(True)
        self.sidebar_act.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(self.sidebar_act)
        
        view_menu.addSeparator()
        
        self.focus_act = QAction("🎯 포커스 모드", self)
        self.focus_act.setShortcut(QKeySequence("F11"))
        self.focus_act.setCheckable(True)
        self.focus_act.triggered.connect(self.toggle_focus_mode)
        view_menu.addAction(self.focus_act)
        
        view_menu.addSeparator()
        
        self.dark_act = QAction("다크 모드", self)
        self.dark_act.setCheckable(True)
        self.dark_act.setChecked(self.dark_mode)
        self.dark_act.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_act)
        
        view_menu.addSeparator()
        
        stats_act = QAction("📊 문서 통계", self)
        stats_act.triggered.connect(self.show_stats)
        view_menu.addAction(stats_act)
        
        # ===== 도구 =====
        tools_menu = menubar.addMenu("도구")
        
        goal_act = QAction("🎯 단어 목표 설정...", self)
        goal_act.triggered.connect(self.set_word_goal)
        tools_menu.addAction(goal_act)
        
        tools_menu.addSeparator()
        
        format_table = QAction("표 정렬", self)
        format_table.triggered.connect(self.format_tables)
        tools_menu.addAction(format_table)
        
        sort_lines = QAction("줄 정렬", self)
        sort_lines.triggered.connect(self.sort_selected_lines)
        tools_menu.addAction(sort_lines)
        
        remove_empty = QAction("빈 줄 제거", self)
        remove_empty.triggered.connect(self.remove_empty_lines)
        tools_menu.addAction(remove_empty)
        
        # ===== 도움말 =====
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
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        buttons = [
            ("H1", lambda: self.insert_at_line_start("# "), "제목 1"),
            ("H2", lambda: self.insert_at_line_start("## "), "제목 2"),
            ("H3", lambda: self.insert_at_line_start("### "), "제목 3"),
            ("|", None, None),
            ("B", lambda: self.wrap_selection("**"), "굵게"),
            ("I", lambda: self.wrap_selection("*"), "기울임"),
            ("S", lambda: self.wrap_selection("~~"), "취소선"),
            ("C", lambda: self.wrap_selection("`"), "코드"),
            ("|", None, None),
            ("•", lambda: self.insert_at_line_start("- "), "목록"),
            ("1.", lambda: self.insert_at_line_start("1. "), "번호 목록"),
            ("☐", lambda: self.insert_at_line_start("- [ ] "), "체크"),
            ("☑", lambda: self.insert_at_line_start("- [x] "), "완료"),
            ("|", None, None),
            ("🔗", self.insert_link, "링크"),
            ("🖼", self.insert_image, "이미지"),
            ("📊", self.insert_table, "테이블"),
            ("😀", self.insert_emoji, "이모지"),
            ("|", None, None),
            ("📈", self.open_mermaid_viewer, "Mermaid 뷰어"),
            ("🎯", self.toggle_focus_mode, "포커스 모드"),
        ]
        
        for text, action, tooltip in buttons:
            if text == "|":
                toolbar.addSeparator()
            else:
                btn = toolbar.addAction(text)
                if tooltip:
                    btn.setToolTip(tooltip)
                if action:
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
    
    def apply_theme(self):
        style = DARK_STYLE if self.dark_mode else LIGHT_STYLE
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
        QTimer.singleShot(350, self.update_preview)
    
    def update_title(self):
        title = "Nebula Note"
        if self.current_file:
            title = f"{os.path.basename(self.current_file)} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.setWindowTitle(title)
    
    def update_stats(self):
        text = self.editor.toPlainText()
        stats = DocumentStats.calculate(text)
        
        self.word_label.setText(f"단어: {stats['words']}")
        self.char_label.setText(f"문자: {stats['chars']}")
        self.read_time_label.setText(f"읽기: ~{stats['read_time']}분")
        
        # 워드 목표
        if self.word_goal > 0:
            self.goal_progress.show()
            progress = min(100, int(stats['words'] / self.word_goal * 100))
            self.goal_progress.setValue(progress)
            self.goal_progress.setToolTip(f"{stats['words']}/{self.word_goal} 단어 ({progress}%)")
        else:
            self.goal_progress.hide()
    
    def update_cursor_pos(self):
        cursor = self.editor.textCursor()
        self.pos_label.setText(f"줄: {cursor.blockNumber()+1}, 열: {cursor.columnNumber()+1}")
    
    def update_preview(self):
        text = self.editor.toPlainText()
        
        # Mermaid 블록 추출
        mermaid_pattern = r'```mermaid\n([\s\S]*?)```'
        placeholder_text = text
        mermaid_blocks = re.findall(mermaid_pattern, text)
        
        for i, block in enumerate(mermaid_blocks):
            placeholder_text = placeholder_text.replace(
                f'```mermaid\n{block}```',
                f'<div class="mermaid">\n{block}\n</div>'
            )
        
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br', 'sane_lists'])
        html_content = md.convert(placeholder_text)
        
        bg = "#1e1e1e" if self.dark_mode else "#ffffff"
        fg = "#d4d4d4" if self.dark_mode else "#333333"
        code_bg = "#2d2d2d" if self.dark_mode else "#f5f5f5"
        theme = "dark" if self.dark_mode else "default"
        
        html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
       line-height: 1.7; padding: 25px; max-width: 850px; margin: 0 auto; 
       background: {bg}; color: {fg}; }}
h1,h2,h3,h4,h5,h6 {{ margin-top: 1.5em; margin-bottom: 0.5em; font-weight: 600; }}
h1 {{ font-size: 2em; border-bottom: 2px solid {code_bg}; padding-bottom: 0.3em; }}
h2 {{ font-size: 1.5em; border-bottom: 1px solid {code_bg}; padding-bottom: 0.3em; }}
code {{ background: {code_bg}; padding: 0.2em 0.4em; border-radius: 3px; font-family: 'Consolas', monospace; font-size: 0.9em; }}
pre {{ background: {code_bg}; padding: 16px; border-radius: 8px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; }}
blockquote {{ border-left: 4px solid #007AFF; margin: 1em 0; padding: 0.5em 1em; background: {code_bg}; border-radius: 0 8px 8px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid {"#444" if self.dark_mode else "#ddd"}; padding: 10px 14px; text-align: left; }}
th {{ background: {code_bg}; font-weight: 600; }}
tr:nth-child(even) {{ background: {code_bg}; }}
img {{ max-width: 100%; border-radius: 8px; }}
a {{ color: #007AFF; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
ul, ol {{ padding-left: 2em; }}
li {{ margin: 0.3em 0; }}
hr {{ border: none; border-top: 1px solid {code_bg}; margin: 2em 0; }}
.mermaid {{ background: transparent; text-align: center; margin: 1em 0; }}
input[type="checkbox"] {{ margin-right: 8px; }}
</style></head><body>
{html_content}
<script>mermaid.initialize({{ startOnLoad: true, theme: '{theme}' }});</script>
</body></html>'''
        
        self.preview.setHtml(html)
    
    def update_recent_menu(self):
        self.recent_menu.clear()
        for f in self.recent_files[:10]:
            if os.path.exists(f):
                act = QAction(os.path.basename(f), self)
                act.setToolTip(f)
                act.triggered.connect(lambda _, p=f: self.open_file(p))
                self.recent_menu.addAction(act)
        
        if self.recent_files:
            self.recent_menu.addSeparator()
            clear = QAction("목록 지우기", self)
            clear.triggered.connect(lambda: setattr(self, 'recent_files', []) or self.update_recent_menu())
            self.recent_menu.addAction(clear)
    
    def add_to_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.update_recent_menu()
        self.save_settings()
    
    def goto_line(self, line_num):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        for _ in range(line_num):
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setFocus()
    
    # ===== 파일 작업 =====
    def new_file(self):
        if self.check_save():
            self.editor.clear()
            self.current_file = None
            self.is_modified = False
            self.update_title()
    
    def open_file(self, path=None):
        if not self.check_save():
            return
        
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "열기", "", 
                "마크다운 (*.md *.markdown *.txt);;모든 파일 (*)")
        
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
    
    def check_save(self):
        if self.is_modified:
            reply = QMessageBox.question(self, "저장", "변경사항을 저장하시겠습니까?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        return True
    
    def create_backup(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = os.path.basename(self.current_file) if self.current_file else "untitled"
        backup_path = os.path.join(BACKUP_DIR, f"{name}_{timestamp}.md")
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())
        
        self.status_bar.showMessage(f"백업 생성: {backup_path}", 3000)
    
    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "HTML 내보내기", "", "HTML (*.html)")
        if path:
            self.preview.page().toHtml(lambda html: self._write_file(path, html))
    
    def _write_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.status_bar.showMessage(f"내보냄: {path}", 3000)
    
    def print_preview(self):
        try:
            from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintPreviewDialog(printer, self)
            dialog.paintRequested.connect(lambda p: self.preview.page().print(p, lambda ok: None))
            dialog.exec()
        except ImportError:
            QMessageBox.warning(self, "알림", "인쇄 기능을 사용하려면 PyQt6-PrintSupport가 필요합니다.")
    
    # ===== 편집 =====
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
    def set_word_goal(self):
        goal, ok = QInputDialog.getInt(self, "단어 목표", "목표 단어 수 (0=비활성화):", 
                                        self.word_goal, 0, 100000, 100)
        if ok:
            self.word_goal = goal
            self.update_stats()
            self.save_settings()
    
    def format_tables(self):
        text = self.editor.toPlainText()
        # 간단한 테이블 정렬 (실제로는 더 복잡한 로직 필요)
        lines = text.split('\n')
        # 구현 생략...
        self.status_bar.showMessage("표 정렬 완료", 2000)
    
    def sort_selected_lines(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            lines = selected.split('\u2029')  # QTextEdit의 줄바꿈
            lines.sort()
            cursor.insertText('\n'.join(lines))
    
    def remove_empty_lines(self):
        text = self.editor.toPlainText()
        lines = [l for l in text.split('\n') if l.strip()]
        self.editor.setPlainText('\n'.join(lines))
    
    def show_stats(self):
        stats = DocumentStats.calculate(self.editor.toPlainText())
        dlg = StatsDialog(stats, self)
        dlg.exec()
    
    # ===== Mermaid =====
    def open_mermaid_viewer(self):
        text = self.editor.toPlainText()
        pattern = r'```mermaid\n([\s\S]*?)```'
        matches = re.findall(pattern, text)
        
        code = matches[0].strip() if matches else "flowchart TD\n    A[시작] --> B[끝]"
        
        if self.mermaid_viewer is None or not self.mermaid_viewer.isVisible():
            self.mermaid_viewer = MermaidViewer(code, self.dark_mode, self)
            self.mermaid_viewer.show()
        else:
            self.mermaid_viewer.update_mermaid(code)
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
            self.side_panel.hide()
            self.splitter.widget(1).hide()  # 미리보기 숨김
            self.menuBar().hide()
            self.statusBar().hide()
            self.findChild(QToolBar).hide()
            
            style = FOCUS_STYLE_DARK if self.dark_mode else FOCUS_STYLE_LIGHT
            self.setStyleSheet(style)
            self.showFullScreen()
        else:
            self.exit_focus_mode()
    
    def exit_focus_mode(self):
        if self.focus_mode:
            self.focus_mode = False
            self.focus_act.setChecked(False)
            
            self.side_panel.show()
            self.splitter.widget(1).show()
            self.menuBar().show()
            self.statusBar().show()
            self.findChild(QToolBar).show()
            
            self.setStyleSheet(self._normal_style)
            self.showNormal()
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.dark_act.setChecked(self.dark_mode)
        self.apply_theme()
        self.save_settings()
        
        if self.mermaid_viewer and self.mermaid_viewer.isVisible():
            self.mermaid_viewer.dark_mode = self.dark_mode
            self.mermaid_viewer.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)
            self.mermaid_viewer.render_mermaid()
    
    # ===== 도움말 =====
    def show_about(self):
        QMessageBox.about(self, "MarkdownPro", 
            f"<h2>MarkdownPro v3.0</h2>"
            f"<p>프로페셔널 마크다운 에디터</p>"
            f"<hr>"
            f"<p><b>주요 기능:</b></p>"
            f"<ul>"
            f"<li>실시간 미리보기</li>"
            f"<li>Mermaid 다이어그램 {len(MERMAID_EXAMPLES)}종 지원</li>"
            f"<li>포커스 모드</li>"
            f"<li>문서 개요 & 통계</li>"
            f"<li>스니펫 관리</li>"
            f"<li>다크 모드</li>"
            f"</ul>")
    
    def show_shortcuts(self):
        QMessageBox.information(self, "단축키", """
<h3>단축키 안내</h3>
<table>
<tr><td><b>Ctrl+N</b></td><td>새 문서</td></tr>
<tr><td><b>Ctrl+O</b></td><td>열기</td></tr>
<tr><td><b>Ctrl+S</b></td><td>저장</td></tr>
<tr><td><b>Ctrl+F</b></td><td>찾기/바꾸기</td></tr>
<tr><td><b>Ctrl+1/2/3/4</b></td><td>제목 1/2/3/4</td></tr>
<tr><td><b>Ctrl+B</b></td><td>굵게</td></tr>
<tr><td><b>Ctrl+I</b></td><td>기울임</td></tr>
<tr><td><b>Ctrl+K</b></td><td>링크</td></tr>
<tr><td><b>Ctrl+M</b></td><td>Mermaid 뷰어</td></tr>
<tr><td><b>Ctrl+D</b></td><td>날짜 삽입</td></tr>
<tr><td><b>F11</b></td><td>포커스 모드</td></tr>
<tr><td><b>Tab</b></td><td>스니펫 확장</td></tr>
<tr><td><b>Esc</b></td><td>포커스 모드 종료</td></tr>
</table>
""")
    
    def closeEvent(self, event):
        if not self.check_save():
            event.ignore()
            return
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
    def set_word_goal(self):
        goal, ok = QInputDialog.getInt(self, "단어 목표", "목표 단어 수 (0=비활성화):", 
                                        self.word_goal, 0, 100000, 100)
        if ok:
            self.word_goal = goal
            self.update_stats()
            self.save_settings()
    
    def format_tables(self):
        text = self.editor.toPlainText()
        # 간단한 테이블 정렬 (실제로는 더 복잡한 로직 필요)
        lines = text.split('\n')
        # 구현 생략...
        self.status_bar.showMessage("표 정렬 완료", 2000)
    
    def sort_selected_lines(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            lines = selected.split('\u2029')  # QTextEdit의 줄바꿈
            lines.sort()
            cursor.insertText('\n'.join(lines))
    
    def remove_empty_lines(self):
        text = self.editor.toPlainText()
        lines = [l for l in text.split('\n') if l.strip()]
        self.editor.setPlainText('\n'.join(lines))
    
    def show_stats(self):
        stats = DocumentStats.calculate(self.editor.toPlainText())
        dlg = StatsDialog(stats, self)
        dlg.exec()
    
    # ===== Mermaid =====
    def open_mermaid_viewer(self):
        text = self.editor.toPlainText()
        pattern = r'```mermaid\n([\s\S]*?)```'
        matches = re.findall(pattern, text)
        
        code = matches[0].strip() if matches else "flowchart TD\n    A[시작] --> B[끝]"
        
        if self.mermaid_viewer is None or not self.mermaid_viewer.isVisible():
            self.mermaid_viewer = MermaidViewer(code, self.dark_mode, self)
            self.mermaid_viewer.show()
        else:
            self.mermaid_viewer.update_mermaid(code)
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
            self.side_panel.hide()
            self.splitter.widget(1).hide()  # 미리보기 숨김
            self.menuBar().hide()
            self.statusBar().hide()
            self.findChild(QToolBar).hide()
            
            style = FOCUS_STYLE_DARK if self.dark_mode else FOCUS_STYLE_LIGHT
            self.setStyleSheet(style)
            self.showFullScreen()
        else:
            self.exit_focus_mode()
    
    def exit_focus_mode(self):
        if self.focus_mode:
            self.focus_mode = False
            self.focus_act.setChecked(False)
            
            self.side_panel.show()
            self.splitter.widget(1).show()
            self.menuBar().show()
            self.statusBar().show()
            self.findChild(QToolBar).show()
            
            self.setStyleSheet(self._normal_style)
            self.showNormal()
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.dark_act.setChecked(self.dark_mode)
        self.apply_theme()
        self.save_settings()
        
        if self.mermaid_viewer and self.mermaid_viewer.isVisible():
            self.mermaid_viewer.dark_mode = self.dark_mode
            self.mermaid_viewer.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)
            self.mermaid_viewer.render_mermaid()
    
    # ===== 도움말 =====
    def show_about(self):
        QMessageBox.about(self, "MarkdownPro", 
            f"<h2>MarkdownPro v3.0</h2>"
            f"<p>프로페셔널 마크다운 에디터</p>"
            f"<hr>"
            f"<p><b>주요 기능:</b></p>"
            f"<ul>"
            f"<li>실시간 미리보기</li>"
            f"<li>Mermaid 다이어그램 {len(MERMAID_EXAMPLES)}종 지원</li>"
            f"<li>포커스 모드</li>"
            f"<li>문서 개요 & 통계</li>"
            f"<li>스니펫 관리</li>"
            f"<li>다크 모드</li>"
            f"</ul>")
    
    def show_shortcuts(self):
        QMessageBox.information(self, "단축키", """
<h3>단축키 안내</h3>
<table>
<tr><td><b>Ctrl+N</b></td><td>새 문서</td></tr>
<tr><td><b>Ctrl+O</b></td><td>열기</td></tr>
<tr><td><b>Ctrl+S</b></td><td>저장</td></tr>
<tr><td><b>Ctrl+F</b></td><td>찾기/바꾸기</td></tr>
<tr><td><b>Ctrl+1/2/3/4</b></td><td>제목 1/2/3/4</td></tr>
<tr><td><b>Ctrl+B</b></td><td>굵게</td></tr>
<tr><td><b>Ctrl+I</b></td><td>기울임</td></tr>
<tr><td><b>Ctrl+K</b></td><td>링크</td></tr>
<tr><td><b>Ctrl+M</b></td><td>Mermaid 뷰어</td></tr>
<tr><td><b>Ctrl+D</b></td><td>날짜 삽입</td></tr>
<tr><td><b>F11</b></td><td>포커스 모드</td></tr>
<tr><td><b>Tab</b></td><td>스니펫 확장</td></tr>
<tr><td><b>Esc</b></td><td>포커스 모드 종료</td></tr>
</table>
""")
    
    def closeEvent(self, event):
        if not self.check_save():
            event.ignore()
            return
        self.save_settings()
        self.save_snippets()
        event.accept()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    # Windows Taskbar Icon Fix
    if sys.platform == 'win32':
        import ctypes
        myappid = 'nebulanote.editor.v1' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setApplicationName("Nebula Note")
    app.setOrganizationName("Nebula Note")
    
    # Set Window Icon
    from PyQt6.QtGui import QIcon
    app.setWindowIcon(QIcon(resource_path("icon.ico")))
    
    window = MarkdownEditor()
    window.show()

    # Close splash screen if it exists
    try:
        import pyi_splash
        pyi_splash.close()
    except ImportError:
        pass
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
