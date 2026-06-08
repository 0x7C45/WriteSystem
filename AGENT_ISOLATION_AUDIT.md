# Agent 工作区隔离检查报告

> 审查时间: 2026-06-06
> 审查范围: 8 个核心 Agents + 4 个 Thesis Agents
> 目标: 确保每个 Agent 只在规定的工作区内完成任务，无上下文泄露风险

---

## 一、工作区隔离原则

### 1.1 隔离的重要性

**为什么需要工作区隔离？**
- 防止 Agent 访问不该访问的文件（如：Phase 2 访问 Phase 3 的终审结果）
- 防止上下文泄露（如：paper-advisor 的审查意见被 paper-copilot 提前看到）
- 确保管线顺序执行（Phase N 不能依赖 Phase N+1 的输出）
- 避免循环依赖（Agent A 读取 Agent B 的输出，Agent B 又读取 Agent A 的输出）

### 1.2 预期的工作区划分

```
Phase 0: paper-order-analyst
  工作区: 00_订单信息/, 01_格式模板/, 02_工作素材/raw/
  只读区: 无
  禁止区: 03-06/ (后续阶段目录)

Phase 1a: paper-literature-agent
  工作区: 04_参考文献/
  只读区: 00_订单信息/订单摘要.md
  禁止区: 03_计划与方案/, 05-06/ (后续阶段目录)

Phase 1b: paper-researcher
  工作区: 03_计划与方案/
  只读区: 00_订单信息/, 04_参考文献/literature_cards/
  禁止区: 05-06/ (后续阶段目录)

Phase 2: paper-copilot
  工作区: 05_撰写过程/
  只读区: 00-04/ (前置阶段目录)
  禁止区: 06_最终交付/ (后续阶段目录)

Phase 3: paper-formatter
  工作区: 06_最终交付/
  只读区: 00-05/ (前置阶段目录)
  禁止区: 无 (最后阶段)

跨阶段 Agents:
  paper-content-reviewer: 只读所有目录，不写入任何目录
  paper-data-auditor: 只读所有目录，不写入任何目录
  paper-advisor: 只读所有目录，写入审查报告到各阶段目录
```

---

## 二、核心 Agents 工作区审查

### 2.1 paper-order-analyst ✅ 隔离良好

**定义文件**: `tools/agent/paper-order-analyst.md`

**声明的工作区**:
- ✅ 输入: `00_订单信息/原始资料/`
- ✅ 输出: `00_订单信息/`, `01_格式模板/`, `02_工作素材/`, `03_计划与方案/论文撰写计划输入.md`

**访问权限审查**:
- ✅ **只读**: 用户提供的原始资料（`00_订单信息/原始资料/`）
- ✅ **写入**: 订单摘要、格式规范、原始资料索引、项目目录初始化
- ✅ **禁止访问**: 04-06/ (后续阶段目录)

**上下文泄露风险**: ✅ **无**
- 原因: Phase 0 是第一个阶段，没有前置依赖
- 后续阶段的文件在 Phase 0 执行时尚不存在

**隔离质量**: ✅ **优秀**
- 工作区边界清晰（00-03/）
- 不会访问后续阶段目录
- 只初始化目录结构，不预填充内容

---

### 2.2 paper-literature-agent ✅ 隔离良好

**定义文件**: `tools/agent/paper-literature-agent.md`

**声明的工作区**:
- ✅ 输入: `00_订单信息/订单摘要.md`（只读）
- ✅ 输出: `04_参考文献/literature_cards/`, `04_参考文献/literature_cards/_索引卡汇总.md`

**访问权限审查**:
- ✅ **只读**: 订单摘要（提取关键词和学科领域）
- ✅ **写入**: 文献索引卡、索引卡汇总
- ✅ **禁止访问**: 03_计划与方案/, 05-06/ (并行阶段和后续阶段)

**上下文泄露风险**: ✅ **无**
- 原因: Phase 1a 与 Phase 1b 并行，不能互相读取对方输出
- 定义明确说明：不访问 Phase 1b 的研究规划文件

**隔离质量**: ✅ **优秀**
- 工作区单一（04_参考文献/）
- 只读取订单摘要，不访问其他阶段文件
- 与 Phase 1b 并行但不互相依赖

---

### 2.3 paper-researcher ⚠️ 需要明确只读范围

**定义文件**: `tools/agent/paper-researcher.md`

**声明的工作区**:
- ⚠️ 输入: Phase 1a 的索引卡（未明确只读路径）
- ✅ 输出: `03_计划与方案/` (开题报告、骨架大纲、核心论点摘要)

**访问权限审查**:
- ⚠️ **只读**: 定义中说"Phase 1a 的索引卡"，但未明确路径
  - 应明确为: `04_参考文献/literature_cards/` (只读)
  - 应明确为: `00_订单信息/订单摘要.md` (只读)
- ✅ **写入**: 研究规划文件（`03_计划与方案/`）
- ✅ **禁止访问**: 05-06/ (后续阶段)

**上下文泄露风险**: ⚠️ **低风险**
- 潜在问题: 如果 researcher 访问 Phase 2 的草稿（05_撰写过程/），会造成循环依赖
- 但定义中明确说"Phase 1b 完成后才进入 Phase 2"，所以 05/ 目录在 Phase 1b 时应该为空

**建议改进**:
- 在 paper-researcher.md 中明确添加"只读区"和"禁止区"声明：
  ```markdown
  ## 工作区权限
  - 只读: 00_订单信息/, 04_参考文献/literature_cards/
  - 写入: 03_计划与方案/
  - 禁止: 05_撰写过程/, 06_最终交付/
  ```

**隔离质量**: ⚠️ **良好（需文档完善）**
- 实际行为应该是隔离的，但定义不够明确
- 建议补充明确的权限声明

---

### 2.4 paper-copilot ✅ 隔离良好

**定义文件**: `tools/agent/paper-copilot.md`

**声明的工作区**:
- ✅ 输入: `03_计划与方案/骨架大纲.md`, `04_参考文献/literature_cards/`, `02_工作素材/data_facts.json`
- ✅ 输出: `05_撰写过程/` (各章草稿、正文草稿、引用注册表)

**访问权限审查**:
- ✅ **只读**: 00-04/ (前置阶段目录)
  - 订单摘要（字数要求）
  - 骨架大纲（段落要点）
  - 文献索引卡（引用来源）
  - 数据事实库（实验数据）
- ✅ **写入**: 05_撰写过程/ (章节文件)
- ✅ **禁止访问**: 06_最终交付/ (后续阶段)

**上下文泄露风险**: ✅ **无**
- 原因: Phase 2 只读取前置阶段的输出，不访问后续阶段
- 入口条件明确要求 M1/M2 通过，确保前置阶段完整

**隔离质量**: ✅ **优秀**
- 工作区边界清晰（05_撰写过程/）
- 只读前置阶段，不访问后续阶段
- 依赖关系明确（search_blocks, query_data_facts 都是只读操作）

---

### 2.5 paper-formatter ✅ 隔离良好

**定义文件**: `tools/agent/paper-formatter.md`

**声明的工作区**:
- ✅ 输入: 05_撰写过程/正文草稿.md, 00_订单信息/格式规范.md, 01_格式模板/, 04_参考文献/
- ✅ 输出: 06_最终交付/ (最终 DOCX、校验报告)

**访问权限审查**:
- ✅ **只读**: 00-05/ (所有前置阶段目录)
  - 格式规范（排版标准）
  - 格式模板（DOCX 模板）
  - 正文草稿（待排版内容）
  - 文献索引卡（参考文献列表）
- ✅ **写入**: 06_最终交付/ (最终输出)
- ✅ **禁止访问**: 无（Phase 3 是最后阶段）

**上下文泄露风险**: ✅ **无**
- 原因: Phase 3 是最后阶段，不存在后续阶段可泄露
- 入口条件明确要求 M3 通过，确保前置阶段完整

**隔离质量**: ✅ **优秀**
- 工作区边界清晰（06_最终交付/）
- 可以读取所有前置阶段（合理需求，因为是终审阶段）
- 不会影响其他阶段的文件

---

### 2.6 paper-advisor ⚠️ 需要评估审查报告位置

**定义文件**: `tools/agent/paper-advisor.md`

**声明的工作区**:
- ✅ 输入: 各阶段的输出文件（只读）
- ⚠️ 输出: 审查报告（位置未明确）

**访问权限审查**:
- ✅ **只读**: 所有阶段目录（M1-M4 需要审查不同阶段的输出）
  - M1: 03_计划与方案/, 04_参考文献/
  - M2: 03_计划与方案/骨架大纲.md
  - M3: 05_撰写过程/正文草稿.md
  - M4: 06_最终交付/
- ⚠️ **写入**: 审查报告位置未明确
  - 应该写入到被审查阶段的目录？（如：M1 报告 → 03_计划与方案/_M1_审查报告.md）
  - 还是统一写入到项目根目录？（如：_ADVISOR_REPORTS/M1.md）

**上下文泄露风险**: ⚠️ **低风险**
- 潜在问题: 如果审查报告写入到被审查阶段的目录，后续 Agent 可能读到
  - 例如：M1 报告写入 03_计划与方案/_M1_审查报告.md，paper-copilot 可能读取并"学习"如何通过审查
- 建议: 审查报告应该写入到项目根目录或单独的 `_REVIEWS/` 目录，不与各阶段目录混合

**建议改进**:
- 在 paper-advisor.md 中明确审查报告的存放位置
- 建议: 创建 `_REVIEWS/` 目录，存放所有里程碑审查报告
  - `_REVIEWS/M1_方向确认.md`
  - `_REVIEWS/M2_骨架确认.md`
  - `_REVIEWS/M3_草稿审查.md`
  - `_REVIEWS/M4_交付确认.md`
- 在各 Agent 定义中明确禁止读取 `_REVIEWS/` 目录（防止提前看到审查意见）

**隔离质量**: ⚠️ **良好（需文档完善）**
- 只读权限合理（审查需要读取所有阶段）
- 写入位置需要明确，避免上下文泄露

---

### 2.7 paper-content-reviewer ✅ 隔离良好

**定义文件**: `tools/agent/paper-content-reviewer.md`

**声明的工作区**:
- ✅ 输入: 被审查的文件（只读）
- ✅ 输出: 审查意见（返回给调用者，不写入文件）

**访问权限审查**:
- ✅ **只读**: 被审查的具体文件（由调用者指定）
  - 不主动扫描整个项目
  - 只审查传入的具体文件或段落
- ✅ **写入**: 无（审查意见通过 Gate 返回，不写入磁盘）
- ✅ **禁止访问**: 无特定禁止区（因为只读且由调用者控制）

**上下文泄露风险**: ✅ **无**
- 原因: content-reviewer 是被动调用，不主动访问文件
- 审查意见通过 Gate 返回，不持久化到磁盘

**隔离质量**: ✅ **优秀**
- 完全被动审查，无主动访问
- 不写入任何文件，无持久化风险
- 由调用者控制审查范围

---

### 2.8 paper-data-auditor ✅ 隔离良好

**定义文件**: `tools/agent/paper-data-auditor.md`

**声明的工作区**:
- ✅ 输入: `02_工作素材/data_facts.json`, 被审查的文件（只读）
- ✅ 输出: 审查意见（返回给调用者，不写入文件）

**访问权限审查**:
- ✅ **只读**: data_facts.json + 被审查的具体文件
  - 不主动扫描整个项目
  - 只审查传入的数据引用
- ✅ **写入**: 无（审查意见通过 Gate 返回）
- ✅ **禁止访问**: 无特定禁止区（因为只读且由调用者控制）

**上下文泄露风险**: ✅ **无**
- 原因: data-auditor 是被动调用，不主动访问文件
- 审查意见通过 Gate 返回，不持久化到磁盘

**隔离质量**: ✅ **优秀**
- 完全被动审查，无主动访问
- 不写入任何文件，无持久化风险
- 由调用者控制审查范围

---

## 三、Thesis Agents 工作区审查

### 3.1 thesis-chapter-stitcher ❌ 外部路径引用

**定义文件**: `tools/agent/thesis-chapter-stitcher.md` (695 bytes)

**问题**:
```
引用了外部路径: /Users/arco/Desktop/.../AGENT_WORKER_PROTOCOL.md
```

**影响**:
- ❌ 其他用户无法使用（路径硬编码）
- ❌ 不在 WriteSystem 主管线中（独立流程）

**建议**: 标记为独立流程，移到 `tools/agents/thesis.INDEPENDENT/` 或修复路径引用

---

### 3.2 thesis-ledger-auditor ❌ 外部路径引用

**定义文件**: `tools/agent/thesis-ledger-auditor.md` (821 bytes)

**问题**: 同 thesis-chapter-stitcher

---

### 3.3 thesis-shard-rewriter ❌ 外部路径引用

**定义文件**: `tools/agent/thesis-shard-rewriter.md` (762 bytes)

**问题**: 同 thesis-chapter-stitcher

---

### 3.4 thesis-shard-validator ❌ 外部路径引用

**定义文件**: `tools/agent/thesis-shard-validator.md` (725 bytes)

**问题**: 同 thesis-chapter-stitcher

---

## 四、上下文泄露风险总结

### 4.1 已识别的风险点

| Agent | 风险类型 | 严重程度 | 建议修复 |
|-------|---------|---------|---------|
| paper-researcher | 只读范围未明确 | 🟡 低 | 补充文档，明确只读/禁止区 |
| paper-advisor | 审查报告位置未明确 | 🟡 低 | 创建 `_REVIEWS/` 目录，禁止其他 Agent 读取 |
| thesis-* agents | 外部路径引用 | 🔴 高 | 修复路径或标记为独立流程 |

### 4.2 零风险的 Agents

- ✅ paper-order-analyst — 第一阶段，无前置依赖
- ✅ paper-literature-agent — 工作区单一，不访问并行阶段
- ✅ paper-copilot — 只读前置，不访问后续
- ✅ paper-formatter — 最后阶段，无后续依赖
- ✅ paper-content-reviewer — 被动审查，无主动访问
- ✅ paper-data-auditor — 被动审查，无主动访问

---

## 五、建议的改进措施

### 5.1 文档完善（高优先级）

**1. 在每个 Agent 定义中添加"工作区权限"章节**

```markdown
## 工作区权限

### 只读区
- 00_订单信息/ — 订单摘要、格式规范
- 04_参考文献/literature_cards/ — 文献索引卡

### 写入区
- 03_计划与方案/ — 研究规划文件

### 禁止区
- 05_撰写过程/ — 后续阶段，禁止提前访问
- 06_最终交付/ — 后续阶段，禁止提前访问
- _REVIEWS/ — 审查报告，禁止读取
```

**适用 Agent**: paper-researcher, paper-advisor

---

**2. 创建 `_REVIEWS/` 目录存放审查报告**

```bash
mkdir -p projects/{project_name}/_REVIEWS/
```

**paper-advisor 写入审查报告到**:
- `_REVIEWS/M1_方向确认.md`
- `_REVIEWS/M2_骨架确认.md`
- `_REVIEWS/M3_草稿审查.md`
- `_REVIEWS/M4_交付确认.md`

**其他 Agent 禁止读取 `_REVIEWS/` 目录**

---

### 5.2 架构完善（中优先级）

**3. 在 scaffold.sh 中自动创建 `_REVIEWS/` 目录**

```bash
# scripts/scaffold.sh 中添加
mkdir -p "$PROJECT_DIR/_REVIEWS"
echo "# 里程碑审查报告" > "$PROJECT_DIR/_REVIEWS/README.md"
```

---

**4. 在 pipeline-spec.md 中明确工作区隔离原则**

```markdown
## 工作区隔离原则

每个 Agent 只能访问规定的工作区：

| Agent | 只读区 | 写入区 | 禁止区 |
|-------|-------|-------|-------|
| paper-order-analyst | 00_订单信息/原始资料/ | 00-03/ | 04-06/ |
| paper-literature-agent | 00_订单信息/ | 04_参考文献/ | 03/, 05-06/ |
| paper-researcher | 00/, 04/ | 03_计划与方案/ | 05-06/, _REVIEWS/ |
| paper-copilot | 00-04/ | 05_撰写过程/ | 06/, _REVIEWS/ |
| paper-formatter | 00-05/ | 06_最终交付/ | _REVIEWS/ |
| paper-advisor | 00-06/ | _REVIEWS/ | 无 |
| paper-content-reviewer | 被调用时的文件 | 无 | 无 |
| paper-data-auditor | 02/, 被调用时的文件 | 无 | 无 |
```

---

### 5.3 Thesis Agents 处理（低优先级）

**5. 修复 thesis-* agents 的外部路径引用**

选项 A: 修复路径
```markdown
# 将硬编码路径改为相对路径
- 旧: /Users/arco/Desktop/.../AGENT_WORKER_PROTOCOL.md
- 新: tools/agent/thesis/_PROTOCOL.md
```

选项 B: 标记为独立流程
```bash
mkdir -p tools/agent/thesis.INDEPENDENT/
mv tools/agent/thesis-*.md tools/agent/thesis.INDEPENDENT/
```

---

## 六、验证方法

### 6.1 静态验证（文档审查）

✅ **已完成** — 本报告已审查所有 Agent 定义文件

### 6.2 动态验证（运行时检测）

**建议**: 在 MCP 工具中添加工作区权限检查

```python
# 伪代码
def check_agent_permission(agent_name, file_path, access_type):
    allowed_zones = AGENT_PERMISSIONS[agent_name][access_type]
    if not any(file_path.startswith(zone) for zone in allowed_zones):
        raise PermissionError(f"{agent_name} 不允许 {access_type} {file_path}")
```

**触发时机**: 每次 Agent 调用文件操作工具时

---

## 七、总结

### 7.1 整体隔离质量

```
核心 Agents 隔离质量: ✅✅✅✅✅⚠️⚠️ (5 优秀 + 2 需完善)
  - paper-order-analyst: ✅ 优秀
  - paper-literature-agent: ✅ 优秀
  - paper-researcher: ⚠️ 良好（需文档完善）
  - paper-copilot: ✅ 优秀
  - paper-formatter: ✅ 优秀
  - paper-advisor: ⚠️ 良好（需文档完善）
  - paper-content-reviewer: ✅ 优秀
  - paper-data-auditor: ✅ 优秀

Thesis Agents 隔离质量: ❌❌❌❌ (4 个需修复)
  - 全部存在外部路径引用问题
  - 不在主管线中，属于独立流程
```

### 7.2 风险评估

**当前风险等级**: 🟡 **低**

- ✅ 主管线（Phase 0-3.5）的核心 Agents 隔离良好
- ⚠️ 存在 2 个需要文档完善的点（paper-researcher, paper-advisor）
- ❌ Thesis Agents 有外部路径问题，但不影响主管线

**推荐行动**:
1. **立即执行**: 补充 paper-researcher 和 paper-advisor 的工作区权限文档
2. **高优先级**: 创建 `_REVIEWS/` 目录，隔离审查报告
3. **中优先级**: 更新 pipeline-spec.md，添加工作区隔离原则表格
4. **低优先级**: 修复 thesis-* agents 的外部路径引用

### 7.3 结论

✅ **WriteSystem 主管线的 Agent 工作区隔离设计合理，无严重上下文泄露风险。**

- 8 个核心 Agent 中，5 个隔离优秀，2 个需文档完善但实际行为合理，1 个需明确审查报告位置
- 各 Agent 的只读/写入边界清晰，Phase 顺序执行确保无循环依赖
- 跨阶段审查 Agents（content-reviewer, data-auditor）采用被动调用模式，无主动访问风险

**建议执行"文档完善"改进措施后，隔离质量可达 100%。**

---

**报告完成时间**: 2026-06-06
**下一步**: 执行文档完善措施（补充工作区权限声明 + 创建 _REVIEWS/ 目录）
