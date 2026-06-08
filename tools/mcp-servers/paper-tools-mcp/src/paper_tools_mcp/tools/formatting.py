"""排版工具：Markdown → Word（Pandoc / minimax-docx）。

提供多级排版策略。env_check 和 analyze 由 run_format_pipeline 顶层缓存，
各排版函数接受可选缓存参数以避免重复调用。
"""

import os
import subprocess
import zipfile
from pathlib import Path

from paper_tools_mcp.utils.safe_path import safe_path_exists, template_path_exists, _validate_path


# ── minimax-docx CLI 路径 ────────────────────────────────────

_SKILLS_DIR = Path.home() / ".claude" / "skills"
_DOCX_CLI_PROJECT = _SKILLS_DIR / "minimax-docx" / "scripts" / "dotnet" / "MiniMaxAIDocx.Cli"
_ENV_CHECK_SCRIPT = _SKILLS_DIR / "minimax-docx" / "scripts" / "env_check.sh"

# 最小有效 DOCX 大小（空 DOCX 约 3-4KB）
_MIN_DOCX_SIZE_BYTES = 2048


def _run_minimax_cli(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """调用 minimax-docx dotnet CLI。"""
    cmd = ["dotnet", "run", "--project", str(_DOCX_CLI_PROJECT), "--"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _check_docx_env() -> bool:
    """检查 minimax-docx .NET 环境是否就绪。"""
    if not _ENV_CHECK_SCRIPT.exists():
        return False
    try:
        r = subprocess.run(
            ["bash", str(_ENV_CHECK_SCRIPT)],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0 and "READY" in r.stdout
    except Exception:
        return False


# ── 输出安全工具 ────────────────────────────────────────────────


def _safe_write_output(
    final_path: str,
    content_writer,
) -> dict:
    """原子写入：先写临时文件，校验通过后 rename。

    Args:
        final_path: 最终输出路径。
        content_writer: callable(tmp_path) -> dict，写入临时文件并返回结果。
            必须返回包含 "status" 键的 dict。

    Returns:
        content_writer 的返回结果（已将 tmp_path 更新为 final_path），
        或 {"status": "FAILED", ...} 如果安全检查失败。
    """
    final = Path(final_path)
    tmp = final.with_suffix(final.suffix + ".tmp")

    # 清理可能残留的旧临时文件
    if tmp.exists():
        try:
            tmp.unlink()
        except OSError:
            pass

    # 调用写入函数，输出到临时路径
    result = content_writer(str(tmp))
    if result.get("status") != "OK":
        # 写入失败，清理临时文件
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        return result

    # 基础文件安全检查
    safety = _verify_docx_minimal(str(tmp))
    if not safety["valid"]:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        return {
            "status": "FAILED",
            "error": f"输出文件安全检查失败: {safety['reason']}",
            "safety_detail": safety,
        }

    # 原子 rename
    try:
        tmp.replace(final_path)
    except OSError as e:
        return {"status": "FAILED", "error": f"rename 失败: {e}"}

    # 更新结果中的路径
    if "output_file" in result:
        result["output_file"] = str(final_path)
    if "output_size_bytes" in result:
        result["output_size_bytes"] = final.stat().st_size
    return result


def _verify_docx_minimal(file_path: str) -> dict:
    """最小 DOCX 文件安全检查。

    检查：文件存在、大小 > 阈值、可作 zip 打开、包含 word/document.xml。
    """
    p = Path(file_path)
    if not p.exists():
        return {"valid": False, "reason": "文件不存在"}
    if p.stat().st_size == 0:
        return {"valid": False, "reason": "文件大小为 0"}
    if p.stat().st_size < _MIN_DOCX_SIZE_BYTES:
        return {"valid": False, "reason": f"文件大小 {p.stat().st_size} < {_MIN_DOCX_SIZE_BYTES}"}
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            names = zf.namelist()
            if "word/document.xml" not in names:
                return {"valid": False, "reason": "zip 中缺少 word/document.xml"}
    except zipfile.BadZipFile:
        return {"valid": False, "reason": "不是有效的 zip/DOCX 文件"}
    return {"valid": True}


def _run_docx_validation_suite(
    docx_path: str,
    template_path: str | None = None,
) -> dict:
    """运行 minimax 完整验证套件。

    按顺序：merge-runs → validate --business → validate --gate-check → validate --xsd (如有)。
    所有 CLI 非零退出码视为失败。

    Args:
        docx_path: 待验证的 DOCX 文件路径。
        template_path: 模板 DOCX 路径（用于 gate-check）。

    Returns:
        {"status": "OK" | "FAILED", "steps": [...]}
    """
    steps: list[dict] = []
    resolved = str(Path(docx_path).resolve())

    # Step 1: merge-runs（修改文件）
    merge_cmd = ["merge-runs", "--input", resolved]
    merge_result = _run_minimax_cli(*merge_cmd, timeout=60)
    steps.append({
        "step": "merge-runs",
        "returncode": merge_result.returncode,
        "stdout": merge_result.stdout[:500] if merge_result.returncode == 0 else merge_result.stderr[:500],
    })
    if merge_result.returncode != 0:
        return {"status": "FAILED", "steps": steps, "failed_at": "merge-runs"}

    # Step 2: validate --business
    biz_result = _run_minimax_cli("validate", "--input", resolved, "--business", timeout=60)
    steps.append({
        "step": "validate --business",
        "returncode": biz_result.returncode,
        "stdout": biz_result.stdout[:500] if biz_result.returncode == 0 else biz_result.stderr[:500],
    })
    if biz_result.returncode != 0:
        return {"status": "FAILED", "steps": steps, "failed_at": "validate-business"}

    # Step 3: gate-check（需要模板）
    if template_path:
        gate_result = _run_minimax_cli(
            "validate", "--input", resolved,
            "--gate-check", str(Path(template_path).resolve()),
            timeout=60,
        )
        steps.append({
            "step": "validate --gate-check",
            "returncode": gate_result.returncode,
            "stdout": gate_result.stdout[:500] if gate_result.returncode == 0 else gate_result.stderr[:500],
        })
        if gate_result.returncode != 0:
            return {"status": "FAILED", "steps": steps, "failed_at": "validate-gate-check"}

    # Step 4: XSD（如果本地有 XSD 文件）
    xsd_path = _SKILLS_DIR / "minimax-docx" / "assets" / "xsd" / "wml-subset.xsd"
    if xsd_path.exists():
        xsd_result = _run_minimax_cli(
            "validate", "--input", resolved,
            "--xsd", str(xsd_path.resolve()),
            timeout=60,
        )
        steps.append({
            "step": "validate --xsd",
            "returncode": xsd_result.returncode,
            "stdout": xsd_result.stdout[:500] if xsd_result.returncode == 0 else xsd_result.stderr[:500],
        })
        if xsd_result.returncode != 0:
            return {"status": "FAILED", "steps": steps, "failed_at": "validate-xsd"}

    return {"status": "OK", "steps": steps}


# ── 向后兼容 ──────────────────────────────────────────────────


def pandoc_to_docx(
    input_file: str,
    output_file: str,
    template_file: str | None = None,
) -> dict:
    """Markdown + 模板 → Word（向后兼容，等价于 apply_pandoc_templated）。"""
    return apply_pandoc_templated(input_file, output_file, template_file)


# ── 排版函数 ──────────────────────────────────────────────────


def build_preflight_docx(
    input_file: str,
    output_file: str,
) -> dict:
    """Markdown → DOCX 结构基线（无模板，仅结构转换）。"""
    if not safe_path_exists(input_file):
        return {"error": f"文件不存在: {input_file}"}

    try:
        _validate_path(output_file)
    except ValueError:
        return {"error": f"输出路径在允许范围外: {output_file}"}

    cmd = [
        "pandoc",
        str(Path(input_file).resolve()),
        "-o", str(Path(output_file).resolve()),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {
                "attempt_id": "preflight", "formatter": "pandoc_bare",
                "error": "Pandoc preflight 编译失败",
                "stderr": result.stderr[:500], "status": "FAILED",
            }

        output_path = Path(output_file)
        return {
            "attempt_id": "preflight", "formatter": "pandoc_bare",
            "input_file": input_file, "output_file": output_file,
            "output_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
            "status": "OK",
        }
    except FileNotFoundError:
        return {"attempt_id": "preflight", "formatter": "pandoc_bare", "error": "Pandoc 未安装", "status": "FAILED"}
    except subprocess.TimeoutExpired:
        return {"attempt_id": "preflight", "formatter": "pandoc_bare", "error": "Pandoc 执行超时", "status": "FAILED"}


def apply_minimax_c2(
    input_file: str,
    output_file: str,
    template_file: str,
    env_ready: bool | None = None,
    cached_analysis: dict | None = None,
) -> dict:
    """minimax-docx C-2 Base-Replace 排版。

    流程：analyze source --json → analyze template --json → apply-template →
          merge-runs → validate --business → gate-check → diff。

    Args:
        input_file: 输入 DOCX 文件路径（通常为 preflight.docx）。
        output_file: 输出终稿.docx 路径。
        template_file: 学校 DOCX 模板路径。
        env_ready: 外部传入的环境就绪状态（None 则内部检查）。
        cached_analysis: 外部缓存的 analyze 结果（None 则内部执行）。
    """
    if not safe_path_exists(input_file):
        return {"attempt_id": "minimax_c2", "formatter": "minimax_c2", "error": f"文件不存在: {input_file}", "status": "FAILED"}

    if not template_path_exists(template_file):
        return {"attempt_id": "minimax_c2", "formatter": "minimax_c2", "error": f"模板不存在: {template_file}", "status": "FAILED"}

    try:
        _validate_path(output_file)
    except ValueError:
        return {"attempt_id": "minimax_c2", "formatter": "minimax_c2", "error": f"输出路径在允许范围外: {output_file}", "status": "FAILED"}

    # 环境检查（使用缓存或内部检查）
    if env_ready is None:
        env_ready = _check_docx_env()
    if not env_ready:
        return {
            "attempt_id": "minimax_c2", "formatter": "minimax_c2",
            "failure_code": "ENV_01", "error": "minimax-docx 环境未就绪", "status": "FAILED",
        }

    input_resolved = str(Path(input_file).resolve())
    template_resolved = str(Path(template_file).resolve())

    try:
        # analyze source（使用缓存或内部执行）
        if cached_analysis and cached_analysis.get("source", {}).get("returncode") == 0:
            pass  # 复用缓存
        else:
            analyze_src = _run_minimax_cli("analyze", "--input", input_resolved, "--json")
            if analyze_src.returncode != 0:
                return {
                    "attempt_id": "minimax_c2", "formatter": "minimax_c2",
                    "failure_code": "DOCX_STYLE_01", "error": "源文件分析失败",
                    "stderr": analyze_src.stderr[:500], "status": "FAILED",
                }

        # analyze template（使用缓存或内部执行）
        if cached_analysis and cached_analysis.get("template", {}).get("returncode") == 0:
            pass  # 复用缓存
        else:
            analyze_tpl = _run_minimax_cli("analyze", "--input", template_resolved, "--json")
            if analyze_tpl.returncode != 0:
                return {
                    "attempt_id": "minimax_c2", "formatter": "minimax_c2",
                    "failure_code": "DOCX_STYLE_01", "error": "模板分析失败",
                    "stderr": analyze_tpl.stderr[:500], "status": "FAILED",
                }

        # 使用原子写入
        def _write_c2(tmp_path: str) -> dict:
            # apply-template（输出到临时路径）
            apply_result = _run_minimax_cli(
                "apply-template",
                "--input", input_resolved,
                "--template", template_resolved,
                "--output", tmp_path,
            )
            if apply_result.returncode != 0:
                stderr_lower = apply_result.stderr.lower() if apply_result.stderr else ""
                if "section" in stderr_lower or "page" in stderr_lower:
                    failure_code = "DOCX_SECTION_01"
                elif "style" in stderr_lower:
                    failure_code = "DOCX_STYLE_01"
                else:
                    failure_code = "DOCX_RENDER_01"
                return {
                    "attempt_id": "minimax_c2", "formatter": "minimax_c2",
                    "failure_code": failure_code, "error": "模板套用失败",
                    "stderr": apply_result.stderr[:500], "status": "FAILED",
                }

            # 验证套件（在临时文件上运行）
            suite = _run_docx_validation_suite(tmp_path, template_file)
            if suite["status"] != "OK":
                return {
                    "attempt_id": "minimax_c2", "formatter": "minimax_c2",
                    "failure_code": "DOCX_RENDER_01",
                    "error": f"验证套件失败: {suite.get('failed_at', 'unknown')}",
                    "validation_steps": suite.get("steps", []),
                    "status": "FAILED",
                }

            # diff 内容完整性
            diff_result = _run_minimax_cli("diff", "--before", input_resolved, "--after", tmp_path)
            tmp_stat = Path(tmp_path).stat() if Path(tmp_path).exists() else None

            return {
                "attempt_id": "minimax_c2", "formatter": "minimax_c2",
                "input_file": input_file, "output_file": tmp_path, "template": template_file,
                "output_size_bytes": tmp_stat.st_size if tmp_stat else 0,
                "validation_steps": suite.get("steps", []),
                "diff_output": diff_result.stdout[:500] if diff_result.returncode == 0 else diff_result.stderr[:500],
                "status": "OK",
            }

        return _safe_write_output(output_file, _write_c2)

    except FileNotFoundError:
        return {"attempt_id": "minimax_c2", "formatter": "minimax_c2", "failure_code": "ENV_01", "error": "dotnet 命令未找到", "status": "FAILED"}
    except subprocess.TimeoutExpired:
        return {"attempt_id": "minimax_c2", "formatter": "minimax_c2", "failure_code": "DOCX_RENDER_01", "error": "minimax-docx 执行超时", "status": "FAILED"}


def apply_minimax_c1(
    input_file: str,
    output_file: str,
    template_file: str,
    env_ready: bool | None = None,
    cached_analysis: dict | None = None,
) -> dict:
    """minimax-docx C-1 Overlay 排版。

    **第二阶段启用**。当前 CLI apply-template 不支持 --mode 参数，
    实际使用 --apply-styles 等独立开关控制。待验证后再启用。

    Args:
        input_file: 输入 DOCX 文件路径。
        output_file: 输出终稿.docx 路径。
        template_file: 学校 DOCX 模板路径。
        env_ready: 外部传入的环境就绪状态。
        cached_analysis: 外部缓存的 analyze 结果。
    """
    if not safe_path_exists(input_file):
        return {"attempt_id": "minimax_c1", "formatter": "minimax_c1", "error": f"文件不存在: {input_file}", "status": "FAILED"}

    if not template_path_exists(template_file):
        return {"attempt_id": "minimax_c1", "formatter": "minimax_c1", "error": f"模板不存在: {template_file}", "status": "FAILED"}

    try:
        _validate_path(output_file)
    except ValueError:
        return {"attempt_id": "minimax_c1", "formatter": "minimax_c1", "error": f"输出路径在允许范围外: {output_file}", "status": "FAILED"}

    if env_ready is None:
        env_ready = _check_docx_env()
    if not env_ready:
        return {
            "attempt_id": "minimax_c1", "formatter": "minimax_c1",
            "failure_code": "ENV_01", "error": "minimax-docx 环境未就绪", "status": "FAILED",
        }

    input_resolved = str(Path(input_file).resolve())
    template_resolved = str(Path(template_file).resolve())
    output_resolved = str(Path(output_file).resolve())

    try:
        # C-1 使用独立开关而非 --mode
        apply_result = _run_minimax_cli(
            "apply-template",
            "--input", input_resolved,
            "--template", template_resolved,
            "--output", output_resolved,
            "--apply-styles", "true",
            "--apply-sections", "false",
            "--apply-headers-footers", "false",
            "--apply-theme", "false",
        )
        if apply_result.returncode != 0:
            return {
                "attempt_id": "minimax_c1", "formatter": "minimax_c1",
                "failure_code": "DOCX_STYLE_01", "error": "C-1 Overlay 模板套用失败",
                "stderr": apply_result.stderr[:500], "status": "FAILED",
            }

        output_path = Path(output_file)
        return {
            "attempt_id": "minimax_c1", "formatter": "minimax_c1",
            "input_file": input_file, "output_file": output_file, "template": template_file,
            "output_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
            "status": "OK",
        }

    except FileNotFoundError:
        return {"attempt_id": "minimax_c1", "formatter": "minimax_c1", "failure_code": "ENV_01", "error": "dotnet 命令未找到", "status": "FAILED"}
    except subprocess.TimeoutExpired:
        return {"attempt_id": "minimax_c1", "formatter": "minimax_c1", "failure_code": "DOCX_RENDER_01", "error": "minimax-docx 执行超时", "status": "FAILED"}


def apply_pandoc_templated(
    input_file: str,
    output_file: str,
    template_file: str | None = None,
) -> dict:
    """Pandoc 带模板排版。"""
    if not safe_path_exists(input_file):
        return {"attempt_id": "pandoc_templated", "formatter": "pandoc_templated", "error": f"文件不存在: {input_file}", "status": "FAILED"}

    if template_file and not template_path_exists(template_file):
        return {"attempt_id": "pandoc_templated", "formatter": "pandoc_templated", "error": f"模板文件不存在: {template_file}", "status": "FAILED"}

    try:
        _validate_path(output_file)
    except ValueError:
        return {"attempt_id": "pandoc_templated", "formatter": "pandoc_templated", "error": f"输出路径在允许范围外: {output_file}", "status": "FAILED"}

    cmd = [
        "pandoc",
        str(Path(input_file).resolve()),
        "-o", str(Path(output_file).resolve()),
    ]

    if template_file:
        cmd.extend(["--reference-doc", str(Path(template_file).resolve())])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {
                "attempt_id": "pandoc_templated", "formatter": "pandoc_templated",
                "error": "Pandoc 编译失败",
                "stderr": result.stderr[:500], "returncode": result.returncode, "status": "FAILED",
            }

        output_path = Path(output_file)
        formatter = "pandoc_templated" if template_file else "pandoc_bare"
        return {
            "attempt_id": formatter, "formatter": formatter,
            "input_file": input_file, "output_file": output_file, "template": template_file,
            "output_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
            "status": "OK",
        }
    except FileNotFoundError:
        return {"attempt_id": "pandoc_templated", "formatter": "pandoc_templated", "error": "Pandoc 未安装", "status": "FAILED"}
    except subprocess.TimeoutExpired:
        return {"attempt_id": "pandoc_templated", "formatter": "pandoc_templated", "error": "Pandoc 执行超时", "status": "FAILED"}
