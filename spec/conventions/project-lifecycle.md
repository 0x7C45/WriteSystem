# 项目生命周期

## 状态机

```
INIT → ACTIVE → REVIEW → ARCHIVED
```

## 状态定义

### INIT（初始化）
- 触发: 用户发起新项目
- 动作: `tools/scaffold.sh {project_name}` 创建 00-06 空目录
- 产物: 标准目录结构 + 订单摘要模板

### ACTIVE（进行中）
- Phase 0: 订单提炼 → 00_订单信息/
- Phase 1a: 文献检索 → 04_参考文献/
- Phase 1b: 研究规划 → 03_计划与方案/
- Phase 2: 逐章撰写 → 05_撰写过程/
- Phase 3: 排版终审 → 06_最终交付/

### REVIEW（待确认）
- 触发: formatter 输出终稿，advisor M4 = PASS
- 等待: 用户最终确认交付物

### ARCHIVED（已归档）
- 触发: 用户确认交付
- 动作: `tools/archive.sh {project_name}` 执行归档协议
- 结果: 项目移至 `projects/_archive/{name}/`

## 归档协议

当项目进入 ARCHIVED 状态时执行:

1. 保留 06_最终交付/ 全部（终稿不可丢）
2. 保留 00_订单信息/ 全部（需求可追溯）
3. 保留 04_参考文献/literature_cards/（文献可复用）
4. 删除 02_工作素材/ 中的 .zip 文件（已解压的）
5. 删除 05_撰写过程/ 中的中间草稿（保留分章终稿）
6. 删除项目根目录散落的 .py / .docx / test_* 文件
7. 删除与 01/ 重复的模板文件
8. 生成 07_归档快照/README.md
9. 移动到 projects/_archive/{name}/

## 项目元数据

每个项目 `00_订单信息/订单摘要.md` 头部记录:

```yaml
---
repo_spec_version: v1.0.0
project_version: 1
created: YYYY-MM-DD
status: active
---
```
