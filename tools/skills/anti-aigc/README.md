# Anti-AIGC Skill

降AI反检测处理管线 - Phase 3.5 自动触发

## 文档
- **[SKILL.md](./SKILL.md)** - 完整的Skill定义（权威文档）
- **[AUDIT_REPORT.md](./AUDIT_REPORT.md)** - 审计报告和待办事项

## 快速开始
- 自动触发: `paper-formatter` Phase 3 自动调用
- 手动测试: `python -m tools.skills.anti_aigc --help`

## 架构
- Phase 0-5: 完整流程 (见 SKILL.md)
- 知识库: `knowledge/*.json` (4个文件)
- 核心脚本: `scripts/anti_aigc_pipeline.py`

## 状态
- 版本: 2.0.0
- 完整度: 35% (设计完成，实现进行中)
- 下次里程碑: Week 4 (生产就绪 50%)

## 文献支撑
基于13篇AIGC检测与对抗论文 (见 `分步骤工作方法与Prompt_文献增强版.md`)
