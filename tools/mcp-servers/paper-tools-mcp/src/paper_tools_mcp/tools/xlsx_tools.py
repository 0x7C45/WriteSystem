"""XLSX 工具：基于 minimax-xlsx 脚本。提供数据查询和公式校验。"""

import json
import subprocess
from pathlib import Path

from paper_tools_mcp.utils.safe_path import safe_path_exists


# ── minimax-xlsx 脚本路径 ────────────────────────────────────

_XLSX_SCRIPTS_DIR = Path.home() / ".claude" / "skills" / "minimax-xlsx" / "scripts"


def _run_xlsx_script(script_name: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """调用 minimax-xlsx Python 脚本。"""
    script_path = _XLSX_SCRIPTS_DIR / script_name
    cmd = ["python3", str(script_path)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def query_excel_data(
    file_path: str,
    query: str = "structure",
    search_target: str | None = None,
    sheet: str | None = None,
) -> dict:
    """查询 Excel 数据。支持概览查询和精确点查。

    Args:
        file_path: Excel 文件路径（.xlsx/.xlsm/.csv/.tsv）。
        query: 查询模式 — "structure" 结构概览(~100 tokens) | "summary" 含预览+统计(~300 tokens) | "quality" 数据质量审计(~200 tokens)。
        search_target: 精确点查关键词。提供时忽略 query 参数，仅返回匹配行关键数值(~20 tokens)。如 "2023年营收"、"样本量"、"回归系数"。
        sheet: 限定工作表名（可选）。
    """
    if query not in ("structure", "summary", "quality"):
        return {"error": f"无效查询模式: {query}，可选: structure, summary, quality"}

    if not safe_path_exists(file_path):
        return {"error": f"文件不存在: {file_path}"}

    # ── 精确点查模式 ──────────────────────────────────────
    if search_target:
        return _point_query(file_path, search_target, sheet)

    # ── 概览查询模式 ──────────────────────────────────────
    cmd_args = [str(Path(file_path).resolve()), "--json"]
    if sheet:
        cmd_args.extend(["--sheet", sheet])

    # quality 模式用 --quality flag
    if query == "quality":
        cmd_args.append("--quality")

    try:
        result = _run_xlsx_script("xlsx_reader.py", *cmd_args)
    except FileNotFoundError:
        return {"error": "python3 未找到"}
    except subprocess.TimeoutExpired:
        return {"error": "Excel 读取超时（60秒）"}

    if result.returncode != 0:
        return {"error": "Excel 读取失败", "stderr": result.stderr[:500]}

    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Excel 输出解析失败", "raw_preview": result.stdout[:200]}

    # 按 query 裁剪返回内容，控制 token 消耗
    if query == "structure":
        return _extract_structure(raw)
    elif query == "summary":
        return _extract_summary(raw)
    else:  # quality
        return _extract_quality(raw)


def _point_query(file_path: str, search_target: str, sheet: str | None = None) -> dict:
    """精确点查：用 pandas 过滤匹配行，仅返回关键数值。"""
    try:
        import pandas as pd
    except ImportError:
        return {"error": "pandas 未安装，无法执行精确点查"}

    resolved = str(Path(file_path).resolve())
    try:
        read_args: dict = {"nrows": 10000}  # 安全上限
        if sheet:
            read_args["sheet_name"] = sheet
        df = pd.read_excel(resolved, **read_args)
    except Exception as e:
        return {"error": f"Excel 读取失败: {e}"}

    # 按关键词过滤
    mask = df.astype(str).apply(
        lambda col: col.str.contains(search_target, case=False, na=False)
    ).any(axis=1)
    matches = df[mask]

    if matches.empty:
        return {"status": "NO_MATCH", "search_target": search_target}

    # 仅返回匹配行的文本表示（最多 3 行）
    rows_text = matches.head(3).to_string(index=False)
    return {
        "status": "OK",
        "search_target": search_target,
        "match_count": len(matches),
        "result": rows_text,
    }


def _extract_structure(raw: dict) -> dict:
    """提取结构概览（~100 tokens）。"""
    sheets_info = []
    for sheet_data in raw.get("sheets", [raw]):
        info = {
            "name": sheet_data.get("name", "unknown"),
            "shape": sheet_data.get("structure", {}).get("shape", {}),
            "columns": sheet_data.get("structure", {}).get("columns", []),
        }
        sheets_info.append(info)
    return {"status": "OK", "query": "structure", "sheets": sheets_info}


def _extract_summary(raw: dict) -> dict:
    """提取摘要（structure + 5行预览 + describe 统计）。"""
    result = _extract_structure(raw)
    result["query"] = "summary"
    for sheet_data in raw.get("sheets", [raw]):
        name = sheet_data.get("name", "unknown")
        # 找到对应的 sheet 并添加预览和统计
        for s in result["sheets"]:
            if s["name"] == name:
                s["preview"] = sheet_data.get("structure", {}).get("preview", [])[:5]
                s["stats"] = sheet_data.get("stats", {})
                break
    return result


def _extract_quality(raw: dict) -> dict:
    """提取数据质量审计结果。"""
    findings = raw.get("quality", {}).get("findings", [])
    return {
        "status": "OK",
        "query": "quality",
        "findings_count": len(findings),
        "findings": findings[:20],  # 最多 20 条
    }


def validate_excel_formulas(
    file_path: str,
    sheet: str | None = None,
) -> dict:
    """静态校验 Excel 公式正确性（检测 #REF!、断裂引用、名称错误等）。

    Args:
        file_path: Excel 文件路径（.xlsx/.xlsm）。
        sheet: 限定工作表名（可选）。
    """
    if not safe_path_exists(file_path):
        return {"error": f"文件不存在: {file_path}"}

    cmd_args = [str(Path(file_path).resolve()), "--json"]
    if sheet:
        cmd_args.extend(["--sheet", sheet])

    try:
        result = _run_xlsx_script("formula_check.py", *cmd_args)
    except FileNotFoundError:
        return {"error": "python3 未找到"}
    except subprocess.TimeoutExpired:
        return {"error": "公式检查超时（60秒）"}

    if result.returncode != 0:
        return {"error": "公式检查失败", "stderr": result.stderr[:500]}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "公式检查输出解析失败", "raw_preview": result.stdout[:200]}
