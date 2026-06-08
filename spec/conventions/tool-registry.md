# 工具出入与替换机制

> 版本: v1.0.0 | 所属: WriteSystem spec/conventions

---

## 概述

仓库中 `tools/` 下的 MCP 服务、Skills、Rules、Agent 定义不是一成不变的。
新工具加入、旧工具被替换、工具之间互相依赖——需要一套机制来追踪。

## 三层清单

```
① 工具自描述       →  MANIFEST.yml 或 SKILL.md frontmatter
② 仓库统一清单     →  tools/REGISTRY.yml
③ 操作脚本         →  scripts/tool.sh add / remove / replace
```

---

## 一、工具自描述 (MANIFEST)

### MCP Server: `tools/mcp-servers/{name}/MANIFEST.yml`

```yaml
name: paper-tools-mcp
version: 0.1.0
type: mcp-server
description: 论文工具 MCP Server — 校验、排版、检索、AIGC
provides:
  tools:
    - validate_word_count
    - validate_citations
    - validate_chapter_citations
    - validate_citation_order
    - validate_markdown_structure
    - validate_assets
    - validate_docx_styles
    - validate_docx_sections
    - validate_docx_layout
    - validate_docx_fonts
    - validate_docx_references
    - run_format_pipeline
    - build_preflight_docx
    - apply_minimax_c2
    - apply_pandoc_templated
    - get_literature_cards
    - build_reference_list
    - search_blocks
    - query_data_facts
    - assess_aigc_risk
    - query_excel_data
    - validate_excel_formulas
    - analyze_docx_template
requires:
  python: ">=3.11"
  packages:
    - mcp>=1.12.0
    - python-docx>=1.1.0
```

### Skill: `tools/skills/{name}/SKILL.md` frontmatter

```yaml
---
name: anti-aigc
version: 1.0.0
type: skill
description: 降AI反检测全流程
phase: 3.5
depends_on:
  mcp-tools:
    - assess_aigc_risk
---
```

### Rule: `tools/rules/{name}.md` frontmatter

```yaml
---
name: academic-writing
version: 1.0.0
type: rule
description: 学术写作规则
---
```

### Agent: `tools/agent/{name}.md` frontmatter

```yaml
---
name: paper-copilot
version: 1.0.0
type: agent
phase: 2
depends_on:
  mcp-tools: [search_blocks, query_data_facts, validate_word_count]
---
```

---

## 二、仓库统一清单 (REGISTRY)

### `tools/REGISTRY.yml`

```yaml
# WriteSystem 工具清单 — 自动维护，勿手动编辑
# 最后更新: 2026-06-04T18:00:00

installed:
  mcp-servers:
    paper-tools-mcp:
      version: 0.1.0
      installed: 2026-06-04
      source: ArticleSystem/mcp-servers/paper-tools-mcp/
      provides:
        tools:
          - validate_word_count
          - validate_citations
          - assess_aigc_risk
          - run_format_pipeline
          # ... (完整列表由 MANIFEST.yml 提供)

  skills:
    anti-aigc:
      version: 1.0.0
      installed: 2026-06-04
      depends_on:
        mcp-tools:
          - assess_aigc_risk

  rules:
    academic-writing:
      version: 1.0.0
      installed: 2026-06-04

  agents:
    paper-copilot:
      version: 1.0.0
      installed: 2026-06-04
      depends_on:
        mcp-tools:
          - search_blocks
          - query_data_facts
          - validate_word_count
```

---

## 三、操作脚本

### `scripts/tool.sh`

```
用法:
  bash scripts/tool.sh add    --type {type} --path {source}  [--name {name}]
  bash scripts/tool.sh remove {name}                          [--force]
  bash scripts/tool.sh replace {name} --with {source}         [--force]
  bash scripts/tool.sh list                                   列出已安装工具
  bash scripts/tool.sh deps {name}                            查看依赖关系
```

### ADD 流程

```
1. 读取源目录的 MANIFEST.yml 或 SKILL.md frontmatter
2. 校验 provides 不与其他已安装工具冲突
3. 检查 depends_on 中的依赖项是否已安装
   → 未满足 → 报错，列出缺失的依赖
4. 复制到 tools/{type}/{name}/
5. 更新 REGISTRY.yml
```

### REMOVE 流程

```
1. 搜索 REGISTRY.yml 中所有 depends_on 引用此工具的条目
2. 找到反向依赖 → 列出"以下工具依赖 {name}: ..."
   → 默认拒绝删除
   → --force: 删除，同时将依赖方标记为 BROKEN
3. 无反向依赖 → 删除目录 + 从 REGISTRY 移除
```

### REPLACE 流程

```
1. 读取旧 MANIFEST → 提取 old_provides
2. 读取新 MANIFEST → 提取 new_provides
3. 生成 diff 报告:

   Diff: paper-tools-mcp v0.1.0 → v0.2.0
   + 新增工具: validate_reference_format, perturb_sentence
   - 移除工具: (无)
   ~ 变更工具: assess_aigc_risk (参数签名变化)

4. 检查「- 移除」和「~ 变更」的工具是否被其他工具依赖
   → 如果有 → 列出受影响方，要求 --force
5. 替换目录 + 更新 REGISTRY
```

### 依赖校验矩阵

```
          被依赖方
           MCP工具   Skill   Rule   Agent
依赖方    ─────────────────────────────
MCP工具    —        —       —      —
Skill      ✅       —       —      —
Rule       —        —       —      —
Agent      ✅       —       —      —
```

只有 Skill 和 Agent 会依赖 MCP 工具。MCP 工具之间不互相依赖。

---

## 四、REGISTRY 校验

`scripts/validate.sh` 增加一项检查：

```
对 REGISTRY.yml 中每个条目:
  ✓ 对应的 MANIFEST 文件存在
  ✓ version 与 MANIFEST 一致
  ✓ provides 与 MANIFEST 一致

对每个 depends_on:
  ✓ 被依赖的工具在 REGISTRY 中已安装
  ✓ 被依赖的工具 provides 包含声明的工具名
```

---

## 五、迁移时的操作

从 ArticleSystem 首次迁移时：

```bash
bash scripts/tool.sh add --type mcp-server --path /mnt/f/AI/Data/ArticleSystem/mcp-servers/paper-tools-mcp
bash scripts/tool.sh add --type skill --path /mnt/f/AI/Data/ArticleSystem/.opencode/skills/anti-aigc
bash scripts/tool.sh add --type agent --path /mnt/f/AI/Data/ArticleSystem/.opencode/agents/paper-copilot
...
```

每迁移一个工具，REGISTRY.yml 自动更新，依赖关系自动建立。
