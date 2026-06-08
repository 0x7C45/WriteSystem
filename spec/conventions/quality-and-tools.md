# 质量量化标准与 MCP 工具契约

> 版本: v1.0.0 | 所属: WriteSystem spec/conventions
> 关联: pipeline-spec.md（管线流程）、source-materials.md（素材规范）

---

# 第一部分：质量量化标准

## 一、字数标准

### 1.1 总字数

| 论文类型 | 目标字数 (中文字符) | 下限 | 上限 | 容忍度 |
|---------|-------------------|------|------|--------|
| 本科毕业论文 | 15000 | 12000 | 20000 | ±20% 内 PASS，超出 WARN |
| 硕士毕业论文 | 30000 | 25000 | 40000 | ±15% 内 PASS，超出 WARN |
| 期刊论文 | 8000 | 6000 | 10000 | ±25% 内 PASS |
| 课程论文 | 3500 | 2800 | 4500 | ±20% 内 PASS |
| 开题报告 | 3000 | 2000 | 5000 | — |

判定规则：
- 在 [下限, 上限] 内 → **PASS**
- 低于下限 → **REVISE**（Chapter 标注为字数不足）
- 高于上限 → **WARN**（提示精简，不阻止交付）

### 1.2 章节字数分布

| 章节 | 占比目标 | 容忍度 |
|------|---------|--------|
| 绪论 | 10-15% | ±5% |
| 文献综述/理论基础 | 15-25% | ±5% |
| 方法/设计 | 15-25% | ±5% |
| 实验/分析 | 25-35% | ±5% |
| 结论 | 5-10% | ±3% |

任何章节低于目标占比下限 10 个百分点 → **REVISE**。

### 1.3 摘要字数

| 类型 | 中文摘要 | 英文摘要 |
|------|---------|---------|
| 毕业论文 | 300-500 字 | 150-250 words |
| 期刊论文 | 200-300 字 | 100-200 words |
| 课程论文 | 150-250 字 | — |

---

## 二、引用标准

### 2.1 文献数量下限

| 论文类型 | 中文文献 | 英文文献 | 总计下限 |
|---------|---------|---------|---------|
| 本科毕业论文 | ≥8 | ≥5 | ≥15 |
| 硕士毕业论文 | ≥15 | ≥15 | ≥30 |
| 期刊论文 | — | — | ≥20 |
| 课程论文 | — | — | ≥8 |

### 2.2 引用密度

| 指标 | 标准 | 判定 |
|------|------|------|
| 引用/千字 | ≥ 1.5 条/千字 | 低于 → WARN |
| 近 5 年文献占比 | ≥ 50% | 低于 → WARN |
| 综述章节引用密度 | ≥ 3 条/千字 | 低于 → REVISE |
| 单篇文献引用次数 | ≤ 5 次 | 超过 → WARN（避免过度依赖） |

### 2.3 引用格式合规

| 检查项 | 标准 |
|--------|------|
| 文中引用标记 | [N] 或 (Author, Year)，全文一致 |
| 参考文献列表 | 按引用顺序排列，编号连续 |
| DOI/URL 可访问 | 随机抽查 20%，至少 80% 可访问 |
| 自引比例 | ≤ 20% |

---

## 三、AIGC 风险标准

### 3.1 检测阈值

| 检测器 | 低风险 | 中风险 | 高风险 |
|--------|--------|--------|--------|
| GPTZero | < 30% | 30-60% | > 60% |
| Originality.ai | < 20% | 20-50% | > 50% |
| 知网 AIGC 检测 | < 15% | 15-40% | > 40% |

### 3.2 触发规则

```
综合判定逻辑:
  任一检测器 → 高风险 → 立即触发 Phase 3.5
  两个及以上检测器 → 中风险 → 触发 Phase 3.5
  全部检测器 → 低风险 → PASS

段落级:
  单段落 > 高风险阈值 → 该段落必须处理
  连续 3 段 > 中风险阈值 → 该区域必须处理
```

### 3.3 迭代终止条件

```
Phase 3.5 最多迭代 3 轮
  第 1 轮后：至少 50% 的高风险段落降为中风险
  第 2 轮后：至少 80% 的高风险段落降为中风险
  第 3 轮后：全部高风险段落降至低风险
  3 轮后仍有高风险段落 → 标记为人工复核，附带处理记录
```

---

## 四、格式标准

### 4.1 DOCX 样式检查

| 检查项 | 标准 | 不通过后果 |
|--------|------|-----------|
| 正文样式 | 与模板定义一致 | REVISE |
| 标题样式 (1-3级) | 与模板定义一致 | REVISE |
| 字体嵌入 | 中文字体已嵌入 | REVISE |
| 页码 | 摘要用罗马，正文用阿拉伯 | REVISE |
| 目录 | 自动生成且页码正确 | WARN |
| 图表编号 | 按章连续，无跳号 | REVISE |

### 4.2 Markdown 结构

| 检查项 | 标准 |
|--------|------|
| 标题层级 | 不跳级（无 H1→H3 跳跃） |
| 表格语法 | 每行列数一致，无未闭合 |
| 图片路径 | 指向存在的文件 |
| 代码块 | 有语言标注，正确闭合 |

---

## 五、数据质量标准

### 5.1 data-auditor 审查 Checklist

| 审查项 | 具体检查 |
|--------|---------|
| 数据来源 | 文中数据可追溯到 data_facts.md |
| 数值一致性 | 同一变量在不同章节中数值一致 |
| 百分比总和 | 所有百分比组件之和 = 100%（±1% 容忍） |
| 统计显著 | 提到"显著"时必须有 p 值或检验统计量 |
| 单位一致性 | 同一变量全文使用相同单位 |
| 精度一致性 | 同一变量全文保留相同小数位数 |
| 无捏造 | 不在 data_facts.md 中的数字标记为可疑 |

### 5.2 图表标准

| 指标 | 标准 |
|------|------|
| 图表总数 | ≥ 3（课程论文）；≥ 8（本科论文）；≥ 15（硕士论文） |
| 分辨率 | ≥ 150 DPI |
| 文字可读性 | 图表内文字 ≥ 8pt |
| 配色 | 灰度可打印（非彩色依赖） |

---

# 第二部分：MCP 工具契约

> 以下 23 个工具归属于 `mcp-servers/paper-tools-mcp/`

---

## 工具 1: validate_word_count

```
用途: 统计 Markdown 文件的字数（中文字符 + 英文单词）
调用方: copilot (Phase 2), formatter (Phase 3)

输入:
  path: string           — Markdown 文件路径
  target: int (可选)      — 目标字数，传入则做对比
  chapter: string (可选)  — 章节标识，传入则输出章节级统计

输出:
  {
    total_chars: int,        // 中文字符数
    total_words: int,        // 英文单词数
    total_equivalent: int,   // 等效中文字数 (chars + words*2)
    sections: [              // 按章节分段统计(如果传入 chapter)
      {heading: str, chars: int, words: int}
    ],
    verdict: "PASS" | "WARN" | "REVISE",
    deviation: "+5.2%"       // 与目标的偏差
  }

阈值: 见本规范第一部分的「字数标准」
```

---

## 工具 2: validate_citations

```
用途: 验证正文中所有引用标记是否有对应的文献索引卡
调用方: copilot (Phase 2), formatter (Phase 3)

输入:
  manuscript_path: string   — 正文 Markdown 路径
  cards_dir: string         — 索引卡目录路径

输出:
  {
    total_citations: int,          // 引用标记总数
    unique_cite_keys: int,         // 去重后的引用文献数
    missing: [                      // 无索引卡的引用
      {cite_key: str, location: str}
    ],
    unused_cards: [str],           // 有索引卡但未被引用的文献
    density_per_1k: float,         // 引用密度
    verdict: "PASS" | "WARN" | "REVISE"
  }

阈值: 无索引卡的引用数 > 0 → REVISE
```

---

## 工具 3: validate_chapter_citations

```
用途: 单章引用检查（Phase 2 每章写完后调用）
调用方: copilot (Phase 2)

输入:
  chapter_path: string     — 章节 Markdown 路径
  cards_dir: string        — 索引卡目录

输出:
  {
    chapter_citations: int,
    new_citations: [str],        // 本章首次出现的引用
    cross_refs: [str],           // 引用其他章节的数据/结论
    verdict: "PASS" | "REVISE"
  }
```

---

## 工具 4: validate_citation_order

```
用途: 验证参考文献列表的排列顺序
调用方: formatter (Phase 3)

输入:
  manuscript_path: string   — 含参考文献的正文
  order: string             — "appearance" | "alphabetical"

输出:
  {
    order_correct: bool,
    out_of_order: [{expected_pos: int, actual_pos: int, ref: str}],
    verdict: "PASS" | "REVISE"
  }
```

---

## 工具 5: validate_markdown_structure

```
用途: 检查 Markdown 语法和结构
调用方: formatter (Phase 3)

输入:
  path: string — Markdown 文件路径

输出:
  {
    heading_hierarchy_valid: bool,    // 标题不跳级
    heading_levels: [{level: int, text: str, line: int}],
    table_errors: [{line: int, issue: str}],
    code_blocks: int,
    unclosed_code_blocks: int,
    image_refs: [{line: int, path: str, exists: bool}],
    broken_links: [{line: int, target: str}],
    verdict: "PASS" | "REVISE"
  }
```

---

## 工具 6: validate_assets

```
用途: 检查正文中引用的所有外部文件（图片、附件）是否存在
调用方: formatter (Phase 3)

输入:
  manuscript_path: string

输出:
  {
    total_refs: int,
    missing: [{ref: str, line: int}],
    orphan_files: [str],         // 存在于素材目录但未被引用的文件
    verdict: "PASS" | "REVISE"
  }
```

---

## 工具 7-11: DOCX 校验系列

### validate_docx_styles

```
输入: docx_path, template_path
输出: {style_mismatches: [{style_name, expected, actual}], verdict}
```

### validate_docx_sections

```
输入: docx_path
输出: {sections: [{type, page_number, correct}], verdict}
```

### validate_docx_layout

```
输入: docx_path, template_path
输出: {margin_errors, line_spacing_errors, header_footer_errors, verdict}
```

### validate_docx_fonts

```
输入: docx_path
输出: {fonts_used: [str], missing_embed: [str], cn_en_mixed_issues: [str], verdict}
```

### validate_docx_references

```
输入: docx_path
输出: {format_errors: [{ref_num, issue}], order_correct: bool, verdict}
```

---

## 工具 12: run_format_pipeline

```
用途: 排版主控管道。选择 C-2 或 pandoc 路线并执行
调用方: formatter (Phase 3)
★ 100% 代码管道，禁止 LLM 自行排版

输入:
  source: string              — Markdown 源文件
  template: string            — 格式模板 .docx
  output: string              — 目标 .docx 路径
  preferred_method: string    — "minimax_c2" | "pandoc" | "auto"

输出:
  {
    method_used: string,           // 实际使用的方法
    output_path: string,           // 生成的 docx 路径
    fallback_triggered: bool,      // 是否触发了降级
    fallback_reason: string|null,
    warnings: [str],
    duration_seconds: float
  }

内部逻辑:
  auto 模式 → 先尝试 apply_minimax_c2 → 失败/PANIC →
              apply_pandoc_templated → 失败 →
              返回错误（不可自动恢复）
```

---

## 工具 13: build_preflight_docx

```
用途: 预览排版 — 生成不带最终格式的临时 docx 供检查
调用方: formatter (Phase 3)

输入: source, template, output
输出: {output_path, preflight_issues: [str]}
```

---

## 工具 14: apply_minimax_c2

```
用途: 使用 minimax-docx C-2 排版链生成 docx
调用方: run_format_pipeline

输入: source, template, output
输出: {output_path, applied_styles: [str], issues: [str]}
```

---

## 工具 15: apply_pandoc_templated

```
用途: 使用 pandoc + 参考模板生成 docx（fallback 路线）
调用方: run_format_pipeline

输入: source, template_docx, output
输出: {output_path, pandoc_version: str, issues: [str]}
```

---

## 工具 16: get_literature_cards

```
用途: 读取所有文献索引卡，返回结构化数据
调用方: formatter (Phase 3)

输入:
  cards_dir: string

输出:
  {
    cards: [{
      cite_key: str,
      title: str,
      authors: str,
      year: int,
      source: str,
      doi: str,
      relation: str
    }],
    total: int
  }
```

---

## 工具 17: build_reference_list

```
用途: 从索引卡生成格式化的参考文献列表
调用方: formatter (Phase 3)

输入:
  cards_dir: string
  cited_keys: [str]           // 只输出被引用的
  format: string              // "gbt7714" | "apa" | "ieee"
  order: string               // "appearance" | "alphabetical"

输出:
  {
    reference_list: str,           // Markdown 格式的参考文献列表
    uncited_cards: [str],          // 未被引用的索引卡
    format_warnings: [str]
  }
```

---

## 工具 18: search_blocks

```
用途: 在文献索引卡中搜索指定主题的内容块
调用方: copilot (Phase 2)

输入:
  keywords: [str]             // 搜索关键词
  cards_dir: string           // 索引卡目录
  limit: int (默认 5)         // 返回结果数

输出:
  {
    results: [{
      cite_key: str,
      card_file: str,
      relevance: float,           // 0-1
      snippet: str,               // 匹配段落
      context: str                // 前后文
    }]
  }
```

---

## 工具 19: query_data_facts

```
用途: 查询 data_facts.md 中的实验数据
调用方: copilot (Phase 2), data-auditor (Phase 2-3)

输入:
  query: string               // 自然语言或关键词查询
  data_facts_path: string     // data_facts.md 路径
  format: string (默认 "text")// "text" | "table" | "json"

输出:
  {
    matches: [{
      section: str,               // 数据集名称
      content: str,              // 匹配的数据内容
      raw_values: object|null     // 结构化数值 (format=json)
    }],
    total_datasets: int
  }
```

---

## 工具 20: assess_aigc_risk

```
用途: 评估文本的 AIGC 生成风险
调用方: formatter (Phase 3), anti-aigc skill (Phase 3.5)

输入:
  text: string                     // 待检测文本
  mode: string (默认 "full")       // "full" | "paragraph"
  detectors: [str] (默认 ["all"])  // "gptzero" | "originality" | "cnki" | "all"

输出:
  {
    overall_score: float,          // 0-1
    risk_level: "low" | "medium" | "high",
    detector_scores: {
      gptzero: float|null,
      originality: float|null,
      cnki: float|null
    },
    paragraph_scores: [{           // mode=paragraph 时
      paragraph_index: int,
      score: float,
      text_preview: str
    }],
    high_risk_paragraphs: [int],
    verdict: "PASS" | "TRIGGER_ANTI_AIGC",
    threshold_applied: float        // 当前使用的阈值
  }

阈值: 见本规范第一部分「AIGC 风险标准」
```

---

## 工具 21: query_excel_data

```
用途: 读取 Excel 文件中的数据
调用方: order-analyst (Phase 0), data-auditor

输入:
  file_path: string
  sheet: string|null
  range: string|null           // "A1:D20"
  output_format: string        // "markdown" | "json"

输出:
  {
    data: str|object,
    sheet_names: [str],
    row_count: int,
    col_count: int
  }
```

---

## 工具 22: validate_excel_formulas

```
用途: 检查 Excel 文件中的公式完整性和引用有效性
调用方: data-auditor

输入:
  file_path: string

输出:
  {
    total_formulas: int,
    broken_refs: [{sheet, cell, formula, issue}],
    circular_refs: [{sheet, cells}],
    verdict: "PASS" | "WARN"
  }
```

---

## 工具 23: analyze_docx_template

```
用途: 分析 Word 模板的结构
调用方: order-analyst (Phase 0)

输入:
  template_path: string

输出:
  {
    styles: [{
      name: str,
      type: str,              // "paragraph" | "character"
      font: str,
      font_size: float,       // pt
      bold: bool,
      alignment: str
    }],
    sections: [{
      page_size: str,
      margins: {top, bottom, left, right},
      header_distance: float,
      footer_distance: float
    }],
    numbering_definitions: [str],
    has_toc_field: bool,
    has_page_numbers: bool
  }
```

---

# 第三部分：工具-Phase 映射矩阵

| 工具 | Phase 0 | Phase 1a | Phase 1b | Phase 2 | Phase 3 | Phase 3.5 |
|------|---------|----------|----------|---------|---------|-----------|
| validate_word_count | | | | ● | ● | |
| validate_citations | | | | ● | ● | |
| validate_chapter_citations | | | | ● | | |
| validate_citation_order | | | | | ● | |
| validate_markdown_structure | | | | | ● | |
| validate_assets | | | | | ● | |
| validate_docx_styles | | | | | ● | |
| validate_docx_sections | | | | | ● | |
| validate_docx_layout | | | | | ● | |
| validate_docx_fonts | | | | | ● | |
| validate_docx_references | | | | | ● | |
| run_format_pipeline | | | | | ● | |
| build_preflight_docx | | | | | ● | |
| apply_minimax_c2 | | | | | ● | |
| apply_pandoc_templated | | | | | ● | |
| get_literature_cards | | | | | ● | |
| build_reference_list | | | | | ● | |
| search_blocks | | ● | | ● | | |
| query_data_facts | | | | ● | ● | |
| assess_aigc_risk | | | | | ● | ● |
| query_excel_data | ● | | | | ● | |
| validate_excel_formulas | | | | | ● | |
| analyze_docx_template | ● | | | | | |
