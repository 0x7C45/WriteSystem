# Git 策略

## .gitignore 原则

忽略:
- 编译产物: __pycache__/, *.pyc, bin/, obj/, *.dll, *.pdb
- 测试缓存: .pytest_cache/
- 运行时缓存: .hermes/plans/, .hermes/audio_cache/
- IDE: .obsidian/workspace.json, .vscode/
- 大文件可选规则: *.zip（已解压的不入库）

提交:
- 源代码: .py, .sh, .js, .cs, .csproj, .slnx
- 文档: .md
- 配置: .yml, .yaml, .json, .toml, .gitignore
- 模板: .docx, .tex, .xml, .xsd
- 文献: .pdf（放在 reference/）
- 交付物: 06_最终交付/ 中的终稿 .docx

## 提交规范

```
格式: {type}({scope}): {description}

type:
  spec     — 仓库规范变更
  tool     — 工具/MCP 变更
  skill    — Skill 变更
  project  — 项目内容变更
  chore    — 清理、归档、重构
  docs     — 文档变更

scope: 目录名或项目名

示例:
  spec(conventions): 更新 project-lifecycle 归档步骤
  tool(scaffold): scaffold.sh 支持自定义模板路径
  project(writing3): Phase 2 完成第3章撰写
  chore(writing1): 归档 writing1
```

## 分支策略

- `main` — 稳定分支，只接受 PR
- 项目分支: `project/{name}` — 单个项目的开发分支
- 工具分支: `tool/{name}` — MCP/Skill 开发

## 仓库规模限制

- 单文件上限: 10MB（超过用 Git LFS）
- 单目录文件数: 建议 < 100
- 仓库总大小: 建议 < 200MB
