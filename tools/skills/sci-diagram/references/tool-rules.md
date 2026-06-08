# 工具选择规则 — Mermaid vs Graphviz

## 默认选择（按类别）

| 类别 | 默认工具 | 原因 |
|------|----------|------|
| A. 流程图 Flowchart | **Graphviz** | 自动布局处理复杂分支和循环回边 |
| B. 框架图 Framework | **Mermaid** | 文本迭代快，subgraph 语法简洁 |
| C. 概念图 Concept Map | **Mermaid** | 层次结构简单，文档内嵌方便 |
| D. 机制图 Mechanism | **Graphviz** | 双向边、反馈环需要精确边路由 |
| E. 场景与交互类 | **Mermaid** | sequenceDiagram 原生支持时序/交互流程；复杂布局可用 Graphviz fallback |
| F. 总结图 Summary | **Mermaid** | 对比/高亮结构简单，快速出图 |

### 子类型例外

| 子类型 | 推荐工具 | 原因 |
|--------|---------|------|
| 时序图 (Sequence Diagram) | **Mermaid** (`sequenceDiagram`) | Graphviz 无原生时序图支持，用 DOT 模拟效果差 |
| 状态机图 (State Machine) | **Mermaid** (`stateDiagram-v2`) 或 Graphviz | Mermaid 原生状态转换语法；复杂状态机用 Graphviz fallback |
| 泳道图 (Swimlane) | **Graphviz** | 多泳道交叉边需要高级布局 |
| 技术路线图 (Timeline/Roadmap) | **Mermaid** (`timeline`) | timeline 语法原生支持阶段分组+里程碑，无需具体日期；有并行/依赖关系时回退到 flowchart + subgraph |
| 分类图/概念拆解 (Classification/Breakdown) | **Mermaid** (`mindmap` 或 `flowchart`) | 简单并列分类用 mindmap（自动辐射布局）；有交叉连接或分类标准中间层时用 flowchart + subgraph |

**节点数建议**：单图建议 ≤15 节点。超出时考虑拆分为多张子图或提升抽象层级。时序图的复杂度以参与者数和消息数衡量，timeline 以 section 数和 task 数衡量，mindmap 以层级深度衡量，均不受此节点数限制（详见 quality-framework.md 最低结构标准表）。

## 回退条件

### 从 Mermaid 切换到 Graphviz

当满足以下任一条件时，应切换到 Graphviz：

- 节点数 > 15：Mermaid 布局质量显著下降
- 存在复杂循环或反馈回路：Mermaid 的边路由无法精确控制
- 需要精确控制边的走向（如避免交叉、指定弯曲路径）
- 要求输出在出版/打印场景下稳定一致

### 从 Graphviz 切换到 Mermaid

当满足以下任一条件时，可切换到 Mermaid：

- 节点数 < 8：结构简单，Mermaid 足以胜任
- 需要快速迭代，频繁文本编辑后预览
- 图表将嵌入 Markdown 文档（GitHub、VS Code 原生支持）
- 目标受众需要自行修改图表内容（Mermaid 文本门槛更低）

## 工具特性对比

| 特性 | Mermaid | Graphviz |
|------|---------|----------|
| 布局引擎 | 内置 | dot / neato / fdp / circo |
| 文本语法 | 简洁直观 | 较冗长但功能丰富 |
| 自动布局质量 | 简单图表现好 | 复杂图表现优秀 |
| 边路由 | 基础 | 高级（splines 精确控制） |
| 文档嵌入 | 原生支持（GitHub、VS Code） | 需先渲染为图片 |
| 迭代速度 | 最快（文本编辑 + 实时预览） | 中等（代码 + 渲染） |
| 节点形状种类 | 有限 | 丰富（20+ 内置形状） |
| 字体处理 | Web 字体 | 系统字体（需指定 PingFang SC） |
| 输出稳定性 | 不同版本间可能有差异 | 跨版本稳定 |
| 子图嵌套 | 支持 subgraph | 支持 cluster_* 子图 |
| 边标签 | 直接写在边上 | label 参数，可控制字号位置 |
| 样式定义 | classDef 批量定义 | node/edge 级别或全局 attr |

## 渲染命令

### Mermaid 渲染

```bash
# 使用 mermaid-cli (mmdc) 渲染
# 需先安装: npm install -g @mermaid-js/mermaid-cli
mmdc -i diagram.mmd -o output/diagram.png -w 2048 -H 1024

# macOS 上需指定 Chromium 路径
PUPPETEER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  mmdc -i diagram.mmd -o output/diagram.png

# 同时输出 PNG 和 SVG
mmdc -i diagram.mmd -o output/diagram.png
mmdc -i diagram.mmd -o output/diagram.svg
```

### Graphviz 渲染

```bash
# 使用 Python graphviz 库渲染
python3 diagram.py

# 脚本内部逻辑（模板中已内置）：
# 1. graph.render(format='png', directory=output_dir, cleanup=True)
# 2. graph.render(format='svg', directory=output_dir, cleanup=True)
```

## 标准调色板

所有图表统一使用以下五色调色板：

| 颜色 | 色值 | 用途 |
|------|------|------|
| 绿色 | `#4CAF50` | 开始/结束、输入层、正向状态 |
| 蓝色 | `#2196F3` | 过程节点、数据层、核心概念 |
| 橙色 | `#FF9800` | 判断/决策、中间层、辅助结构 |
| 红色 | `#E91E63` | 关键输出、终止条件、异常路径 |
| 紫色 | `#9C27B0` | 补充概念、扩展节点、边缘层 |
