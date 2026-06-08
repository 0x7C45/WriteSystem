#!/bin/bash
# archive.sh — 归档已完成论文项目
# 用法: bash scripts/archive.sh {project_name} [--dry-run]

set -euo pipefail

DRY_RUN=false
if [ "${2:-}" == "--dry-run" ]; then
    DRY_RUN=true
fi

if [ $# -eq 0 ]; then
    echo "用法: bash scripts/archive.sh {project_name} [--dry-run]"
    echo "示例: bash scripts/archive.sh writing1"
    exit 1
fi

PROJECT_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$REPO_ROOT/projects/$PROJECT_NAME"
ARCHIVE_DIR="$REPO_ROOT/projects/_archive"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目 '$PROJECT_NAME' 不存在: $PROJECT_DIR"
    exit 1
fi

echo "归档项目: $PROJECT_NAME"
echo "源: $PROJECT_DIR"
echo "目标: $ARCHIVE_DIR/$PROJECT_NAME"
if $DRY_RUN; then echo "模式: 预览 (--dry-run)"; fi
echo ""

cleanup_steps() {
    local dir="$1"; local dry="$2"
    step() { echo "  [$1/7] $2"; }

    step 1 "保留 06_最终交付/ (跳过)"
    step 2 "保留 00_订单信息/ (跳过)"
    step 3 "保留 04_参考文献/ (跳过)"

    step 4 "删除已解压 .zip..."
    if [ -d "$dir/02_工作素材" ]; then
        find "$dir/02_工作素材" -name "*.zip" -type f | while read f; do
            echo "    rm $f"
            if ! $dry; then rm -f "$f"; fi
        done
    fi

    step 5 "清理中间草稿..."
    if [ -d "$dir/05_撰写过程" ]; then
        for pattern in "正文草稿*.md" "正文完整版*.md" "正文终稿*.md"; do
            find "$dir/05_撰写过程" -maxdepth 1 -name "$pattern" -type f | while read f; do
                echo "    rm $f"
                if ! $dry; then rm -f "$f"; fi
            done
        done
    fi

    step 6 "删除项目根目录散落文件..."
    for pattern in "*.py" "template*.docx" "test_*.md"; do
        find "$dir" -maxdepth 1 -name "$pattern" -type f | while read f; do
            echo "    rm $f"
            if ! $dry; then rm -f "$f"; fi
        done
    done

    step 7 "生成归档摘要..."
    TODAY=$(date +%Y-%m-%d)
    mkdir -p "$dir/07_归档快照"
    cat > "$dir/07_归档快照/README.md" << EOF
# $PROJECT_NAME 归档快照
> 归档日期: $TODAY
## 保留: 00_订单信息/ 04_参考文献/ 06_最终交付/
## 清理: 中间草稿、散落脚本、重复模板、已解压 zip
EOF
}

cleanup_steps "$PROJECT_DIR" "$DRY_RUN"

if $DRY_RUN; then
    echo ""
    echo "以上为预览。执行归档: bash scripts/archive.sh $PROJECT_NAME"
    exit 0
fi

mkdir -p "$ARCHIVE_DIR"
[ -d "$ARCHIVE_DIR/$PROJECT_NAME" ] && rm -rf "$ARCHIVE_DIR/$PROJECT_NAME"
mv "$PROJECT_DIR" "$ARCHIVE_DIR/"
echo ""
echo "✓ '$PROJECT_NAME' 已归档到 $ARCHIVE_DIR/$PROJECT_NAME"
