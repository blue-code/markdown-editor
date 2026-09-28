"""Localized sample content: Mermaid examples, document templates, snippets and autocomplete.

Every public function takes a language code from i18n.SUPPORTED_LANGUAGES and falls back to English.
"""

from datetime import datetime

from i18n import DEFAULT_LANGUAGE


def _pick(values, lang):
    """Return values[lang] for dicts, or values itself for language-neutral content."""
    if isinstance(values, dict):
        return values.get(lang) or values[DEFAULT_LANGUAGE]
    return values


# ============== Mermaid examples ==============

_FLOWCHART = {
    "ko": """```mermaid
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
    "en": """```mermaid
flowchart TD
    A[Start] --> B{Check condition}
    B -->|Yes| C[Process 1]
    B -->|No| D[Process 2]
    C --> E[Result]
    D --> E
    E --> F((End))

    subgraph Subprocess
    G[Step 1] --> H[Step 2]
    end
```""",
    "ja": """```mermaid
flowchart TD
    A[開始] --> B{条件を確認}
    B -->|Yes| C[処理 1]
    B -->|No| D[処理 2]
    C --> E[結果]
    D --> E
    E --> F((終了))

    subgraph サブプロセス
    G[ステップ1] --> H[ステップ2]
    end
```""",
    "zh": """```mermaid
flowchart TD
    A[开始] --> B{检查条件}
    B -->|Yes| C[处理 1]
    B -->|No| D[处理 2]
    C --> E[结果]
    D --> E
    E --> F((结束))

    subgraph 子流程
    G[步骤1] --> H[步骤2]
    end
```""",
}

_FLOWCHART_LR = {
    "ko": """```mermaid
flowchart LR
    A[입력] --> B[처리]
    B --> C{검증}
    C -->|성공| D[출력]
    C -->|실패| E[에러]
    E --> A
```""",
    "en": """```mermaid
flowchart LR
    A[Input] --> B[Process]
    B --> C{Validate}
    C -->|Pass| D[Output]
    C -->|Fail| E[Error]
    E --> A
```""",
    "ja": """```mermaid
flowchart LR
    A[入力] --> B[処理]
    B --> C{検証}
    C -->|成功| D[出力]
    C -->|失敗| E[エラー]
    E --> A
```""",
    "zh": """```mermaid
flowchart LR
    A[输入] --> B[处理]
    B --> C{校验}
    C -->|成功| D[输出]
    C -->|失败| E[错误]
    E --> A
```""",
}

_SEQUENCE = {
    "ko": """```mermaid
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
    "en": """```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant F as 🖥️ Frontend
    participant A as ⚙️ API Server
    participant D as 🗄️ DB

    U->>F: Log in
    activate F
    F->>A: POST /auth/login
    activate A
    A->>D: Find user
    activate D
    D-->>A: User record
    deactivate D
    A-->>F: JWT token
    deactivate A
    F-->>U: Logged in
    deactivate F

    Note over U,D: Authentication complete
```""",
    "ja": """```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 ユーザー
    participant F as 🖥️ フロントエンド
    participant A as ⚙️ APIサーバー
    participant D as 🗄️ DB

    U->>F: ログイン要求
    activate F
    F->>A: POST /auth/login
    activate A
    A->>D: ユーザー検索
    activate D
    D-->>A: ユーザー情報
    deactivate D
    A-->>F: JWT トークン
    deactivate A
    F-->>U: ログイン成功
    deactivate F

    Note over U,D: 認証完了
```""",
    "zh": """```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 用户
    participant F as 🖥️ 前端
    participant A as ⚙️ API服务器
    participant D as 🗄️ 数据库

    U->>F: 登录请求
    activate F
    F->>A: POST /auth/login
    activate A
    A->>D: 查询用户
    activate D
    D-->>A: 用户信息
    deactivate D
    A-->>F: JWT 令牌
    deactivate A
    F-->>U: 登录成功
    deactivate F

    Note over U,D: 认证完成
```""",
}

_CLASS = """```mermaid
---
title: Animal example
---
classDiagram
    note "From Duck till Zebra"
    Animal <|-- Duck
    note for Duck "can fly\\ncan swim\\ncan dive\\ncan help in debugging"
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
    class Zebra{
        +bool is_wild
        +run()
    }

```"""

_STATE = {
    "ko": """```mermaid
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
    "en": """```mermaid
stateDiagram-v2
    [*] --> Idle: start

    Idle --> Processing: request received
    Processing --> Validating: processed

    state Validating {
        [*] --> DataCheck
        DataCheck --> PermissionCheck
        PermissionCheck --> [*]
    }

    Validating --> Done: valid
    Validating --> Failed: invalid

    Done --> [*]
    Failed --> Idle: retry
    Failed --> [*]: give up

    note right of Processing: async processing
```""",
    "ja": """```mermaid
stateDiagram-v2
    [*] --> 待機: 開始

    待機 --> 処理中: リクエスト受信
    処理中 --> 検証中: 処理完了

    state 検証中 {
        [*] --> データ検証
        データ検証 --> 権限検証
        権限検証 --> [*]
    }

    検証中 --> 完了: 検証成功
    検証中 --> 失敗: 検証失敗

    完了 --> [*]
    失敗 --> 待機: 再試行
    失敗 --> [*]: 中止

    note right of 処理中: 非同期処理
```""",
    "zh": """```mermaid
stateDiagram-v2
    [*] --> 等待: 开始

    等待 --> 处理中: 收到请求
    处理中 --> 校验中: 处理完成

    state 校验中 {
        [*] --> 数据校验
        数据校验 --> 权限校验
        权限校验 --> [*]
    }

    校验中 --> 完成: 校验成功
    校验中 --> 失败: 校验失败

    完成 --> [*]
    失败 --> 等待: 重试
    失败 --> [*]: 放弃

    note right of 处理中: 异步处理
```""",
}

_ER = """```mermaid
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
```"""

_GANTT = {
    "ko": """```mermaid
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
    "en": """```mermaid
gantt
    title Project Schedule
    dateFormat YYYY-MM-DD

    section 📋 Planning
    Requirements      :done, req, 2024-01-01, 7d
    UI design         :done, design, after req, 5d
    DB design         :done, db, after req, 5d

    section 💻 Development
    Backend API       :active, backend, after design, 14d
    Frontend          :frontend, after design, 14d
    Database setup    :database, after db, 7d

    section 🧪 Testing
    Unit tests        :unittest, after backend, 5d
    Integration tests :inttest, after unittest, 5d
    QA                :qa, after inttest, 7d

    section 🚀 Release
    Staging deploy    :staging, after qa, 2d
    Production deploy :crit, prod, after staging, 1d
```""",
    "ja": """```mermaid
gantt
    title プロジェクト開発スケジュール
    dateFormat YYYY-MM-DD

    section 📋 企画
    要件分析          :done, req, 2024-01-01, 7d
    画面設計          :done, design, after req, 5d
    DB 設計           :done, db, after req, 5d

    section 💻 開発
    バックエンド API  :active, backend, after design, 14d
    フロントエンド    :frontend, after design, 14d
    DB 構築           :database, after db, 7d

    section 🧪 テスト
    単体テスト        :unittest, after backend, 5d
    結合テスト        :inttest, after unittest, 5d
    QA テスト         :qa, after inttest, 7d

    section 🚀 リリース
    ステージング      :staging, after qa, 2d
    本番リリース      :crit, prod, after staging, 1d
```""",
    "zh": """```mermaid
gantt
    title 项目开发计划
    dateFormat YYYY-MM-DD

    section 📋 规划
    需求分析          :done, req, 2024-01-01, 7d
    界面设计          :done, design, after req, 5d
    数据库设计        :done, db, after req, 5d

    section 💻 开发
    后端 API          :active, backend, after design, 14d
    前端              :frontend, after design, 14d
    数据库搭建        :database, after db, 7d

    section 🧪 测试
    单元测试          :unittest, after backend, 5d
    集成测试          :inttest, after unittest, 5d
    QA 测试           :qa, after inttest, 7d

    section 🚀 发布
    预发布部署        :staging, after qa, 2d
    生产部署          :crit, prod, after staging, 1d
```""",
}

_PIE = {
    "ko": """```mermaid
pie showData
    title 2024년 브라우저 시장 점유율
    "Chrome" : 65.7
    "Safari" : 18.5
    "Firefox" : 6.3
    "Edge" : 5.2
    "기타" : 4.3
```""",
    "en": """```mermaid
pie showData
    title Browser Market Share 2024
    "Chrome" : 65.7
    "Safari" : 18.5
    "Firefox" : 6.3
    "Edge" : 5.2
    "Other" : 4.3
```""",
    "ja": """```mermaid
pie showData
    title 2024年 ブラウザシェア
    "Chrome" : 65.7
    "Safari" : 18.5
    "Firefox" : 6.3
    "Edge" : 5.2
    "その他" : 4.3
```""",
    "zh": """```mermaid
pie showData
    title 2024年 浏览器市场份额
    "Chrome" : 65.7
    "Safari" : 18.5
    "Firefox" : 6.3
    "Edge" : 5.2
    "其他" : 4.3
```""",
}

_MINDMAP = {
    "ko": """```mermaid
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
    "en": """```mermaid
mindmap
  root((Project))
    📋 Planning
      Requirements
      User research
      Competitor analysis
    💻 Development
      Frontend
        React
        TypeScript
        Tailwind
      Backend
        Node.js
        PostgreSQL
        Redis
    🎨 Design
      UI/UX
      Prototype
      Design system
    🧪 Quality
      Testing
      Code review
      CI/CD
```""",
    "ja": """```mermaid
mindmap
  root((プロジェクト))
    📋 企画
      要件分析
      ユーザー調査
      競合分析
    💻 開発
      フロントエンド
        React
        TypeScript
        Tailwind
      バックエンド
        Node.js
        PostgreSQL
        Redis
    🎨 デザイン
      UI/UX
      プロトタイプ
      デザインシステム
    🧪 品質
      テスト
      コードレビュー
      CI/CD
```""",
    "zh": """```mermaid
mindmap
  root((项目))
    📋 规划
      需求分析
      用户调研
      竞品分析
    💻 开发
      前端
        React
        TypeScript
        Tailwind
      后端
        Node.js
        PostgreSQL
        Redis
    🎨 设计
      UI/UX
      原型
      设计系统
    🧪 质量
      测试
      代码评审
      CI/CD
```""",
}

_GIT = """```mermaid
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
```"""

_JOURNEY = {
    "ko": """```mermaid
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
    "en": """```mermaid
journey
    title Online Shopping Journey
    section Browse
      Visit home page: 5: Customer
      Search products: 4: Customer
      View product details: 5: Customer
    section Purchase
      Add to cart: 4: Customer
      Checkout page: 3: Customer
      Payment complete: 5: Customer
    section Delivery
      Track shipment: 4: Customer
      Receive package: 5: Customer
      Write a review: 3: Customer
```""",
    "ja": """```mermaid
journey
    title ネットショップの購入体験
    section 探す
      ホームページ訪問: 5: 顧客
      商品検索: 4: 顧客
      商品詳細を見る: 5: 顧客
    section 購入
      カートに追加: 4: 顧客
      決済ページ: 3: 顧客
      決済完了: 5: 顧客
    section 配送
      配送状況の確認: 4: 顧客
      商品の受け取り: 5: 顧客
      レビュー投稿: 3: 顧客
```""",
    "zh": """```mermaid
journey
    title 网购用户旅程
    section 浏览
      访问首页: 5: 顾客
      搜索商品: 4: 顾客
      查看商品详情: 5: 顾客
    section 购买
      加入购物车: 4: 顾客
      结算页面: 3: 顾客
      支付完成: 5: 顾客
    section 配送
      查看物流: 4: 顾客
      收到商品: 5: 顾客
      发表评价: 3: 顾客
```""",
}

_QUADRANT = """```mermaid
quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]

```"""

_REQUIREMENT = """```mermaid
requirementDiagram

    requirement test_req {
    id: 1
    text: the test text.
    risk: high
    verifymethod: test
    }

    element test_entity {
    type: simulation
    }

    test_entity - satisfies -> test_req
```"""

_TIMELINE = {
    "ko": """```mermaid
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
    "en": """```mermaid
timeline
    title Company History
    section 2020
        Jan : Company founded
        Jun : Seed funding
    section 2021
        Mar : Beta launch
        Sep : Series A
        Dec : 100K MAU
    section 2022
        Apr : Public launch
        Aug : Series B
        Nov : 1M MAU
    section 2023
        Feb : Global expansion
        Jul : IPO preparation
        Dec : $10M annual revenue
```""",
    "ja": """```mermaid
timeline
    title 会社沿革
    section 2020年
        1月 : 会社設立
        6月 : シード資金調達
    section 2021年
        3月 : ベータ版リリース
        9月 : シリーズA 調達
        12月 : MAU 10万人達成
    section 2022年
        4月 : 正式サービス開始
        8月 : シリーズB 調達
        11月 : MAU 100万人達成
    section 2023年
        2月 : 海外進出
        7月 : IPO 準備
        12月 : 年間売上 10億円達成
```""",
    "zh": """```mermaid
timeline
    title 公司发展历程
    section 2020年
        1月 : 公司成立
        6月 : 获得种子轮融资
    section 2021年
        3月 : 发布测试版
        9月 : A轮融资
        12月 : 月活跃用户达10万
    section 2022年
        4月 : 正式上线
        8月 : B轮融资
        11月 : 月活跃用户达100万
    section 2023年
        2月 : 拓展海外市场
        7月 : 筹备IPO
        12月 : 年营收突破1亿元
```""",
}

_SANKEY = """```mermaid
sankey-beta
Net Primary production %,Consumed energy %,85
Net Primary production %,Detritus %,15
Consumed energy %,Egested energy %,20%
Consumed energy %,Assimilated Energy %,65
Assimilated Energy %, Energy for Growth %, 25
Assimilated Energy %, Respired energy %, 40
Detritus %, Consumed by microbes %, 10
Detritus %, Stored in the earth %, 5
```"""

_XY = """```mermaid
xychart-beta
  title "Training progress"
  x-axis [mon, tues, wed, thur, fri, sat, sun]
  y-axis "Time trained (minutes)" 0 --> 300
  bar [60, 0, 120, 180, 230, 300, 0]
  line [60, 0, 120, 180, 230, 300, 0]
```"""

_BLOCK_TEMPLATE = """```mermaid
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
        Auth["{auth}"]
        User["{user}"]
        Product["{product}"]
    end

    space:3

    block:data:3
        columns 2
        PostgreSQL Redis
    end
```"""

_BLOCK_LABELS = {
    "ko": {"auth": "인증 서비스", "user": "사용자 서비스", "product": "상품 서비스"},
    "en": {"auth": "Auth Service", "user": "User Service", "product": "Product Service"},
    "ja": {"auth": "認証サービス", "user": "ユーザーサービス", "product": "商品サービス"},
    "zh": {"auth": "认证服务", "user": "用户服务", "product": "商品服务"},
}

_BLOCK = {
    lang: _BLOCK_TEMPLATE.replace("{auth}", labels["auth"])
    .replace("{user}", labels["user"])
    .replace("{product}", labels["product"])
    for lang, labels in _BLOCK_LABELS.items()
}

_C4 = {
    "ko": """```mermaid
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
    "en": """```mermaid
C4Context
    title System Context Diagram

    Person(customer, "Customer", "Shops on the platform")
    Person(admin, "Admin", "Staff who manage the system")

    System(ecommerce, "E-commerce System", "Online shopping platform")

    System_Ext(payment, "Payment System", "External payment gateway")
    System_Ext(delivery, "Delivery System", "Courier API")
    System_Ext(email, "Email Service", "Sends notifications")

    Rel(customer, ecommerce, "Browse / buy products")
    Rel(admin, ecommerce, "Manage products / orders")
    Rel(ecommerce, payment, "Process payments")
    Rel(ecommerce, delivery, "Request delivery")
    Rel(ecommerce, email, "Send notifications")
```""",
    "ja": """```mermaid
C4Context
    title システムコンテキスト図

    Person(customer, "顧客", "サービスを利用するユーザー")
    Person(admin, "管理者", "システムを管理する社員")

    System(ecommerce, "EC システム", "オンラインショッピング基盤")

    System_Ext(payment, "決済システム", "外部決済代行")
    System_Ext(delivery, "配送システム", "配送業者 API")
    System_Ext(email, "メールサービス", "通知の送信")

    Rel(customer, ecommerce, "商品検索/購入")
    Rel(admin, ecommerce, "商品/注文管理")
    Rel(ecommerce, payment, "決済処理")
    Rel(ecommerce, delivery, "配送依頼")
    Rel(ecommerce, email, "通知送信")
```""",
    "zh": """```mermaid
C4Context
    title 系统上下文图

    Person(customer, "顾客", "使用服务的用户")
    Person(admin, "管理员", "管理系统的员工")

    System(ecommerce, "电商系统", "在线购物平台")

    System_Ext(payment, "支付系统", "第三方支付")
    System_Ext(delivery, "物流系统", "快递公司 API")
    System_Ext(email, "邮件服务", "发送通知")

    Rel(customer, ecommerce, "搜索/购买商品")
    Rel(admin, ecommerce, "管理商品/订单")
    Rel(ecommerce, payment, "处理支付")
    Rel(ecommerce, delivery, "请求配送")
    Rel(ecommerce, email, "发送通知")
```""",
}

_KANBAN = """```mermaid
---
config:
  kanban:
    ticketBaseUrl: 'https://mermaidchart.atlassian.net/browse/#TICKET#'
---
kanban
  Todo
    [Create Documentation]
    docs[Create Blog about the new diagram]
  [In progress]
    id6[Create renderer so that it works in all cases. We also add some extra text here for testing purposes. And some more just for the extra flare.]
  id9[Ready for deploy]
    id8[Design grammar]@{ assigned: 'knsv' }
  id10[Ready for test]
    id4[Create parsing tests]@{ ticket: MC-2038, assigned: 'K.Sveidqvist', priority: 'High' }
    id66[last item]@{ priority: 'Very Low', assigned: 'knsv' }
  id11[Done]
    id5[define getData]
    id2[Title of diagram is more than 100 chars when user duplicates diagram with 100 char]@{ ticket: MC-2036, priority: 'Very High'}
    id3[Update DB function]@{ ticket: MC-2037, assigned: knsv, priority: 'High' }

  id12[Can't reproduce]
    id3[Weird flickering in Firefox]

```"""


# (id, names per language, code)
MERMAID_EXAMPLES = [
    ("flowchart", {"ko": "플로우차트 (Flowchart)", "en": "Flowchart", "ja": "フローチャート", "zh": "流程图"}, _FLOWCHART),
    ("flowchart_lr", {"ko": "플로우차트 (좌→우)", "en": "Flowchart (Left → Right)", "ja": "フローチャート (左→右)", "zh": "流程图 (从左到右)"}, _FLOWCHART_LR),
    ("sequence", {"ko": "시퀀스 다이어그램", "en": "Sequence Diagram", "ja": "シーケンス図", "zh": "时序图"}, _SEQUENCE),
    ("class", {"ko": "클래스 다이어그램", "en": "Class Diagram", "ja": "クラス図", "zh": "类图"}, _CLASS),
    ("state", {"ko": "상태 다이어그램", "en": "State Diagram", "ja": "状態遷移図", "zh": "状态图"}, _STATE),
    ("er", {"ko": "ER 다이어그램", "en": "ER Diagram", "ja": "ER 図", "zh": "ER 图"}, _ER),
    ("gantt", {"ko": "간트 차트", "en": "Gantt Chart", "ja": "ガントチャート", "zh": "甘特图"}, _GANTT),
    ("pie", {"ko": "파이 차트", "en": "Pie Chart", "ja": "円グラフ", "zh": "饼图"}, _PIE),
    ("mindmap", {"ko": "마인드맵", "en": "Mind Map", "ja": "マインドマップ", "zh": "思维导图"}, _MINDMAP),
    ("git", {"ko": "Git 그래프", "en": "Git Graph", "ja": "Git グラフ", "zh": "Git 图"}, _GIT),
    ("journey", {"ko": "사용자 여정", "en": "User Journey", "ja": "ユーザージャーニー", "zh": "用户旅程图"}, _JOURNEY),
    ("quadrant", {"ko": "사분면 차트", "en": "Quadrant Chart", "ja": "4象限チャート", "zh": "象限图"}, _QUADRANT),
    ("requirement", {"ko": "요구사항 다이어그램", "en": "Requirement Diagram", "ja": "要求図", "zh": "需求图"}, _REQUIREMENT),
    ("timeline", {"ko": "타임라인", "en": "Timeline", "ja": "タイムライン", "zh": "时间线"}, _TIMELINE),
    ("sankey", {"ko": "생키 다이어그램", "en": "Sankey Diagram", "ja": "サンキー図", "zh": "桑基图"}, _SANKEY),
    ("xy", {"ko": "XY 차트", "en": "XY Chart", "ja": "XY チャート", "zh": "XY 图表"}, _XY),
    ("block", {"ko": "블록 다이어그램", "en": "Block Diagram", "ja": "ブロック図", "zh": "框图"}, _BLOCK),
    ("c4", {"ko": "C4 컨텍스트", "en": "C4 Context", "ja": "C4 コンテキスト", "zh": "C4 上下文图"}, _C4),
    ("kanban", {"ko": "칸반", "en": "Kanban", "ja": "カンバン", "zh": "看板"}, _KANBAN),
]

# Shown directly in the Mermaid menu.
FEATURED_MERMAID_IDS = ("flowchart", "sequence", "class", "gantt", "pie", "mindmap")


def mermaid_examples(lang):
    """Return [(id, display_name, code), ...] in menu order."""
    return [(example_id, _pick(names, lang), _pick(code, lang)) for example_id, names, code in MERMAID_EXAMPLES]


# ============== Document templates ==============

def _basic_template(lang):
    return {
        "ko": """# 제목

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
        "en": """# Title

This is a basic Markdown document.

## Subtitle

Use **bold** or *italic* for emphasis.

### List
- Item 1
- Item 2
- Item 3

### Link
[Link text](https://example.com)
""",
        "ja": """# タイトル

これは基本的な Markdown 文書です。

## サブタイトル

**太字** や *斜体* で強調できます。

### リスト
- 項目 1
- 項目 2
- 項目 3

### リンク
[リンクテキスト](https://example.com)
""",
        "zh": """# 标题

这是一篇基础的 Markdown 文档。

## 副标题

可以使用 **粗体** 或 *斜体* 进行强调。

### 列表
- 项目 1
- 项目 2
- 项目 3

### 链接
[链接文本](https://example.com)
""",
    }[lang]


def _readme_template(lang):
    texts = {
        "ko": ("프로젝트 이름", "프로젝트 한 줄 설명", "개요", "프로젝트에 대한 자세한 설명을 작성합니다.",
               "기능", "기능", "개발 중", "설치", "사용법", "문서", "전체 문서 보기", "기여",
               "기여를 환영합니다! [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.", "라이선스"),
        "en": ("Project Name", "One-line project description", "Overview", "Describe your project in detail here.",
               "Features", "Feature", "in progress", "Installation", "Usage", "Documentation", "Read the full docs", "Contributing",
               "Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).", "License"),
        "ja": ("プロジェクト名", "プロジェクトの一行説明", "概要", "プロジェクトの詳しい説明を書きます。",
               "機能", "機能", "開発中", "インストール", "使い方", "ドキュメント", "ドキュメント全文を見る", "コントリビュート",
               "コントリビュート歓迎です! [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。", "ライセンス"),
        "zh": ("项目名称", "一句话项目简介", "概述", "在这里详细介绍你的项目。",
               "功能", "功能", "开发中", "安装", "使用方法", "文档", "查看完整文档", "参与贡献",
               "欢迎贡献! 请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。", "许可证"),
    }[lang]
    (name, tagline, overview, overview_body, features, feature, wip, install, usage,
     docs, docs_link, contributing, contributing_body, license_title) = texts
    return f"""# {name}

> {tagline}

[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)]()

## 📋 {overview}

{overview_body}

## ✨ {features}

- ✅ {feature} 1
- ✅ {feature} 2
- 🚧 {feature} 3 ({wip})

## 📦 {install}

```bash
npm install project-name
```

## 🚀 {usage}

```javascript
const project = require('project-name');
project.init();
```

## 📖 {docs}

[{docs_link}](https://docs.example.com)

## 🤝 {contributing}

{contributing_body}

## 📄 {license_title}

MIT License
"""


def _meeting_template(lang, now):
    date_formats = {"ko": "%Y년 %m월 %d일", "en": "%B %d, %Y", "ja": "%Y年%m月%d日", "zh": "%Y年%m月%d日"}
    today = now.strftime(date_formats[lang])
    return {
        "ko": f"""# 📝 회의록

| 항목 | 내용 |
|------|------|
| **날짜** | {today} |
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
        "en": f"""# 📝 Meeting Notes

| Item | Details |
|------|------|
| **Date** | {today} |
| **Time** | 10:00 - 11:00 |
| **Location** | Meeting Room A |
| **Attendees** | Alex, Sam, Jordan |
| **Recorder** | Alex |

---

## 📌 Agenda

1. Project status update
2. Next sprint planning
3. Open issues

## 📝 Discussion

### 1. Project status

#### Completed
- [x] User authentication module
- [x] Dashboard UI

#### In progress
- [ ] API optimization
- [ ] Test coverage

### 2. Next sprint

| Owner | Task | Due | Priority |
|--------|------|------|----------|
| Alex | Backend API | 12/15 | 🔴 High |
| Sam | Frontend | 12/20 | 🟡 Medium |
| Jordan | QA testing | 12/25 | 🟢 Low |

## ✅ Decisions

1. Keep the weekly stand-up
2. Code review is required for every change

## 📅 Next meeting

- **When**: Next Monday 10:00
- **Agenda**: Sprint review
""",
        "ja": f"""# 📝 議事録

| 項目 | 内容 |
|------|------|
| **日付** | {today} |
| **時間** | 10:00 - 11:00 |
| **場所** | 会議室 A |
| **参加者** | 山田、佐藤、鈴木 |
| **記録者** | 山田 |

---

## 📌 議題

1. プロジェクト進捗の共有
2. 次のスプリント計画
3. 課題の検討

## 📝 議論内容

### 1. プロジェクト進捗

#### 完了したタスク
- [x] ユーザー認証モジュール
- [x] ダッシュボード UI

#### 進行中のタスク
- [ ] API の最適化
- [ ] テストコードの作成

### 2. 次のスプリント

| 担当者 | タスク | 期限 | 優先度 |
|--------|------|------|----------|
| 山田 | バックエンド API | 12/15 | 🔴 高 |
| 佐藤 | フロントエンド | 12/20 | 🟡 中 |
| 鈴木 | QA テスト | 12/25 | 🟢 低 |

## ✅ 決定事項

1. 週次スタンドアップを継続
2. コードレビューを必須化

## 📅 次回の会議

- **日時**: 来週月曜日 10:00
- **議題**: スプリントレビュー
""",
        "zh": f"""# 📝 会议纪要

| 项目 | 内容 |
|------|------|
| **日期** | {today} |
| **时间** | 10:00 - 11:00 |
| **地点** | 会议室 A |
| **参会人** | 张伟、李娜、王强 |
| **记录人** | 张伟 |

---

## 📌 议程

1. 项目进展同步
2. 下个迭代计划
3. 问题讨论

## 📝 讨论内容

### 1. 项目进展

#### 已完成
- [x] 用户认证模块
- [x] 仪表盘 UI

#### 进行中
- [ ] API 优化
- [ ] 编写测试代码

### 2. 下个迭代

| 负责人 | 任务 | 截止 | 优先级 |
|--------|------|------|----------|
| 张伟 | 后端 API | 12/15 | 🔴 高 |
| 李娜 | 前端 | 12/20 | 🟡 中 |
| 王强 | QA 测试 | 12/25 | 🟢 低 |

## ✅ 决议

1. 保持每周站会
2. 代码评审为必需流程

## 📅 下次会议

- **时间**: 下周一 10:00
- **议程**: 迭代回顾
""",
    }[lang]


def _api_template(lang):
    texts = {
        "ko": {
            "title": "API 문서", "overview": "개요", "overview_body": "이 문서는 REST API의 사용법을 설명합니다.",
            "auth": "인증", "auth_body": "모든 요청에 API 키가 필요합니다:", "endpoints": "엔드포인트",
            "get_user": "사용자 조회", "params": "파라미터", "cols": "| 이름 | 타입 | 필수 | 설명 |",
            "user_id": "사용자 ID", "response": "응답", "create_user": "사용자 생성", "body": "요청 본문",
            "sample_name": "홍길동", "errors": "에러 코드", "err_cols": "| 코드 | 설명 | 해결 방법 |",
            "e400": "| 400 | 잘못된 요청 | 요청 파라미터 확인 |", "e401": "| 401 | 인증 실패 | API 키 확인 |",
            "e404": "| 404 | 리소스 없음 | ID 확인 |", "e500": "| 500 | 서버 오류 | 관리자 문의 |",
        },
        "en": {
            "title": "API Documentation", "overview": "Overview", "overview_body": "This document explains how to use the REST API.",
            "auth": "Authentication", "auth_body": "Every request requires an API key:", "endpoints": "Endpoints",
            "get_user": "Get user", "params": "Parameters", "cols": "| Name | Type | Required | Description |",
            "user_id": "User ID", "response": "Response", "create_user": "Create user", "body": "Request body",
            "sample_name": "Jane Doe", "errors": "Error codes", "err_cols": "| Code | Meaning | How to fix |",
            "e400": "| 400 | Bad request | Check request parameters |", "e401": "| 401 | Unauthorized | Check your API key |",
            "e404": "| 404 | Not found | Check the ID |", "e500": "| 500 | Server error | Contact support |",
        },
        "ja": {
            "title": "API ドキュメント", "overview": "概要", "overview_body": "このドキュメントでは REST API の使い方を説明します。",
            "auth": "認証", "auth_body": "すべてのリクエストに API キーが必要です:", "endpoints": "エンドポイント",
            "get_user": "ユーザー取得", "params": "パラメータ", "cols": "| 名前 | 型 | 必須 | 説明 |",
            "user_id": "ユーザー ID", "response": "レスポンス", "create_user": "ユーザー作成", "body": "リクエストボディ",
            "sample_name": "山田太郎", "errors": "エラーコード", "err_cols": "| コード | 説明 | 対処法 |",
            "e400": "| 400 | 不正なリクエスト | パラメータを確認 |", "e401": "| 401 | 認証失敗 | API キーを確認 |",
            "e404": "| 404 | リソースなし | ID を確認 |", "e500": "| 500 | サーバーエラー | 管理者に連絡 |",
        },
        "zh": {
            "title": "API 文档", "overview": "概述", "overview_body": "本文档介绍 REST API 的使用方法。",
            "auth": "认证", "auth_body": "所有请求都需要 API 密钥:", "endpoints": "接口",
            "get_user": "查询用户", "params": "参数", "cols": "| 名称 | 类型 | 必填 | 说明 |",
            "user_id": "用户 ID", "response": "响应", "create_user": "创建用户", "body": "请求体",
            "sample_name": "张三", "errors": "错误码", "err_cols": "| 代码 | 说明 | 解决方法 |",
            "e400": "| 400 | 请求错误 | 检查请求参数 |", "e401": "| 401 | 认证失败 | 检查 API 密钥 |",
            "e404": "| 404 | 资源不存在 | 检查 ID |", "e500": "| 500 | 服务器错误 | 联系管理员 |",
        },
    }[lang]
    t = texts
    return f"""# {t['title']}

## 📚 {t['overview']}

{t['overview_body']}

**Base URL**: `https://api.example.com/v1`

## 🔐 {t['auth']}

{t['auth_body']}

```
Authorization: Bearer YOUR_API_KEY
```

## 📡 {t['endpoints']}

### {t['get_user']}

```http
GET /users/{{id}}
```

#### {t['params']}

{t['cols']}
|------|------|------|------|
| id | string | ✅ | {t['user_id']} |

#### {t['response']}

```json
{{
  "id": "123",
  "name": "{t['sample_name']}",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}}
```

### {t['create_user']}

```http
POST /users
```

#### {t['body']}

```json
{{
  "name": "{t['sample_name']}",
  "email": "user@example.com",
  "password": "secure123"
}}
```

## ⚠️ {t['errors']}

{t['err_cols']}
|------|------|----------|
{t['e400']}
{t['e401']}
{t['e404']}
{t['e500']}
"""


def _blog_template(lang, now):
    t = {
        "ko": {
            "title": "제목을 입력하세요", "author": "작성자", "tags": "[태그1, 태그2, 태그3]", "h1": "블로그 제목",
            "cover": "대표 이미지", "intro": "들어가며",
            "intro_body": "독자의 관심을 끄는 도입부를 작성합니다. 이 글에서 다룰 내용을 간략히 소개하세요.",
            "key": "핵심 메시지", "key_body": "한 문장으로 요약", "body": "본문", "s1": "첫 번째 섹션",
            "s1_body": "내용을 작성합니다. 적절한 예시와 함께 설명하세요.", "code_comment": "코드 예시",
            "s2": "두 번째 섹션", "s2_body": "추가 내용을 작성합니다.",
            "p1": "첫 번째 포인트", "p2": "두 번째 포인트", "p3": "세 번째 포인트", "outro": "마치며",
            "outro_body": "핵심 내용을 정리하고 독자에게 남기고 싶은 메시지를 작성합니다.",
            "thanks": "읽어주셔서 감사합니다! 질문이 있으시면 댓글로 남겨주세요.",
        },
        "en": {
            "title": "Enter a title", "author": "Author", "tags": "[tag1, tag2, tag3]", "h1": "Blog Title",
            "cover": "Cover image", "intro": "Introduction",
            "intro_body": "Hook the reader with a strong opening and briefly describe what this post covers.",
            "key": "Key message", "key_body": "Summarize it in one sentence", "body": "Main content", "s1": "First section",
            "s1_body": "Write your content here and explain it with examples.", "code_comment": "Code example",
            "s2": "Second section", "s2_body": "Add more details.",
            "p1": "First point", "p2": "Second point", "p3": "Third point", "outro": "Wrapping up",
            "outro_body": "Summarize the key takeaways and leave the reader with a final thought.",
            "thanks": "Thanks for reading! Leave a comment if you have any questions.",
        },
        "ja": {
            "title": "タイトルを入力", "author": "著者", "tags": "[タグ1, タグ2, タグ3]", "h1": "ブログのタイトル",
            "cover": "アイキャッチ画像", "intro": "はじめに",
            "intro_body": "読者の興味を引く導入を書きます。この記事で扱う内容を簡単に紹介しましょう。",
            "key": "要点", "key_body": "一文でまとめる", "body": "本文", "s1": "最初のセクション",
            "s1_body": "内容を書きます。適切な例を交えて説明しましょう。", "code_comment": "コード例",
            "s2": "2 番目のセクション", "s2_body": "追加の内容を書きます。",
            "p1": "1 つ目のポイント", "p2": "2 つ目のポイント", "p3": "3 つ目のポイント", "outro": "おわりに",
            "outro_body": "要点を整理し、読者に伝えたいメッセージを書きます。",
            "thanks": "お読みいただきありがとうございました! ご質問はコメントでどうぞ。",
        },
        "zh": {
            "title": "请输入标题", "author": "作者", "tags": "[标签1, 标签2, 标签3]", "h1": "博客标题",
            "cover": "封面图片", "intro": "引言",
            "intro_body": "用一段引人入胜的开头吸引读者，并简要介绍本文要讲的内容。",
            "key": "核心观点", "key_body": "用一句话概括", "body": "正文", "s1": "第一部分",
            "s1_body": "在这里撰写内容，并结合示例进行说明。", "code_comment": "代码示例",
            "s2": "第二部分", "s2_body": "补充更多内容。",
            "p1": "第一点", "p2": "第二点", "p3": "第三点", "outro": "结语",
            "outro_body": "总结要点，并留下想对读者说的话。",
            "thanks": "感谢阅读! 如有问题欢迎留言。",
        },
    }[lang]
    return f"""---
title: "{t['title']}"
date: {now.strftime('%Y-%m-%d')}
author: {t['author']}
tags: {t['tags']}
---

# {t['h1']}

![{t['cover']}](cover.jpg)

## {t['intro']}

{t['intro_body']}

> 💡 **{t['key']}**: {t['key_body']}

## {t['body']}

### {t['s1']}

{t['s1_body']}

```python
# {t['code_comment']}
def hello():
    print("Hello, World!")
```

### {t['s2']}

{t['s2_body']}

1. {t['p1']}
2. {t['p2']}
3. {t['p3']}

## {t['outro']}

{t['outro_body']}

---

*{t['thanks']}*
"""


_TEMPLATE_NAMES = [
    ("basic", {"ko": "기본 문서", "en": "Basic Document", "ja": "基本の文書", "zh": "基础文档"}),
    ("readme", {"ko": "README 템플릿", "en": "README Template", "ja": "README テンプレート", "zh": "README 模板"}),
    ("meeting", {"ko": "회의록", "en": "Meeting Notes", "ja": "議事録", "zh": "会议纪要"}),
    ("api", {"ko": "기술 문서", "en": "Technical Docs", "ja": "技術文書", "zh": "技术文档"}),
    ("blog", {"ko": "블로그 포스트", "en": "Blog Post", "ja": "ブログ記事", "zh": "博客文章"}),
]


def _normalize(lang):
    return lang if lang in ("ko", "en", "ja", "zh") else DEFAULT_LANGUAGE


def example_templates(lang, now=None):
    """Return [(id, display_name, markdown), ...]. Dates are filled in at call time."""
    lang = _normalize(lang)
    now = now or datetime.now()
    bodies = {
        "basic": _basic_template(lang),
        "readme": _readme_template(lang),
        "meeting": _meeting_template(lang, now),
        "api": _api_template(lang),
        "blog": _blog_template(lang, now),
    }
    return [(template_id, names[lang], bodies[template_id]) for template_id, names in _TEMPLATE_NAMES]


# ============== Editor helpers ==============

_CELL_WORDS = {
    "ko": ("헤더", "내용", "굵게", "기울임", "취소선", "코드", "링크", "이미지"),
    "en": ("Header", "Cell", "bold", "italic", "strikethrough", "code", "link", "image"),
    "ja": ("見出し", "内容", "太字", "斜体", "取り消し線", "コード", "リンク", "画像"),
    "zh": ("表头", "内容", "粗体", "斜体", "删除线", "代码", "链接", "图片"),
}


def autocomplete_items(lang):
    header, cell, bold, italic, strike, code, link, image = _CELL_WORDS[_normalize(lang)]
    return [
        "# ", "## ", "### ", "#### ", "##### ", "###### ",
        f"**{bold}**", f"*{italic}*", f"~~{strike}~~", f"`{code}`",
        f"[{link}](url)", f"![{image}](url)",
        "- ", "1. ", "- [ ] ", "- [x] ",
        "```\n```", "```python\n```", "```javascript\n```", "```mermaid\n```",
        "> ", "---",
        f"| {header} |\n|---|\n| {cell} |",
    ]


def default_snippets(lang, now=None):
    header, cell = _CELL_WORDS[_normalize(lang)][:2]
    now = now or datetime.now()
    return {
        "todo": "- [ ] ",
        "done": "- [x] ",
        "note": "> **📝 Note:** ",
        "warn": "> **⚠️ Warning:** ",
        "tip": "> **💡 Tip:** ",
        "code": "```\n$1\n```",
        "link": "[$1]($2)",
        "img": "![$1]($2)",
        "table2": f"| {header}1 | {header}2 |\n|-------|-------|\n| {cell}1 | {cell}2 |",
        "table3": f"| {header}1 | {header}2 | {header}3 |\n|-------|-------|-------|\n| {cell}1 | {cell}2 | {cell}3 |",
        "mermaid": "```mermaid\nflowchart TD\n    A --> B\n```",
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "datetime": now.strftime("%Y-%m-%d %H:%M"),
    }
