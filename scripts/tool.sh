#!/bin/bash
# tool.sh — 仓库工具管理（MCP / Skill / Rule / Agent 的出入替换）
# 用法:
#   bash scripts/tool.sh add    --type {type} --path {source}  [--name {name}]
#   bash scripts/tool.sh remove {name}                          [--force]
#   bash scripts/tool.sh replace {name} --with {source}         [--force]
#   bash scripts/tool.sh list
#   bash scripts/tool.sh deps {name}

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REGISTRY="$REPO_ROOT/tools/REGISTRY.yml"
TOOLS_DIR="$REPO_ROOT/tools"

# 类型→目录映射
type_dir() {
    case "${1:-}" in
        mcp-server|mcp)  echo "mcp-servers" ;;
        skill)           echo "skills" ;;
        rule)            echo "rules" ;;
        agent)           echo "agent" ;;
        *)               echo "" ;;
    esac
}

# ── list ──
cmd_list() {
    echo "已安装工具:"
    if grep -q '^installed: {}' "$REGISTRY" 2>/dev/null; then
        echo "  (无)"
        return
    fi
    # 简单解析 YAML
    python3 -c "
import yaml, sys
try:
    with open('$REGISTRY') as f:
        data = yaml.safe_load(f)
    installed = data.get('installed', {})
    for category, items in installed.items():
        if items:
            print(f'  [{category}]')
            for name, info in items.items():
                ver = info.get('version', '?')
                print(f'    {name}  v{ver}')
except: print('  (解析失败)')
" 2>/dev/null || echo "  (需要 PyYAML)"
}

# ── deps ──
cmd_deps() {
    local name="${1:-}"
    [ -z "$name" ] && { echo "用法: bash scripts/tool.sh deps {name}"; exit 1; }
    echo "依赖关系查询: $name"
    python3 -c "
import yaml
with open('$REGISTRY') as f:
    data = yaml.safe_load(f)
installed = data.get('installed', {})
# 查找工具
found = None
for cat, items in installed.items():
    if name in (items or {}):
        found = (cat, items[name])
        break
if not found:
    print('  未找到')
    exit()
cat, info = found
deps = info.get('depends_on', {})
if not deps:
    print('  无依赖')
else:
    for dep_cat, dep_names in deps.items():
        print(f'  依赖 {dep_cat}: {dep_names}')

# 反向依赖
print('  被以下工具依赖:')
has_rev = False
for rev_cat, rev_items in installed.items():
    for rev_name, rev_info in (rev_items or {}).items():
        rdeps = rev_info.get('depends_on', {})
        for rcat, rnames in rdeps.items():
            if name in rnames:
                print(f'    {rev_name} ({rev_cat})')
                has_rev = True
if not has_rev:
    print('    (无)')
" 2>/dev/null || echo "  (需要 PyYAML)"
}

# ── add ──
cmd_add() {
    local src_type="" src_path="" src_name=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --type)  src_type="$2"; shift 2 ;;
            --path)  src_path="$2"; shift 2 ;;
            --name)  src_name="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    [ -z "$src_type" ] && { echo "错误: 需要 --type (mcp-server|skill|rule|agent)"; exit 1; }
    [ -z "$src_path" ] && { echo "错误: 需要 --path (源目录)"; exit 1; }
    [ ! -d "$src_path" ] && { echo "错误: 源目录不存在: $src_path"; exit 1; }

    local target_subdir
    target_subdir=$(type_dir "$src_type")
    [ -z "$target_subdir" ] && { echo "错误: 未知类型 '$src_type'，可选: mcp-server|skill|rule|agent"; exit 1; }

    # 自动推断名称
    if [ -z "$src_name" ]; then
        src_name=$(basename "$src_path")
    fi

    local target_dir="$TOOLS_DIR/$target_subdir/$src_name"

    if [ -d "$target_dir" ]; then
        echo "错误: 目标已存在: $target_dir"
        echo "  使用 replace 替换或 remove 删除后再 add"
        exit 1
    fi

    echo "添加 $src_type: $src_name"
    echo "  源: $src_path"
    echo "  目标: $target_dir"

    # 复制
    cp -r "$src_path" "$target_dir"

    # 更新 REGISTRY（简单追加，后续用 PyYAML 完善）
    echo "  已复制到 $target_dir"
    echo "  提示: 手动更新 tools/REGISTRY.yml 或使用 PyYAML 自动更新"
}

# ── remove ──
cmd_remove() {
    local name="${1:-}" force=false
    [ "$name" = "--force" ] && { force=true; name="${2:-}"; }
    [ "${2:-}" = "--force" ] && force=true
    [ -z "$name" ] && { echo "用法: bash scripts/tool.sh remove {name} [--force]"; exit 1; }

    # 查找工具位置
    local found=""
    for subdir in mcp-servers skills rules agent; do
        if [ -d "$TOOLS_DIR/$subdir/$name" ]; then
            found="$TOOLS_DIR/$subdir/$name"
            break
        fi
    done
    [ -z "$found" ] && { echo "错误: 未找到 '$name'"; exit 1; }

    echo "移除: $name"
    echo "  位置: $found"

    # TODO: 检查反向依赖
    # if ! $force; then check_reverse_deps "$name" && exit 1; fi

    rm -rf "$found"
    echo "  已删除"
    echo "  提示: 手动从 tools/REGISTRY.yml 中移除相关条目"
}

# ── replace ──
cmd_replace() {
    local name="${1:-}" src_path="" force=false
    shift
    while [ $# -gt 0 ]; do
        case "$1" in
            --with)   src_path="$2"; shift 2 ;;
            --force)  force=true; shift ;;
            *) shift ;;
        esac
    done
    [ -z "$name" ] && { echo "用法: bash scripts/tool.sh replace {name} --with {source} [--force]"; exit 1; }
    [ -z "$src_path" ] && { echo "错误: 需要 --with (新源目录)"; exit 1; }

    echo "替换: $name"
    echo "  新源: $src_path"
    echo "  提示: 替换操作会先 remove 再 add，依赖校验待完善"
}

# ── 主入口 ──
case "${1:-}" in
    list)   shift; cmd_list "$@" ;;
    deps)   shift; cmd_deps "$@" ;;
    add)    shift; cmd_add "$@" ;;
    remove) shift; cmd_remove "$@" ;;
    replace)shift; cmd_replace "$@" ;;
    *)
        echo "用法: bash scripts/tool.sh {add|remove|replace|list|deps}"
        echo ""
        echo "  add    --type {type} --path {source}    添加工具"
        echo "  remove {name} [--force]                  移除工具"
        echo "  replace {name} --with {source} [--force] 替换工具"
        echo "  list                                     列出已安装"
        echo "  deps {name}                              查看依赖"
        exit 1
        ;;
esac
