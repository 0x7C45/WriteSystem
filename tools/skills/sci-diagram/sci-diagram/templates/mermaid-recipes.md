# Mermaid 语法模板 — 六类图表

> 每个模板均可直接复制使用，包含中文标签和英文注释。
> 标准调色板：绿色 #4CAF50、蓝色 #2196F3、橙色 #FF9800、红色 #E91E63、紫色 #9C27B0

---

## A. 流程图 (Flowchart)

<!-- 使用 flowchart TD（上到下），包含开始/结束（圆形）、处理（矩形）、判断（菱形）、循环回边 -->

```mermaid
flowchart TD
    %% 开始节点用双括号表示圆形
    START((开始 Start)) --> INIT["初始化<br/>Initialize<br/>变量赋初值"]

    %% 主循环体
    INIT --> LOOP["循环处理<br/>Process Loop<br/>遍历数据"]

    %% 判断节点用花括号表示菱形
    LOOP --> COND{"条件满足?<br/>Condition Met?"}

    %% 是/否分支
    COND -->|是 Yes| ACTION["执行操作<br/>Execute Action<br/>处理当前项"]
    COND -->|否 No| EXIT["退出循环<br/>Break Loop"]

    %% 操作后继续
    ACTION --> UPDATE["更新状态<br/>Update State<br/>记录中间结果"]
    UPDATE --> MORE{"还有数据?<br/>More Data?"}

    %% 循环回边：More → Loop
    MORE -->|是 Yes| LOOP
    MORE -->|否 No| RESULT["汇总结果<br/>Aggregate Results"]

    EXIT --> RESULT
    RESULT --> END((结束 End))

    %% 样式定义：标准五色调色板
    classDef startEnd fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef process fill:#BBDEFB,stroke:#2196F3,color:#333
    classDef decision fill:#FFF9C4,stroke:#FF9800,color:#333
    classDef output fill:#FCE4EC,stroke:#E91E63,color:#333

    class START,END startEnd
    class INIT,LOOP,ACTION,UPDATE,RESULT process
    class COND,MORE decision
    class EXIT output
```

**关键语法说明**：
- `flowchart TD` — 上到下布局（也可用 `LR` 左到右）
- `(())` — 圆形节点（开始/结束）
- `[]` — 矩形节点（处理步骤）
- `{}` — 菱形节点（判断/决策）
- `-->|标签|` — 带标签的边
- `<br/>` — 节点内换行
- `classDef` — 样式定义，`class` 关键字批量应用

---

## B. 框架图 (Framework Diagram)

<!-- 使用 flowchart TD + subgraph 表示分层结构 -->

```mermaid
flowchart TD
    %% 第一层：输入层
    subgraph LAYER1["输入层 Input Layer"]
        A1["数据源 A<br/>Source A"]
        A2["数据源 B<br/>Source B"]
    end

    %% 第二层：处理层
    subgraph LAYER2["处理层 Processing Layer"]
        B1["数据清洗<br/>Data Cleaning"] --> B2["特征提取<br/>Feature Extraction"]
        B2 --> B3["模型推理<br/>Model Inference"]
    end

    %% 第三层：输出层
    subgraph LAYER3["输出层 Output Layer"]
        C1["结果聚合<br/>Result Aggregation"]
        C2["报告生成<br/>Report Generation"]
    end

    %% 层间连接
    A1 --> B1
    A2 --> B1
    B3 --> C1
    B3 --> C2

    %% 样式：每层一种主色
    classDef inputStyle fill:#E8F5E9,stroke:#4CAF50,color:#333
    classDef processStyle fill:#E3F2FD,stroke:#2196F3,color:#333
    classDef outputStyle fill:#FCE4EC,stroke:#E91E63,color:#333

    class A1,A2 inputStyle
    class B1,B2,B3 processStyle
    class C1,C2 outputStyle
```

**关键语法说明**：
- `subgraph LABEL["显示名"]` — 子图分组表示层
- 层内节点用 `-->` 串联，层间也用 `-->` 连接
- 每层使用独立 classDef，视觉上区分职责

---

## A-bis. 技术路线图 / Timeline

<!-- 使用 timeline 语法，按阶段展示任务和里程碑，无需具体日期 -->

```mermaid
timeline
    title 技术路线图标题<br/>Technology Roadmap Title
    section 阶段一 基础研究<br/>Phase 1: Foundation
        任务 1.1 研究现状分析<br/>Literature Review : 交付物：技术报告<br/>Deliverable: Technical Report
        任务 1.2 工具链搭建<br/>Toolchain Setup : 交付物：开发环境<br/>Deliverable: Dev Environment
    section 阶段二 核心实现<br/>Phase 2: Implementation
        任务 2.1 关键模块设计<br/>Module Design : 交付物：设计文档<br/>Deliverable: Design Doc
        任务 2.2 编码与单元测试<br/>Coding & Testing : 交付物：可运行原型<br/>Deliverable: Prototype
    section 阶段三 验证优化<br/>Phase 3: Validation
        任务 3.1 集成测试<br/>Integration Test : 交付物：测试报告<br/>Deliverable: Test Report
        任务 3.2 性能优化<br/>Optimization : 交付物：最终版本<br/>Deliverable: Final Release
```

**关键语法说明**：
- `timeline` — Mermaid 时间线语法（v9.3+），无需具体日期
- `title` — 图表标题
- `section` — 阶段分组（每个 section 自动换色）
- `任务名 : 交付物描述` — 每行一个任务，冒号后为补充描述
- **不支持 `classDef`**：使用内置配色方案
- **已知渲染 bug**：section 标题和 task 文本中避免使用 `<br/>` 和英文冒号 `:`（会触发 addEvent TypeError）。如需换行，将内容拆分为多个 task
- 若需表达并行/依赖关系，回退到 A 类 flowchart + subgraph 模板
- 适用于 A4 技术路线图、研究路径图、项目阶段规划等场景

---

## C. 概念图 (Concept Map)

<!-- 使用 graph TD（无向），中心节点辐射展开 -->

```mermaid
graph TD
    %% 中心节点用双括号突出显示
    CENTER(("核心主题<br/>Core Topic<br/>研究/算法名称"))

    %% 一级概念：从中心辐射
    CENTER -->|维度一 Dimension 1| C1["概念 A<br/>Concept A"]
    CENTER -->|维度二 Dimension 2| C2["概念 B<br/>Concept B"]
    CENTER -->|维度三 Dimension 3| C3["概念 C<br/>Concept C"]

    %% 二级概念：从一级展开
    C1 --> C1A["细节 A-1<br/>Detail A-1"]
    C1 --> C1B["细节 A-2<br/>Detail A-2"]

    C2 --> C2A["细节 B-1<br/>Detail B-1"]

    C3 --> C3A["细节 C-1<br/>Detail C-1"]
    C3 --> C3B["细节 C-2<br/>Detail C-2"]
    C3 --> C3C["细节 C-3<br/>Detail C-3"]

    %% 样式
    classDef centerStyle fill:#E1BEE7,stroke:#9C27B0,color:#333
    classDef conceptStyle fill:#BBDEFB,stroke:#2196F3,color:#333
    classDef leafStyle fill:#E8F5E9,stroke:#4CAF50,color:#333

    class CENTER centerStyle
    class C1,C2,C3 conceptStyle
    class C1A,C1B,C2A,C3A,C3B,C3C leafStyle
```

**关键语法说明**：
- `graph TD` — 无向图（flowchart 是有向的，graph 是无向的）
- 中心节点用 `((" "))` 双括号突出
- 一级到二级用简短边标签说明关系
- 层次通过 classDef 颜色区分（中心/一级/二级）

---

## C-bis. 分类图 / Taxonomy (flowchart + subgraph)

<!-- 使用 flowchart TD + 嵌套 subgraph，强调分类标准和层级 -->

```mermaid
flowchart TD
    %% 分类根节点
    ROOT["分类根节点<br/>Classification Root<br/>如：RV32I 指令集"]

    %% 分类标准层（菱形决策节点增加结构深度）
    ROOT --> STD{"按什么分类？<br/>Classification<br/>Criterion"}
    STD -->|按功能| GA["类别 A<br/>Category A<br/>如：算术运算类"]
    STD -->|按格式| GB["类别 B<br/>Category B<br/>如：逻辑运算类"]
    STD -->|按用途| GC["类别 C<br/>Category C<br/>如：访存控制类"]

    %% 每个类别用 subgraph 分组，内含子项
    subgraph SA["类别 A: 详细名称<br/>Category A: Detail"]
        A1["子项 A-1<br/>Item A-1<br/>如：ADD — 加法<br/>指令数: N"]
        A2["子项 A-2<br/>Item A-2<br/>如：SUB — 减法"]
        A3["子项 A-3<br/>Item A-3"]
    end
    GA --> SA

    subgraph SB["类别 B: 详细名称<br/>Category B: Detail"]
        B1["子项 B-1<br/>Item B-1"]
        B2["子项 B-2<br/>Item B-2"]
    end
    GB --> SB

    subgraph SC["类别 C: 详细名称<br/>Category C: Detail"]
        C1["子项 C-1<br/>Item C-1"]
    end
    GC --> SC

    %% 交叉连接：某些子项可能跨类别关联
    A1 -.->|依赖/关联| B1

    %% 样式
    classDef rootStyle fill:#E1BEE7,stroke:#9C27B0,color:#333
    classDef critStyle fill:#FFF9C4,stroke:#FBC02D,color:#333
    classDef catStyle fill:#BBDEFB,stroke:#2196F3,color:#333
    classDef itemStyle fill:#E8F5E9,stroke:#4CAF50,color:#333

    class ROOT rootStyle
    class STD critStyle
    class GA,GB,GC catStyle
    class A1,A2,A3,B1,B2,C1 itemStyle
```

**关键语法说明**：
- `flowchart TD` + 菱形 `{" "}` 中间层增加结构深度（分类标准层）
- `subgraph` 按类别分组，视觉上隔离不同类别
- 每个子项包含：名称 + 英文 + 具体示例/数量，提升信息粒度
- `-.->` 虚线表示跨类别关联（可选），增加语义丰富度
- 适用于 C3 分类图、C4 术语关系图等需要层级分类的场景

---

## C-ter. 概念拆解图 (mindmap 语法)

<!-- 使用 mindmap 语法，自动辐射布局，适合纯层级概念 -->

```mermaid
mindmap
  root((核心主题<br/>Core Topic<br/>如：RISC-V 指令集))
    分支A["维度一<br/>Dimension 1<br/>如：基础整数指令"]
      A1["子项 A-1<br/>如：算术运算<br/>ADD/SUB/SLL"]
      A2["子项 A-2<br/>如：逻辑运算<br/>AND/OR/XOR"]
      A3["子项 A-3<br/>如：比较运算<br/>SLT/SLTU"]
    分支B["维度二<br/>Dimension 2<br/>如：扩展指令集"]
      B1["子项 B-1<br/>如：M 扩展<br/>乘除法"]
      B2["子项 B-2<br/>如：F 扩展<br/>单精度浮点"]
    分支C["维度三<br/>Dimension 3<br/>如：系统控制"]
      C1["子项 C-1<br/>如：CSR 指令"]
```

**关键语法说明**：
- `mindmap` — Mermaid 专用思维导图语法（v9.4+）
- `root(( ))` — 圆形根节点，用双括号
- `[" "]` — 可选的方括号文本，支持 `<br/>` 换行
- **缩进表示层级**：2 空格 = 一级分支，4 空格 = 二级子项，以此类推
- **不支持 `classDef`**：使用内置配色，无法自定义颜色
- **只支持树形结构**：不支持交叉连接（跨分支关联）
- 适用于 C1 概念图、C2 概念拆解图、纯层级无交叉的 C3 分类图等场景
- 当概念间有复杂交叉关系时，使用 C-bis 分类图模板（flowchart）更合适

---

## D. 机制图 (Mechanism)

<!-- 使用 graph LR，双向边 + 反馈环 -->

```mermaid
graph LR
    %% 主路径节点
    A["输入信号<br/>Input Signal"] --> B["处理模块 A<br/>Module A"]
    B --> C["处理模块 B<br/>Module B"]
    C --> D["输出结果<br/>Output Result"]

    %% 反馈环：从输出反馈回处理模块
    D -.->|反馈调节<br/>Feedback| B

    %% 辅助模块
    E["辅助模块<br/>Auxiliary Module"] --> B
    E --> C

    %% 横向调节
    A -.->|旁路信号<br/>Bypass| C

    %% 样式
    classDef inputStyle fill:#E8F5E9,stroke:#4CAF50,color:#333
    classDef processStyle fill:#E3F2FD,stroke:#2196F3,color:#333
    classDef outputStyle fill:#FCE4EC,stroke:#E91E63,color:#333
    classDef auxStyle fill:#FFF3E0,stroke:#FF9800,color:#333

    class A inputStyle
    class B,C processStyle
    class D outputStyle
    class E auxStyle
```

**关键语法说明**：
- `graph LR` — 左到右布局，适合展示流程机制
- `-->` 实线箭头表示主路径
- `-.->` 虚线箭头表示反馈/辅助路径（注意 Mermaid 的虚线语法）
- 反馈环是机制图的核心特征，从输出回到中间节点

---

## E. 泳道图 (Swimlane Diagram)

<!-- 使用 flowchart LR + subgraph 表示泳道 -->

```mermaid
flowchart LR
    %% 泳道 1：角色 A
    subgraph LANE1["角色 A Role A"]
        direction TB
        S1["步骤 1<br/>Step 1: 接收请求"] --> S2["步骤 2<br/>Step 2: 初步验证"]
    end

    %% 泳道 2：角色 B
    subgraph LANE2["角色 B Role B"]
        direction TB
        S3["步骤 3<br/>Step 3: 核心处理"] --> S4["步骤 4<br/>Step 4: 结果校验"]
    end

    %% 泳道 3：角色 C
    subgraph LANE3["角色 C Role C"]
        direction TB
        S5["步骤 5<br/>Step 5: 输出生成"] --> S6["步骤 6<br/>Step 6: 交付完成"]
    end

    %% 跨泳道流转
    S2 --> S3
    S4 --> S5
    %% 回退路径（可选）
    S4 -.->|校验失败 Fallback| S3

    %% 样式：每条泳道一种颜色
    classDef lane1Style fill:#E8F5E9,stroke:#4CAF50,color:#333
    classDef lane2Style fill:#E3F2FD,stroke:#2196F3,color:#333
    classDef lane3Style fill:#FCE4EC,stroke:#E91E63,color:#333

    class S1,S2 lane1Style
    class S3,S4 lane2Style
    class S5,S6 lane3Style
```

**关键语法说明**：
- `flowchart LR` — 横向排列泳道
- 每个 `subgraph` 代表一条泳道（一个角色/部门）
- `direction TB` — 泳道内部节点纵向排列
- 跨泳道用 `-->` 连接，形成完整流程
- 回退/异常路径用 `-.->` 虚线箭头

---

## E-bis. 时序图 (Sequence Diagram)

<!-- 使用 sequenceDiagram 展示多参与者之间的消息时序 -->

```mermaid
sequenceDiagram
    %% 参与者定义
    participant Client as 客户端<br/>Client
    participant Server as 服务器<br/>Server
    participant DB as 数据库<br/>Database
    participant Auth as 认证服务<br/>Auth Service

    %% 激活条表示处理中
    activate Client
    Client->>Server: 1. 发送请求<br/>Send Request
    activate Server

    %% 同步调用
    Server->>Auth: 2. 验证令牌<br/>Verify Token
    activate Auth
    Auth-->>Server: 3. 验证结果<br/>Auth Result
    deactivate Auth

    %% 条件分支
    alt 令牌有效 Valid Token
        Server->>DB: 4. 查询数据<br/>Query Data
        activate DB
        DB-->>Server: 5. 返回结果<br/>Return Data
        deactivate DB
        Server-->>Client: 6. 成功响应<br/>Success Response
    else 令牌无效 Invalid Token
        Server-->>Client: 错误：认证失败<br/>Error: Auth Failed
    end

    deactivate Server
    deactivate Client

    %% 注释说明
    Note over Client,Auth: 认证阶段<br/>Authentication Phase
    Note over Server,DB: 数据阶段<br/>Data Phase
```

**关键语法说明**：
- `participant` — 定义参与者（角色/系统）
- `->>` — 实线箭头（同步请求）
- `-->>` — 虚线箭头（异步响应/返回）
- `-x` — 叉号箭头（请求失败）
- `activate/deactivate` — 激活条（显示处理中状态）
- `alt/else/end` — 条件分支
- `loop ... end` — 循环
- `par ... and ... end` — 并行
- `Note over A,B:` — 跨参与者注释
- **注意**：sequenceDiagram 不支持 `classDef` 样式定义

---

## F. 总结图 (Summary)

<!-- 使用 graph LR 做对比，简洁高亮 -->

```mermaid
graph LR
    %% 对比：方案 A
    subgraph PLAN_A["方案 A Plan A"]
        A1["特点 1<br/>Feature 1"] --> A2["特点 2<br/>Feature 2"]
    end

    %% 对比：方案 B
    subgraph PLAN_B["方案 B Plan B"]
        B1["特点 1<br/>Feature 1"] --> B2["特点 2<br/>Feature 2"]
    end

    %% 共同输入
    INPUT["共同输入<br/>Common Input"] --> PLAN_A
    INPUT --> PLAN_B

    %% 关键区别标注
    A2 -->|推荐 Recommended| PICK["选择结果<br/>Selection"]
    B2 -.->|备选 Alternative| PICK

    %% 样式
    classDef inputStyle fill:#E8F5E9,stroke:#4CAF50,color:#333
    classDef planAStyle fill:#E3F2FD,stroke:#2196F3,color:#333
    classDef planBStyle fill:#FFF3E0,stroke:#FF9800,color:#333
    classDef pickStyle fill:#FCE4EC,stroke:#E91E63,color:#333

    class INPUT inputStyle
    class A1,A2 planAStyle
    class B1,B2 planBStyle
    class PICK pickStyle
```

**关键语法说明**：
- `graph LR` — 左右对比布局
- 两个 subgraph 并列展示不同方案
- `-->|推荐|` 实线 + 标签标注选择偏好
- `-.->|备选|` 虚线标注备选方案
- 整体结构：共同输入 → 多方案对比 → 选择结果
