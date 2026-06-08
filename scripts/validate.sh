#!/bin/bash
# validate.sh — 仓库健康检查
# 用法: bash scripts/validate.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ISSUES=0
WARNINGS=0

red()   { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow(){ echo -e "\033[33m$1\033[0m"; }

echo "=== WriteSystem 仓库健康检查 ==="
echo ""

# --- 1. 必要目录 ---
echo "--- 必要目录 ---"
for dir in spec tools/agent tools/skills tools/rules tools/mcp-servers \
           library docs projects projects/_archive scripts; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        green "  ✓ $dir/"
    else
        red "  ✗ $dir/ — 缺失"
        ((ISSUES++))
    fi
done

# --- 2. 禁止的 Agent 专属目录 ---
echo ""
echo "--- Agent 专属目录（不应存在） ---"
for dir in .opencode .hermes .claude; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        yellow "  ⚠ $dir/ — 应删除，不属于仓库"
        ((WARNINGS++))
    fi
done

# --- 3. 必要文件 ---
echo ""
echo "--- 必要文件 ---"
for file in spec/REPO_SPEC.md spec/VERSION AGENTS.md README.md .gitignore; do
    if [ -f "$REPO_ROOT/$file" ]; then
        green "  ✓ $file"
    else
        red "  ✗ $file — 缺失"
        ((ISSUES++))
    fi
done

# --- 4. 编译产物 ---
echo ""
echo "--- 编译产物 ---"
CRUFT=$(find "$REPO_ROOT" -type d \( -name "__pycache__" -o -name "bin" -o -name "obj" -o -name ".pytest_cache" \) \
    -not -path "*/dotnet/*" 2>/dev/null | wc -l)
CRUFT_FILES=$(find "$REPO_ROOT" -type f \( -name "*.pyc" -o -name "*.pdb" \) \
    -not -path "*/dotnet/*" 2>/dev/null | wc -l)
if [ "$CRUFT" -eq 0 ] && [ "$CRUFT_FILES" -eq 0 ]; then
    green "  ✓ 无编译产物"
else
    yellow "  ⚠ $CRUFT 缓存目录 + $CRUFT_FILES 缓存文件"
    ((WARNINGS++))
fi

# --- 5. 项目根目录清洁度 ---
echo ""
echo "--- 项目根目录清洁度 ---"
if [ -d "$REPO_ROOT/projects" ]; then
    for proj in "$REPO_ROOT/projects/"*/; do
        proj_name=$(basename "$proj")
        [ "$proj_name" = "_archive" ] && continue
        LOOSE=$(find "$proj" -maxdepth 1 -type f \( -name "*.py" -o -name "*.docx" \) 2>/dev/null | wc -l)
        if [ "$LOOSE" -gt 0 ]; then
            yellow "  ⚠ $proj_name: $LOOSE 个散落文件"
            ((WARNINGS++))
        fi
    done
fi
green "  ✓ 项目根目录干净"

# --- 6. 空目录 ---
echo ""
echo "--- 空目录 ---"
EMPTY=$(find "$REPO_ROOT/projects" -type d -empty -not -path "*/.git/*" -not -path "*/_archive" -not -path "*/_examples/*" 2>/dev/null)
if [ -z "$EMPTY" ]; then
    green "  ✓ 无空目录"
else
    echo "$EMPTY" | while read d; do
        yellow "  ⚠ $d (空)"
    done
    ((WARNINGS++))
fi

# --- 汇总 ---
echo ""
echo "========================================="
if [ "$ISSUES" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    green "✓ 仓库健康 — 0 错误, 0 警告"
elif [ "$ISSUES" -eq 0 ]; then
    yellow "⚠ 仓库基本健康 — 0 错误, $WARNINGS 个警告"
else
    red "✗ 仓库需修复 — $ISSUES 个错误, $WARNINGS 个警告"
fi
echo "========================================="
exit $ISSUES
