DOCS = {
"en": """# Product Launch Plan

Ship **Nebula Note 3.1** to the Mac App Store with *live* Mermaid diagrams and math.

## Timeline

| Phase | Owner | Status |
|---|---|---|
| Design | Alex | ✅ Done |
| Build | Sam | 🚧 In progress |
| Release | Jordan | ⏳ Planned |

## Release flow

```mermaid
flowchart LR
    A[Write] --> B{Review}
    B -->|Approved| C[Build]
    B -->|Changes| A
    C --> D((Ship))
```

## Growth model

Expected reach: $R = N \\cdot (1 + g)^t$

```python
def launch(version):
    print(f"Shipping {version} 🚀")
```
""",
"ko": """# 제품 출시 계획

실시간 Mermaid 다이어그램과 수식을 담아 **Nebula Note 3.1**을 *Mac App Store*에 출시합니다.

## 일정

| 단계 | 담당 | 상태 |
|---|---|---|
| 디자인 | 김지민 | ✅ 완료 |
| 개발 | 이준호 | 🚧 진행 중 |
| 출시 | 박서연 | ⏳ 예정 |

## 출시 흐름

```mermaid
flowchart LR
    A[작성] --> B{검토}
    B -->|승인| C[빌드]
    B -->|수정| A
    C --> D((출시))
```

## 성장 모델

예상 도달 수: $R = N \\cdot (1 + g)^t$

```python
def launch(version):
    print(f"{version} 출시 🚀")
```
""",
"ja": """# 製品リリース計画

リアルタイムの Mermaid 図と数式を備えた **Nebula Note 3.1** を *Mac App Store* でリリースします。

## スケジュール

| フェーズ | 担当 | 状況 |
|---|---|---|
| デザイン | 山田 | ✅ 完了 |
| 開発 | 佐藤 | 🚧 進行中 |
| リリース | 鈴木 | ⏳ 予定 |

## リリースの流れ

```mermaid
flowchart LR
    A[執筆] --> B{レビュー}
    B -->|承認| C[ビルド]
    B -->|修正| A
    C --> D((公開))
```

## 成長モデル

想定リーチ: $R = N \\cdot (1 + g)^t$

```python
def launch(version):
    print(f"{version} をリリース 🚀")
```
""",
"zh": """# 产品发布计划

带着实时 Mermaid 图表和数学公式，将 **Nebula Note 3.1** 发布到 *Mac App Store*。

## 时间表

| 阶段 | 负责人 | 状态 |
|---|---|---|
| 设计 | 张伟 | ✅ 完成 |
| 开发 | 李娜 | 🚧 进行中 |
| 发布 | 王强 | ⏳ 计划中 |

## 发布流程

```mermaid
flowchart LR
    A[撰写] --> B{评审}
    B -->|通过| C[构建]
    B -->|修改| A
    C --> D((发布))
```

## 增长模型

预计覆盖: $R = N \\cdot (1 + g)^t$

```python
def launch(version):
    print(f"发布 {version} 🚀")
```
""",
}
