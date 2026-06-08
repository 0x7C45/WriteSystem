# 管线交互配置

> 版本: v1.0.0 | 所属: WriteSystem spec/conventions

---

## 概述

用户对管线的交互行为有三个可调维度，通过 `订单摘要.md` 的 frontmatter 控制。
每个维度可在项目启动时设置，也可在任意阶段修改后立即生效。

---

## 配置项

### 1. `interaction_level` — 交互粒度

控制用户介入的频率。

| 值 | 确认节点 | 适用场景 |
|----|---------|---------|
| `coarse` (默认) | 5 个：订单 → 骨架 → 草稿 → 交付 | 用户信任管线，只需关键决策 |
| `fine` | coarse 的 5 个 + 每章写完加一次确认 | 用户想逐章把控质量 |
| `minimal` | 2 个：订单 → 交付 | 用户完全托管，只看结果 |

**`coarse` 节点：**

```
① 订单确认    — Phase 0 完成，用户审阅订单摘要 + 格式规范
② 骨架确认    — Phase 1b 完成 + M2 PASS，用户审阅骨架大纲
③ 草稿确认    — Phase 2 完成 + M3 PASS，用户审阅正文草稿
④ 交付确认    — Phase 3 完成 + M4 PASS，用户审阅终稿
⑤ 归档确认    — 用户确认交付 → 触发归档
```

**`fine` 额外节点：**

```
在 coarse 基础上，每章 Phase 2 Gate 2.2 通过后加一次确认：
  第1章写完 → 用户确认 → 继续第2章
  第2章写完 → 用户确认 → 继续第3章
  ...
```

**`minimal` 节点：**

```
① 订单确认    — Phase 0 完成
⑤ 归档确认    — Phase 3 完成 + M4 PASS
（中间全部自动，不打断用户）
```

### 2. `revise_mode` — REVISE 处理模式

控制 Gate 或 Milestone 返回 REVISE 时的行为。

| 值 | 行为 | 适用场景 |
|----|------|---------|
| `auto` (默认) | AI 自动修复并重新提交，最多 `max_revise_rounds` 轮 | 用户信任 AI 能自行纠错 |
| `manual` | 暂停管线，通知用户问题，等待用户决策（修改后继续 / 忽略继续 / 放弃） | 用户想自己把控修改方向 |

**`auto` 模式下的轮次限制：**

- 默认 `max_revise_rounds = 2`
- 达到上限后降级为 `manual` 模式（通知用户）
- 每轮自动修复后记录变更到 `导师确认态.md`

**`manual` 模式下的通知格式：**

```
⚠️ 管线暂停 — M2 骨架确认返回 REVISE

问题: 第3章方法论缺少文献支撑
位置: 03_计划与方案/骨架大纲.md, §3.2

选项:
  [1] AI 自动修复后继续
  [2] 我自己修改后继续
  [3] 忽略此问题，继续
  [4] 放弃当前项目
```

### 3. `m3_mode` — M3 草稿审查时机

| 值 | 行为 |
|----|------|
| `merged` (默认，不可改) | 所有章节合并为正文草稿后，一次性提交 M3 |

> M3 目前只支持 `merged`。未来如需「每章独立 M3」可扩展。

---

## Frontmatter 格式

在 `00_订单信息/订单摘要.md` 的 YAML 头部添加：

```yaml
---
repo_spec_version: v1.0.0
project_version: 1
created: 2026-06-04
status: active
pipeline:
  interaction_level: coarse     # coarse | fine | minimal
  revise_mode: auto             # auto | manual
  max_revise_rounds: 2          # 仅 revise_mode=auto 时生效
---
```

### 默认值

如果 frontmatter 中未声明 `pipeline` 段，使用以下默认值：

```
interaction_level = coarse
revise_mode = auto
max_revise_rounds = 2
```

---

## 运行时修改

用户可随时修改这些值，在下一次检查点立即生效：

```
例: 用户觉得 fine 太繁琐，改为 coarse
  → 修改 frontmatter 中 interaction_level: coarse
  → 当前章节继续完成后，后续章节不再逐章确认
```

---

## 管线中的引用点

pipeline-spec.md 中各交互节点的表述从「停止，等待用户确认」改为：

```
如果 interaction_level = fine 且当前为 Phase 2 章末 → 停止等待确认
如果 interaction_level = coarse 且当前为 M2/M3/M4 → 停止等待确认
如果 interaction_level = minimal 且当前为 M4 → 停止等待确认
否则 → 自动继续
```

各 REVISE 处理点从「返回对应步骤修改」改为：

```
如果 revise_mode = auto 且当前轮次 < max_revise_rounds → 自动修复
如果 revise_mode = auto 且当前轮次 ≥ max_revise_rounds → 降级为 manual
如果 revise_mode = manual → 暂停，通知用户选择
```
