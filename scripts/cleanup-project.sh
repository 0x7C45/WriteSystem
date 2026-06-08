#!/bin/bash
# cleanup-project.sh — 清理项目中的临时文件
# 用法: bash scripts/cleanup-project.sh {project_name}

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "用法: bash scripts/cleanup-project.sh {project_name}"
    echo "示例: bash scripts/cleanup-project.sh my-paper"
    exit 1
fi

PROJECT_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$REPO_ROOT/projects/$PROJECT_NAME"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目 '$PROJECT_NAME' 不存在: $PROJECT_DIR"
    exit 1
fi

echo "清理项目: $PROJECT_NAME"
echo "位置: $PROJECT_DIR"
echo ""

# 统计清理前大小
BEFORE=$(du -sh "$PROJECT_DIR" | cut -f1)

# ── 清理临时文件 ──
echo "清理临时文件..."

# 1. 删除 .run_instruction.md
if [ -f "$PROJECT_DIR/.run_instruction.md" ]; then
    rm "$PROJECT_DIR/.run_instruction.md"
    echo "  ✓ 已删除 .run_instruction.md"
fi

# 2. 删除 Python 缓存
PYCACHE_COUNT=$(find "$PROJECT_DIR" -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "  ✓ 已删除 $PYCACHE_COUNT 个 __pycache__ 目录"
fi

PYC_COUNT=$(find "$PROJECT_DIR" -type f -name "*.pyc" 2>/dev/null | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "  ✓ 已删除 $PYC_COUNT 个 .pyc 文件"
fi

# 3. 删除临时日志文件
LOG_COUNT=$(find "$PROJECT_DIR" -type f \( -name "*.log" -o -name "*.tmp" \) 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -type f \( -name "*.log" -o -name "*.tmp" \) -delete 2>/dev/null || true
    echo "  ✓ 已删除 $LOG_COUNT 个日志/临时文件"
fi

# 4. 删除空目录
EMPTY_COUNT=$(find "$PROJECT_DIR" -type d -empty 2>/dev/null | wc -l)
if [ "$EMPTY_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -type d -empty -delete 2>/dev/null || true
    echo "  ✓ 已删除 $EMPTY_COUNT 个空目录"
fi

# 5. 删除 macOS 和 Windows 系统文件
DS_STORE_COUNT=$(find "$PROJECT_DIR" -name ".DS_Store" 2>/dev/null | wc -l)
if [ "$DS_STORE_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -name ".DS_Store" -delete 2>/dev/null || true
    echo "  ✓ 已删除 $DS_STORE_COUNT 个 .DS_Store 文件"
fi

THUMBS_COUNT=$(find "$PROJECT_DIR" -name "Thumbs.db" 2>/dev/null | wc -l)
if [ "$THUMBS_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -name "Thumbs.db" -delete 2>/dev/null || true
    echo "  ✓ 已删除 $THUMBS_COUNT 个 Thumbs.db 文件"
fi

# ── 清理后统计 ──
AFTER=$(du -sh "$PROJECT_DIR" | cut -f1)

echo ""
echo "========================================="
echo "清理完成"
echo "========================================="
echo "项目: $PROJECT_NAME"
echo "清理前: $BEFORE"
echo "清理后: $AFTER"
echo ""
echo "清理内容："
echo "  - .run_instruction.md"
echo "  - Python 缓存 (__pycache__, *.pyc)"
echo "  - 临时文件 (*.log, *.tmp)"
echo "  - 空目录"
echo "  - 系统文件 (.DS_Store, Thumbs.db)"
echo "========================================="
