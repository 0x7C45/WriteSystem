---
name: sci-diagram
description: 科研非数据表达图表生成。覆盖 6 类 35 种图表类型，双引擎（Mermaid + Graphviz）交叉互补，含 MVP 质量评价体系。适用于论文科研绘图。
user-invocable: true
argument-hint: "[内容描述或图表需求]"
---

# 科研图谱生成 Skill

为学术论文生成高质量非数据表达图表。双引擎（Mermaid + Graphviz）交叉互补，覆盖全部 6 类科研图表。

## When to Activate

- 用户要求生成流程图、框架图、概念图、泳道图、架构图、技术路线图
- 论文写作场景中的图表需求（开题报告、毕设论文、期刊投稿）
- 用户描述一个系统/算法/流程/概念，并需要可视化表达
- 关键词：图表、示意图、流程、框架、概念、架构、机制、技术路线、研究路径

## Core Workflow

```
输入：内容描述（文本、代码、论文段落）
  ↓
步骤 1: 识别图表类型 → 参考 references/chart-catalog.md
  ↓
步骤 2: 选择工具 → 参考 references/tool-rules.md
  ↓
步骤 3: 生成图表 → 参考 templates/ 中的语法模板
  ↓
步骤 4: 质量检查 → 参考 references/quality-framework.md
  ↓
步骤 5: 交付 PNG + SVG + 源文件
```

## Step 1: 识别图表类型

根据内容特征匹配 6 类中的具体类型：

| 内容特征 | 类别 | 典型图表 |
|---------|------|---------|
| "怎么做" — 步骤、顺序、路径 | A. 流程与步骤类 | 流程框图、实验流程图、方法流程图、技术路线图、泳道图 |
| "由什么组成" — 分层、模块、架构 | B. 框架与结构类 | 框架图、系统架构图、模型架构图、分层结构图 |
| "是什么" — 概念、定义、关系 | C. 概念与定义类 | 概念图、概念拆解图、分类图、术语关系图、知识图谱 |
| "为什么" — 因果、机制、变量 | D. 机制与因果类 | 作用机制图、因果路径图、理论模型图、变量关系图 |
| "谁参与" — 角色、场景、协作 | E. 场景与交互类 | 应用场景图、用户旅程图、多主体协作图、交互流程图、时序图 |
| "一眼看懂" — 总结、亮点、贡献 | F. 总结与传播类 | 图形摘要、论文贡献图、研究亮点图、对比总结图 |

完整目录见 `references/chart-catalog.md`。

## Step 2: 选择工具

**默认双引擎，按类别分工：**

| 类别 | 首选工具 | Fallback | 理由 |
|------|---------|----------|------|
| A. 流程与步骤类 | **Graphviz** | Mermaid | 自动布局处理循环和分支最优 |
| B. 框架与结构类 | **Mermaid** | Graphviz | subgraph 语法直观、文档原生渲染、满分可修改性 |
| C. 概念与定义类 | **Mermaid** | Graphviz | 边标签+3 层结构、文本迭代最快 |
| D. 机制与因果类 | **Graphviz** | Mermaid | neato/fdp 处理复杂关系网、闭环、双向边 |
| E. 场景与交互类 | **Mermaid** | Graphviz | sequenceDiagram 原生支持时序/交互流程 |
| F. 总结与传播类 | **Mermaid** | Graphviz | 快速迭代、适合高信息密度 |

详细规则和 fallback 条件见 `references/tool-rules.md`。

## Step 3: 生成图表

### Mermaid 生成流程

1. 在目标项目目录下创建 `diagrams.md`
2. 用 Mermaid 语法定义图表（参考 `templates/mermaid-recipes.md`）
3. 渲染输出：
   ```bash
   # PNG 300 DPI（-s 3 放大 3 倍约等于 300 DPI）
   PUPPETEER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     mmdc -i diagrams.md -o output/diagram.png -w 2048 -s 3
   # SVG 矢量
   PUPPETEER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     mmdc -i diagrams.md -o output/diagram.svg
   ```

### Graphviz 生成流程

1. 创建 Python 脚本（如 `generate_diagram.py`）
2. 用 `graphviz.Digraph` 或 `graphviz.Graph` 定义图表（参考 `templates/graphviz-recipes.md`）
3. 渲染输出：
   ```python
   # PNG 300 DPI
   graph.format = 'png'
   graph.attr(dpi='300')
   graph.render('output/diagram', cleanup=True)
   # SVG 矢量
   graph.format = 'svg'
   graph.render('output/diagram', cleanup=True)
   ```

### 通用规范

- **双语标注**：中文主标签 + 英文副标签（如 `初始化 Initialize`）
- **禁止嵌入排版信息**：图号（如"图4-10"）和图名（如"miniRvEMU执行流程图"）属于论文排版层，不得嵌入图表内容。图题由论文文档管理，图表只承载语义内容
- **字体**：macOS 用 `PingFang SC`，Linux 用 `Noto Sans CJK SC`
- **节点数**：单图建议 ≤15 节点，超出时考虑拆分为多张子图或提升抽象层级
- **配色**：统一 Material Design 色板
  - 开始/输入：绿色 `#4CAF50`
  - 处理/数据：蓝色 `#2196F3`
  - 决策/算法：橙色 `#FF9800`
  - 输出/结果：红色 `#E91E63`
  - 辅助/说明：紫色 `#9C27B0`

## Step 4: 质量检查

用 5 维 MVP 体系逐项检查（每维 0/3/5 分）：

| 维度 | 核心问题 | 检查要点 |
|------|---------|---------|
| 语义准确性 | 图有没有画错？ | 概念名称、关系方向、因果关系、箭头方向 |
| 结构逻辑 | 图表类型选对了吗？ | 主线清晰、分支合理、层级明确、起止清楚 |
| 抽象粒度 | 太粗、太细，还是刚好？ | 粒度一致、层级不混乱、适合目标读者 |
| 视觉清晰度 | 能轻松看懂吗？ | 字体够大、无重叠、箭头不乱、颜色辅助理解 |
| 可修改性 | 后续能快速迭代吗？ | 有源文件、能局部修改、可版本管理 |

**总分判断**：
- 0-10：不可用，重画
- 11-16：方向可保留，需大改
- 17-21：基本可用，需优化
- 22-25：可交付

详细评分标准见 `references/quality-framework.md`。结构逻辑与抽象粒度的常见反模式清单（扁平辐射、单线链、信息稀疏、装饰节点）亦见该文件。

## Step 5: 交付

### 默认输出（本科 & 期刊统一）

- **PNG (300 DPI)** + SVG + 可编辑源文件（.md 或 .py）
- Mermaid 优先（迭代快），Graphviz 补充复杂图

### 学术期刊附加要求

- Graphviz 优先（布局稳定），Mermaid 辅助快速验证
- 需要用户确认每张图的语义准确性达到 5 分

### 按需启用

- HTML 报告：用户明确要求交互式交付或多图对比时才启用
- matplotlib：用户要求出版级精细控制时才启用

## References

- `references/chart-catalog.md` — 6 类 25+ 种图表详细目录
- `references/tool-rules.md` — 工具选择规则 + fallback 条件
- `references/quality-framework.md` — MVP 5 维评价体系完整版
- `templates/mermaid-recipes.md` — Mermaid 语法模板集
- `templates/graphviz-recipes.md` — Graphviz DOT 语法模板集
