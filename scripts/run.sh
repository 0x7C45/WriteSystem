#!/bin/bash
# run.sh — 一句话启动完整论文撰写管线
# 用法: bash scripts/run.sh <材料目录> [--auto|--review] [--template <模板路径>]
# 示例: bash scripts/run.sh ~/Desktop/论文资料 --auto
#       bash scripts/run.sh ~/Desktop/论文资料 --review --template ~/模板.docx

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ============ 参数解析 ============

show_usage() {
    cat << EOF
用法: bash scripts/run.sh <材料目录> [选项]

参数:
  <材料目录>           包含所有参考文件的文件夹（PDF、DOCX、图片、MD等）

选项:
  --auto              全自动模式（默认）— 除非信息缺失否则不停止
  --review            中途审查模式 — 每个 Phase 结束后暂停汇报
  --template <路径>    指定格式模板文件（可选）
  --minimal           最小交互模式 — 仅订单确认和最终交付时停止
  --help              显示此帮助信息

模式说明:
  --auto     → interaction_level: minimal + revise_mode: auto
  --review   → interaction_level: coarse + revise_mode: manual
  --minimal  → interaction_level: minimal + revise_mode: auto（同 --auto）

示例:
  # 全自动模式，AI 一路执行到完成
  bash scripts/run.sh ~/Desktop/论文资料 --auto

  # 中途审查模式，每个 Phase 后停止询问
  bash scripts/run.sh ~/Desktop/论文资料 --review

  # 指定模板的全自动模式
  bash scripts/run.sh ~/Desktop/论文资料 --auto --template ~/学位论文模板.docx
EOF
}

# 默认值
MATERIALS_DIR=""
MODE="auto"  # auto | review
TEMPLATE_PATH=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            MODE="auto"
            shift
            ;;
        --review)
            MODE="review"
            shift
            ;;
        --minimal)
            MODE="auto"  # minimal 等同于 auto
            shift
            ;;
        --template)
            TEMPLATE_PATH="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        -*)
            echo "错误: 未知选项 $1"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$MATERIALS_DIR" ]; then
                MATERIALS_DIR="$1"
            else
                echo "错误: 多余的参数 $1"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# 验证必需参数
if [ -z "$MATERIALS_DIR" ]; then
    echo "错误: 缺少材料目录参数"
    show_usage
    exit 1
fi

# 验证材料目录存在
if [ ! -d "$MATERIALS_DIR" ]; then
    echo "错误: 材料目录不存在: $MATERIALS_DIR"
    exit 1
fi

# 验证模板文件（如果提供）
if [ -n "$TEMPLATE_PATH" ] && [ ! -f "$TEMPLATE_PATH" ]; then
    echo "错误: 模板文件不存在: $TEMPLATE_PATH"
    exit 1
fi

# 转换为绝对路径
MATERIALS_DIR=$(cd "$MATERIALS_DIR" && pwd)
if [ -n "$TEMPLATE_PATH" ]; then
    TEMPLATE_PATH=$(cd "$(dirname "$TEMPLATE_PATH")" && pwd)/$(basename "$TEMPLATE_PATH")
fi

# ============ 项目初始化 ============

# 生成项目名称（基于时间戳）
PROJECT_NAME="paper-$(date +%Y%m%d-%H%M%S)"
PROJECT_DIR="$REPO_ROOT/projects/$PROJECT_NAME"

echo "========================================"
echo "WriteSystem 一句话启动"
echo "========================================"
echo ""
echo "材料目录: $MATERIALS_DIR"
echo "运行模式: $MODE"
echo "项目名称: $PROJECT_NAME"
[ -n "$TEMPLATE_PATH" ] && echo "格式模板: $TEMPLATE_PATH"
echo ""

# 创建项目脚手架
echo "[1/5] 创建项目结构..."
bash "$SCRIPT_DIR/scaffold.sh" "$PROJECT_NAME" > /dev/null

# 复制材料到原始资料目录
echo "[2/5] 复制材料文件..."
MATERIALS_COUNT=$(find "$MATERIALS_DIR" -type f | wc -l)
cp -r "$MATERIALS_DIR"/* "$PROJECT_DIR/00_订单信息/原始资料/" 2>/dev/null || true
echo "  已复制 $MATERIALS_COUNT 个文件"

# 如果指定了模板，额外复制到 01_格式模板/
if [ -n "$TEMPLATE_PATH" ]; then
    cp "$TEMPLATE_PATH" "$PROJECT_DIR/01_格式模板/"
    echo "  已复制模板到 01_格式模板/"
fi

# 根据模式调整 pipeline 配置
echo "[3/5] 配置管线参数..."
if [ "$MODE" = "auto" ]; then
    INTERACTION_LEVEL="minimal"
    REVISE_MODE="auto"
    echo "  模式: 全自动（minimal + auto）"
else
    INTERACTION_LEVEL="coarse"
    REVISE_MODE="manual"
    echo "  模式: 中途审查（coarse + manual）"
fi

# 更新订单摘要的 pipeline 配置
sed -i "s/interaction_level: coarse/interaction_level: $INTERACTION_LEVEL/" \
    "$PROJECT_DIR/00_订单信息/订单摘要.md"
sed -i "s/revise_mode: auto/revise_mode: $REVISE_MODE/" \
    "$PROJECT_DIR/00_订单信息/订单摘要.md"

# 生成执行指令文件
echo "[4/5] 生成 AI 执行指令..."
INSTRUCTION_FILE="$PROJECT_DIR/.run_instruction.md"

cat > "$INSTRUCTION_FILE" << EOF
# 论文撰写管线执行指令

> 项目: $PROJECT_NAME
> 模式: $MODE
> 生成时间: $(date +"%Y-%m-%d %H:%M:%S")

---

## 执行概览

你将按照以下顺序执行完整的论文撰写管线：

\`\`\`
Phase 0 → Phase 1a/1b → M1/M2 → Phase 2 → M3 → Phase 3 → M4 → (Phase 3.5 可选)
\`\`\`

**配置参数**:
- \`interaction_level\`: $INTERACTION_LEVEL
- \`revise_mode\`: $REVISE_MODE

---

## Phase 0 — 订单提炼

**Agent**: \`paper-order-analyst\`

**任务**:
1. 扫描 \`00_订单信息/原始资料/\` 下的所有文件
2. 识别文件类型：格式模板 / 需求文件 / 数据文件 / 图片 / 参考范文 / 用户笔记
3. 自动分类并移动到对应目录（格式模板 → 01_格式模板/, 数据 → 02_工作素材/）
4. 生成 \`00_订单信息/原始资料/README.md\` 分类清单
5. 提炼 \`00_订单信息/订单摘要.md\`（标题、类型、学科、字数、截止日期、引用格式）
6. 提炼 \`00_订单信息/格式规范.md\`（从模板分析：页边距、字体、行距）

**质量门控**:
- Gate 0.1: content-reviewer 审查订单摘要完整性
- Gate 0.2: content-reviewer 审查格式规范完整性

**完成标志**: 订单摘要和格式规范已生成且通过审查

EOF

cat >> "$INSTRUCTION_FILE" << EOF
---

## Phase 1a — 文献检索（与 1b 并行）

**Agent**: \`paper-literature-agent\`

**任务**:
1. 从订单摘要提取关键词，确定检索策略（中英文、检索源）
2. 执行检索（知网、Google Scholar、arXiv、Semantic Scholar）
3. 去重、初筛、获取全文
4. 为每篇文献生成索引卡（核心发现、研究方法、与本文关系）
5. 生成 \`04_参考文献/literature_cards/_索引卡汇总.md\`

**质量门控**:
- Gate 1a.1: content-reviewer 审查检索策略
- Gate 1a.2: content-reviewer 审查索引卡质量和数量（本科≥15，硕士≥30）

**完成标志**: 索引卡数量达标且质量通过

---

## Phase 1b — 研究规划（与 1a 并行）

**Agent**: \`paper-researcher\`

**任务**:
1. 阅读索引卡，识别研究缺口，确定方法选择
2. 撰写开题报告（研究背景 → 研究问题 → 文献综述概要 → 研究方法 → 预期贡献）
3. 生成骨架大纲（细化到每个段落的 20-30 字要点）
4. 生成核心论点摘要（200字以内）

**质量门控**:
- Gate 1b.G1: content-reviewer 审查文献基础
- Gate 1b.G2: content-reviewer 审查学术严谨性
- Gate 1b.G3: content-reviewer + data-auditor 联合审查骨架逻辑
- Gate 1b.G4: content-reviewer 结构连贯性审查

**里程碑**:
- M1: paper-advisor 方向确认（Phase 1a 完成后）
- M2: paper-advisor 骨架确认（Phase 1b 完成后）

**完成标志**: M1 和 M2 均为 PASS

EOF

cat >> "$INSTRUCTION_FILE" << EOF
---

## Phase 2 — 逐章撰写

**Agent**: \`paper-copilot\`

**任务**:
1. 按骨架大纲逐章撰写
2. 每段撰写时：
   - \`search_blocks(keywords)\` 检索相关索引卡内容
   - \`query_data_facts(query)\` 查询实验数据
   - 使用 \`[cite_key]\` 格式标记引用
3. 每章完成后保存到 \`05_撰写过程/第N章_{标题}.md\`
4. 更新 \`05_撰写过程/_引用编号注册表.md\`
5. 所有章节完成后合并为 \`05_撰写过程/正文草稿.md\`

**质量门控**:
- Gate 2.1: content-reviewer 章节计划审查
- Gate 2.2: validate_word_count + validate_chapter_citations + content-reviewer + data-auditor
- Gate 2.3: 合并后全局检查（总字数、引用一致性、数据一致性）

**里程碑**:
- M3: paper-advisor 草稿审查（全文完成后）

**完成标志**: M3 = PASS

---

## Phase 3 — 排版终审

**Agent**: \`paper-formatter\`

**任务**:
1. Markdown 就绪性检查（并行）:
   - validate_markdown_structure
   - validate_assets
   - validate_word_count
   - validate_citations
2. 引用生成与排序:
   - build_reference_list（按引用格式）
   - validate_citation_order
   - 追加参考文献列表到正文
3. 排版管道:
   - apply_minimax_c2（首选）或 apply_pandoc_templated（备用）
   - 输出 \`06_最终交付/{论文标题}_终稿.docx\`
4. DOCX 成品校验（并行）:
   - validate_docx_styles / sections / layout / fonts / references
5. 终审:
   - content-reviewer + data-auditor
   - assess_aigc_risk

**质量门控**:
- Gate 3.2: DOCX 校验通过

**里程碑**:
- M4: paper-advisor 交付确认

**AIGC 触发**: 如果 assess_aigc_risk 返回高风险 → Phase 3.5

**完成标志**: M4 = PASS

EOF

cat >> "$INSTRUCTION_FILE" << EOF
---

## Phase 3.5 — 降AI处理（条件触发）

**Skill**: \`anti-aigc\`

**触发条件**: Phase 3 中 assess_aigc_risk 返回高风险

**任务**:
1. 多检测器并行评分（GPTZero / Originality / 知网）
2. 生成逐段 AI 热力图，标记高危段落
3. 对高危段落执行后处理对抗:
   - 统计特征多样化（词频分布、句长方差）
   - 句式结构变异（主动/被动转换、从句重组）
   - 段落结构重组（逻辑链重排、过渡句重写）
4. 迭代验证直到全部通过或达到 3 轮
5. 语义保真度验证
6. 替换终稿 docx

**完成标志**: AIGC 风险分 < 阈值，语义保真度 > 0.85

---

## 执行模式说明

### 全自动模式（--auto / --minimal）
- **行为**: AI 一路执行到完成，除非遇到信息缺失或无法自动解决的错误
- **停止节点**:
  1. Phase 0 完成后（订单确认）
  2. Phase 3 + M4 完成后（交付确认）
- **REVISE 处理**: 自动修复，最多 2 轮，超过后降级为 manual
- **适用场景**: 用户完全信任 AI，只关心结果

### 中途审查模式（--review）
- **行为**: 每个 Phase 结束后停止，向用户汇报并询问要求
- **停止节点**:
  1. Phase 0 完成后（订单确认）
  2. Phase 1a + 1b + M1/M2 完成后（骨架确认）
  3. Phase 2 + M3 完成后（草稿确认）
  4. Phase 3 + M4 完成后（交付确认）
- **REVISE 处理**: 暂停管线，通知用户问题，等待决策
- **适用场景**: 用户想逐阶段把控质量和方向

---

## 重要提示

1. **规范位置**: 所有规范定义在 \`spec/conventions/pipeline-spec.md\`
2. **Agent 定义**: 各 Agent 能力在 \`tools/agent/*.md\`
3. **MCP 工具**: 23 个验证和处理工具在 \`tools/mcp-servers/paper-tools-mcp/\`
4. **质量底线**: 不可跳过的检查见 pipeline-spec.md § 十
5. **状态转换**: INIT → ACTIVE → REVIEW → ARCHIVED

---

## 开始执行

现在请按照上述流程执行完整管线。从 Phase 0 开始。

项目路径: \`$PROJECT_DIR\`

EOF

echo "  指令文件已生成: .run_instruction.md"
echo ""

# ============ 启动 AI 执行 ============

echo "[5/5] 启动 AI 执行管线..."
echo ""
echo "========================================"
echo "准备就绪！"
echo "========================================"
echo ""
echo "项目位置: $PROJECT_DIR"
echo "执行指令: $INSTRUCTION_FILE"
echo ""
echo "请在 AI Agent 中执行以下命令："
echo ""
if command -v pbcopy &> /dev/null; then
    # macOS
    echo "cd $PROJECT_DIR && cat .run_instruction.md" | pbcopy
    echo "  （命令已复制到剪贴板）"
elif command -v xclip &> /dev/null; then
    # Linux with xclip
    echo "cd $PROJECT_DIR && cat .run_instruction.md" | xclip -selection clipboard
    echo "  （命令已复制到剪贴板）"
elif command -v clip.exe &> /dev/null; then
    # WSL
    echo "cd $PROJECT_DIR && cat .run_instruction.md" | clip.exe
    echo "  （命令已复制到剪贴板）"
else
    echo "  cd $PROJECT_DIR && cat .run_instruction.md"
fi
echo ""
echo "或者直接告诉 AI："
echo ""
echo "  \"请阅读 $PROJECT_DIR/.run_instruction.md 并开始执行\""
echo ""
echo "========================================"





