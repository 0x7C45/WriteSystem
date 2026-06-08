"""DOCX 模板分析工具：基于 minimax-docx CLI。"""

import json
import subprocess
from pathlib import Path

from paper_tools_mcp.utils.safe_path import safe_path_exists, template_path_exists


# ── minimax-docx CLI 路径 ────────────────────────────────────

_SKILLS_DIR = Path.home() / ".claude" / "skills"
_DOCX_CLI_PROJECT = _SKILLS_DIR / "minimax-docx" / "scripts" / "dotnet" / "MiniMaxAIDocx.Cli"
_ENV_CHECK_SCRIPT = _SKILLS_DIR / "minimax-docx" / "scripts" / "env_check.sh"


def _run_cli(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """调用 minimax-docx dotnet CLI。"""
    cmd = ["dotnet", "run", "--project", str(_DOCX_CLI_PROJECT), "--"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def analyze_docx_template(
    file_path: str,
    analysis_type: str = "full",
) -> dict:
    """分析 DOCX 模板的样式结构（styleId 映射、zone 结构、字体方案）。

    Args:
        file_path: DOCX 模板文件路径。
        analysis_type: "full" 完整分析（styleId+zone+字体）| "styles_only" 仅样式。
    """
    if analysis_type not in ("full", "styles_only"):
        return {"error": f"无效分析类型: {analysis_type}，可选: full, styles_only"}

    if not safe_path_exists(file_path):
        return {"error": f"文件不存在: {file_path}"}

    # 检查 minimax-docx 环境
    if not _ENV_CHECK_SCRIPT.exists():
        return {"status": "ENV_NOT_READY", "message": "minimax-docx 脚本未找到"}

    try:
        env_result = subprocess.run(
            ["bash", str(_ENV_CHECK_SCRIPT)],
            capture_output=True, text=True, timeout=15,
        )
        if env_result.returncode != 0 or "READY" not in env_result.stdout:
            return {"status": "ENV_NOT_READY", "message": "minimax-docx 环境未就绪（.NET 未安装或版本不兼容）"}
    except Exception as e:
        return {"status": "ENV_NOT_READY", "message": f"环境检查失败: {e}"}

    # 执行分析
    cli_args = ["analyze", "--input", str(Path(file_path).resolve())]
    if analysis_type == "styles_only":
        cli_args.append("--styles-only")

    try:
        result = _run_cli(*cli_args)
    except FileNotFoundError:
        return {"status": "ENV_NOT_READY", "message": "dotnet 命令未找到"}
    except subprocess.TimeoutExpired:
        return {"status": "ERROR", "message": "模板分析超时（120秒）"}

    if result.returncode != 0:
        return {
            "status": "ERROR",
            "message": "模板分析失败",
            "stderr": result.stderr[:500] if result.stderr else "",
        }

    # 解析 CLI 输出
    output = result.stdout.strip()
    return {
        "status": "OK",
        "file": file_path,
        "analysis_type": analysis_type,
        "raw_output": output,
    }
