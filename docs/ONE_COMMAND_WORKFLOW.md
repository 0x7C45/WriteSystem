# 一句话启动完整论文工作流

> WriteSystem v1.0.0 | 从资料文件夹到最终 DOCX，一条命令启动全流程

---

## 快速开始

### 1. 准备材料文件夹

将所有参考文件放到一个文件夹下（支持任意格式）：

```
~/Desktop/论文资料/
├── 毕业论文格式模板.docx
├── 论文任务书.pdf
├── 实验数据.xlsx
├── 参考范文.pdf
├── 实验照片1.jpg
├── 实验照片2.jpg
└── 我的研究想法.txt
```

**支持的文件类型**：
- **格式模板**: .docx
- **需求文件**: .pdf, .docx, .txt, .md
- **数据文件**: .xlsx, .csv, .json
- **图片**: .jpg, .png, .svg
- **参考范文**: .pdf, .docx
- **用户笔记**: .txt, .md

**无需**：
- ❌ 手动分类文件到子目录
- ❌ 重命名文件
- ❌ 编写 README 或配置文件

### 2. 一句话启动

```bash
cd /path/to/WriteSystem
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

**就这样！** AI 会自动：
1. 创建项目结构
2. 复制所有材料
3. 配置管线参数
4. 生成执行指令
5. 等待你启动 AI 执行

---

## 运行模式

### 全自动模式（推荐新手）

```bash
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

**行为**：
- AI 一路执行到完成
- 只在 2 个节点停止：
  1. Phase 0 完成后（确认订单理解正确）
  2. Phase 3 + M4 完成后（交付最终 DOCX）
- 遇到 REVISE 自动修复（最多 2 轮）
- 除非信息缺失否则不中断

**适用场景**：
- 材料齐全，信任 AI 能力
- 时间紧迫，需要快速产出
- 熟悉流程，不需要逐步把控

### 中途审查模式（推荐初次使用）

```bash
bash scripts/run.sh ~/Desktop/论文资料 --review
```

**行为**：
- 每个 Phase 结束后停止
- 向用户汇报进展并询问要求
- 停止节点：
  1. Phase 0 完成 → 确认订单摘要
  2. Phase 1a+1b+M1/M2 完成 → 确认骨架大纲
  3. Phase 2+M3 完成 → 确认正文草稿
  4. Phase 3+M4 完成 → 确认最终交付
- 遇到 REVISE 暂停，等待用户决策

**适用场景**：
- 首次使用，想了解每个阶段产出
- 对论文质量有严格要求
- 需要在过程中调整方向

### 指定格式模板

```bash
bash scripts/run.sh ~/Desktop/论文资料 --auto --template ~/学位论文模板.docx
```

如果材料文件夹里没有格式模板，或者想明确指定某个模板，使用 `--template` 选项。

---

## 执行流程

### 脚本做什么

```bash
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

1. **创建项目** — 生成 `projects/paper-YYYYMMDD-HHMMSS/` 标准目录
2. **复制材料** — 所有文件复制到 `00_订单信息/原始资料/`
3. **配置管线** — 根据模式调整 `订单摘要.md` 的 pipeline 配置
4. **生成指令** — 创建 `.run_instruction.md` 详细执行指令
5. **等待启动** — 提示你在 AI 中执行

### AI 做什么

当你在 AI Agent 中执行指令后，AI 会按以下顺序工作：

```
Phase 0: 订单提炼
  ↓ 识别文件类型、分类、提炼订单摘要和格式规范
  ↓ Gate 0.1/0.2: 审查完整性

Phase 1a: 文献检索 ∥ Phase 1b: 研究规划
  ↓ 检索中英文文献、生成索引卡 ∥ 撰写开题报告、生成骨架大纲
  ↓ M1: 方向确认 → M2: 骨架确认

Phase 2: 逐章撰写
  ↓ 按骨架大纲逐段撰写、引用文献、查询数据
  ↓ M3: 草稿审查

Phase 3: 排版终审
  ↓ 校验 Markdown、生成参考文献、排版 DOCX、终审
  ↓ M4: 交付确认

[Phase 3.5: 降AI处理]  ← 条件触发
  ↓ 多检测器评分、对抗性后处理、迭代验证
```

**预计耗时**：
- Phase 0: 2-5 分钟
- Phase 1a+1b: 30-60 分钟
- Phase 2: 2-6 小时（取决于字数）
- Phase 3: 10-30 分钟
- Phase 3.5: 20-40 分钟（如果触发）

**总计**：3-8 小时（取决于论文字数和复杂度）

---

## 最终产物

执行完成后，在 `projects/paper-YYYYMMDD-HHMMSS/06_最终交付/` 会生成：

| 文件 | 说明 |
|------|------|
| `{论文标题}_终稿.docx` | **最终交付的 Word 文档** |
| `Markdown就绪性报告.md` | Markdown 结构校验结果 |
| `终审报告.md` | content-reviewer + data-auditor 的质量审查 |
| `排版历程报告.md` | 排版管道执行日志 |
| `降AI处理报告.md` | AIGC 风险评估和处理记录（如果触发） |

---

## 常见场景

### 场景 1: 只有口头需求，没有文件

创建一个空文件夹，写一个 `需求.txt`：

```bash
mkdir ~/论文资料
cat > ~/论文资料/需求.txt << EOF
论文标题：基于深度学习的图像分类研究
类型：本科毕业论文
学科：计算机科学
字数：8000-10000字
截止日期：2026-07-15
引用格式：GB/T 7714
特殊要求：需要3个实验对比
EOF

bash scripts/run.sh ~/论文资料 --auto
```

### 场景 2: 材料很多，不确定哪些有用

**全部扔进去！** AI 会自动识别：

```bash
# 把桌面上所有可能相关的文件都扔进一个文件夹
mkdir ~/论文资料-全部
cp ~/Desktop/*.{pdf,docx,xlsx,jpg,txt} ~/论文资料-全部/ 2>/dev/null || true
cp ~/Downloads/论文相关/* ~/论文资料-全部/ 2>/dev/null || true

bash scripts/run.sh ~/论文资料-全部 --review
```

用 `--review` 模式，Phase 0 完成后检查 AI 是否正确识别。

### 场景 3: 需要手动干预某些章节

启动后，在 Phase 2 时告诉 AI：

```
第 3 章我自己写，跳过它，继续第 4 章
```

然后手动创建 `05_撰写过程/第3章_xxx.md`，AI 合并时会包含。

### 场景 4: 修改中途配置

如果执行到一半觉得 `--review` 太繁琐，想改成全自动：

1. 编辑 `projects/paper-YYYYMMDD-HHMMSS/00_订单信息/订单摘要.md`
2. 修改 frontmatter:
   ```yaml
   pipeline:
     interaction_level: minimal  # 改成 minimal
     revise_mode: auto           # 改成 auto
   ```
3. 告诉 AI："配置已更新，继续执行"

---

## 故障排除

### Q1: 脚本报错 "材料目录不存在"

**原因**: 路径错误或文件夹不存在

**解决**:
```bash
# 检查路径
ls -la ~/Desktop/论文资料

# 使用绝对路径
bash scripts/run.sh /Users/yourname/Desktop/论文资料 --auto
```

### Q2: AI 说找不到项目

**原因**: 没有切换到项目目录

**解决**: 脚本结束时会提示项目路径，复制粘贴到 AI：
```
cd /path/to/WriteSystem/projects/paper-20260606-143022
cat .run_instruction.md
```

### Q3: Phase 0 识别错误（把数据文件当成了需求文件）

**解决**: 告诉 AI：
```
请将 data.xlsx 移动到 02_工作素材/raw/，它是实验数据
```

### Q4: 想跳过降AI处理

在 Phase 3 终审时告诉 AI：
```
跳过降AI处理，我接受当前版本
```

### Q5: 中途想放弃当前项目

```bash
# 项目会保留在 projects/ 下，随时可以归档或删除
rm -rf projects/paper-20260606-143022
```

---

## 高级用法

### 批量处理多个论文

```bash
for dir in ~/论文资料/*; do
    bash scripts/run.sh "$dir" --auto
done
```

### 自定义项目名称

脚本会自动生成 `paper-YYYYMMDD-HHMMSS`，如果想自定义：

```bash
# 先用脚本生成项目
bash scripts/run.sh ~/Desktop/论文资料 --auto
# 生成后重命名
mv projects/paper-20260606-143022 projects/my-thesis
```

### 复用现有项目

如果之前执行到一半中断了，想继续：

```bash
cd projects/paper-20260606-143022
# 告诉 AI: "请从当前状态继续执行管线"
```

---

## 与手动流程对比

### 传统手动流程

```bash
# 1. 创建项目
bash scripts/scaffold.sh my-paper

# 2. 手动复制文件到对应目录
cp ~/Desktop/模板.docx projects/my-paper/01_格式模板/
cp ~/Desktop/数据.xlsx projects/my-paper/02_工作素材/raw/
# ... 逐个分类复制

# 3. 手动编辑订单摘要.md
vim projects/my-paper/00_订单信息/订单摘要.md

# 4. 告诉 AI: "使用 paper-order-analyst 分析 Phase 0"
# 5. Phase 0 完成后，告诉 AI: "开始 Phase 1a"
# 6. Phase 1a 完成后，告诉 AI: "开始 Phase 1b"
# ... 逐个 Phase 手动启动
```

### 一句话启动流程

```bash
bash scripts/run.sh ~/Desktop/论文资料 --auto
# AI 自动执行全部 Phase
```

**节省时间**：~20 分钟的手动操作 → 30 秒

---

## 技术细节

### 自动生成的文件

执行 `run.sh` 后会生成：

1. **标准项目结构** — `projects/paper-YYYYMMDD-HHMMSS/`
2. **执行指令** — `.run_instruction.md`（5个Phase的详细任务清单）
3. **配置调整** — `订单摘要.md` 的 pipeline 段根据模式自动修改

### Pipeline 配置映射

| 用户模式 | interaction_level | revise_mode | 效果 |
|---------|------------------|-------------|------|
| `--auto` | minimal | auto | 只在订单确认和交付时停止 |
| `--review` | coarse | manual | 每个 Phase 后停止，REVISE 时等待用户 |
| `--minimal` | minimal | auto | 同 --auto |

### 模板处理逻辑

- 如果指定 `--template`，复制到 `01_格式模板/` 和 `00_订单信息/原始资料/`
- 如果材料文件夹中有 `.docx` 文件，AI 在 Phase 0 自动识别为模板
- 如果都没有，AI 使用默认学术论文格式

---

## 参考文档

- **完整管线规范** → `spec/conventions/pipeline-spec.md`
- **配置说明** → `spec/conventions/pipeline-config.md`
- **Agent 定义** → `tools/agent/*.md`
- **MCP 工具** → `tools/mcp-servers/paper-tools-mcp/MANIFEST.yml`
- **手动流程** → `docs/QUICKSTART.md`

---

**立即开始**：

```bash
cd /mnt/f/AI/Data/WriteSystem
bash scripts/run.sh ~/Desktop/论文资料 --auto
```
