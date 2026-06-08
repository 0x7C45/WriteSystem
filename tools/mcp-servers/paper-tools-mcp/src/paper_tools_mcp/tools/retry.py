"""排版重试管理器：失败码定义、单次 fallback、历史记录。

第一阶段：minimax_c2 → (失败) → pandoc_templated → (失败) → 人工处理。
仅支持一次 fallback，不做多层递归重试。
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from paper_tools_mcp.utils.safe_path import safe_path_exists, template_path_exists, _validate_path


# ── 失败码定义 ────────────────────────────────────────────────

FAILURE_CODES: dict[str, dict[str, str]] = {
    # docx 样式
    "DOCX_STYLE_01": {"severity": "high", "action": "fallback", "description": "关键样式缺失（无标题段落）"},
    "DOCX_STYLE_02": {"severity": "medium", "action": "fallback", "description": "正文段落样式未命中"},
    "DOCX_STYLE_03": {"severity": "medium", "action": "review", "description": "标题样式层级异常"},
    # docx 页面
    "DOCX_SECTION_01": {"severity": "high", "action": "fallback", "description": "分节数量不符"},
    "DOCX_LAYOUT_01": {"severity": "medium", "action": "review", "description": "页边距不符"},
    # docx 字体/参考文献（第二阶段实现）
    "DOCX_FONT_01": {"severity": "medium", "action": "review", "description": "字体映射异常"},
    "DOCX_REF_01": {"severity": "medium", "action": "review", "description": "参考文献样式异常"},
    # Markdown 层
    "MD_STRUCT_01": {"severity": "high", "action": "block", "description": "Markdown 标题层级错误"},
    "MD_ASSET_01": {"severity": "medium", "action": "block", "description": "图片/脚注/公式引用缺失"},
    # 环境/CLI
    "ENV_01": {"severity": "high", "action": "fail", "description": ".NET 环境不可用"},
    "CLI_01": {"severity": "high", "action": "fail", "description": "DOCX 文件无法打开"},
    "DOCX_RENDER_01": {"severity": "low", "action": "fallback", "description": "渲染异常"},
}

# action 含义：
# "fallback" — 执行一次 pandoc_templated fallback
# "review"   — 标记人工复核，不自动降级
# "block"    — Gate 1 拦截，不进入排版
# "fail"     — 直接失败，人工处理


# ── 尝试记录 ──────────────────────────────────────────────────


@dataclass
class FormatAttempt:
    """记录单次排版尝试。"""
    attempt_id: str
    formatter: str
    docx_path: str
    success: bool = False
    failure_codes: list[str] = field(default_factory=list)
    error_message: str = ""
    post_validation: dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# ── 降级调度器（简化版） ────────────────────────────────────────


def should_fallback(failure_codes: list[str]) -> bool:
    """判断是否应执行一次 fallback。

    只有当所有 failure code 的 action 为 "fallback" 时才降级。
    任一 code 的 action 为 "fail" 或 "block" 则不降级。
    """
    if not failure_codes:
        return False

    for code in failure_codes:
        info = FAILURE_CODES.get(code, {})
        action = info.get("action", "fail")
        if action in ("fail", "block"):
            return False

    # 至少有一个 fallback 类的 code
    return any(
        FAILURE_CODES.get(c, {}).get("action") == "fallback"
        for c in failure_codes
    )


def get_history_summary(attempts: list[FormatAttempt]) -> dict:
    """生成排版历程摘要。"""
    success_attempt = next((a for a in attempts if a.success), None)
    final_attempt = attempts[-1] if attempts else None

    return {
        "total_attempts": len(attempts),
        "success": success_attempt is not None,
        "final_formatter": success_attempt.formatter if success_attempt else (final_attempt.formatter if final_attempt else None),
        "degraded": len(attempts) > 1,
        "attempts": [
            {
                "attempt_id": a.attempt_id,
                "formatter": a.formatter,
                "success": a.success,
                "failure_codes": a.failure_codes,
                "error": a.error_message,
                "timestamp": a.timestamp,
            }
            for a in attempts
        ],
    }


# ── MCP 工具：排版主链编排 ────────────────────────────────────


def run_format_pipeline(
    input_file: str,
    output_dir: str | None = None,
    template_file: str | None = None,
    spec_path: str | None = None,
    validation_mode: Literal["strict", "compat"] = "strict",
) -> dict:
    """排版主链：preflight → minimax C-2 → 验证套件 → 失败则单次 fallback。

    Args:
        input_file: 输入 Markdown 文件路径。
        output_dir: 输出目录（默认为输入文件同级目录下的 output/）。
        template_file: 学校 DOCX 模板路径。strict 模式下必须有。
        spec_path: 格式规范文件路径（仅用于 Markdown 级参考，非 DOCX 模板）。
        validation_mode: "strict"（默认）或 "compat"。
            strict: 缺少 template_file 或 REVIEW → FAILED
            compat: REVIEW → REVIEW；缺少/无效 template_file 不提前失败，但后续排版可能失败
    """
    from paper_tools_mcp.tools.formatting import (
        build_preflight_docx,
        apply_minimax_c2,
        apply_pandoc_templated,
    )
    from paper_tools_mcp.tools.validation import post_validate_docx

    if validation_mode not in ("strict", "compat"):
        validation_mode = "strict"

    if not safe_path_exists(input_file):
        return {"status": "FAILED", "error": f"文件不存在: {input_file}"}

    template_available = bool(template_file and template_path_exists(template_file))

    # strict 模式下缺少模板直接失败
    if validation_mode == "strict" and not template_available:
        return {
            "status": "FAILED",
            "error": "strict 模式下必须提供 template_file",
            "validation_mode": validation_mode,
        }

    input_path = Path(input_file).resolve()
    if output_dir is None:
        output_dir = str(input_path.parent / "output")

    # 验证 output_dir 在允许范围内
    try:
        _validate_path(output_dir)
    except ValueError:
        return {"status": "FAILED", "error": f"输出路径在允许范围外: {output_dir}"}

    os.makedirs(output_dir, exist_ok=True)

    preflight_path = str(Path(output_dir) / "preflight.docx")
    final_path = str(Path(output_dir) / "论文终稿_标准版.docx")
    fallback_path = str(Path(output_dir) / "论文终稿_标准版_fallback.docx")

    attempts: list[FormatAttempt] = []

    # Step 1: 环境检查（仅一次）
    from paper_tools_mcp.tools.formatting import _check_docx_env
    env_ready = _check_docx_env()

    # Step 2: 构建 preflight
    preflight_result = build_preflight_docx(input_file, preflight_path)
    if preflight_result.get("status") != "OK":
        return {
            "status": "FAILED",
            "error": "Preflight 构建失败",
            "preflight_result": preflight_result,
            "validation_mode": validation_mode,
            "summary": get_history_summary(attempts),
        }

    # Step 3: 分析模板（仅一次，缓存结果）
    cached_analysis: dict | None = None
    if env_ready and template_available:
        cached_analysis = _analyze_template(preflight_path, template_file)

    # 用于 docx 后置校验的模板路径（统一使用 template_file，不用 spec_path）
    docx_spec = template_file if template_available else None

    # Step 4: 主链 — apply_minimax_c2
    used_minimax_c2 = env_ready and template_available
    if used_minimax_c2:
        result = apply_minimax_c2(
            preflight_path, final_path, template_file,
            env_ready=True, cached_analysis=cached_analysis,
        )
    else:
        # 无模板或环境不可用，直接走 pandoc
        result = apply_pandoc_templated(input_file, final_path, template_file)

    attempt = FormatAttempt(
        attempt_id="attempt_1",
        formatter="minimax_c2" if used_minimax_c2 else ("pandoc_templated" if template_file else "pandoc_bare"),
        docx_path=final_path,
    )

    if result.get("status") == "OK":
        # 后置校验（使用 template_file，不再依赖 spec_path 存在）
        attempt.post_validation = post_validate_docx(final_path, docx_spec, validation_mode=validation_mode)
        overall = attempt.post_validation.get("status", "UNKNOWN")
        fc = attempt.post_validation.get("overall_failure_codes", [])
        if overall == "PASS":
            attempt.success = True
        else:
            attempt.success = False
            attempt.failure_codes = fc
            # compat 模式下 REVIEW 产物保留供人工复核
            if not (validation_mode == "compat" and overall == "REVIEW"):
                _cleanup_failed_output(final_path)
    else:
        attempt.error_message = result.get("error", "未知错误")
        code = result.get("failure_code", "DOCX_RENDER_01")
        attempt.failure_codes = [code] if code else ["DOCX_RENDER_01"]
        # 清理主链可能的残留文件
        _cleanup_failed_output(final_path)

    attempts.append(attempt)

    # Step 5: 若主链失败，判断是否 fallback
    if not attempt.success and should_fallback(attempt.failure_codes):
        fallback_attempt = FormatAttempt(
            attempt_id="attempt_2",
            formatter="pandoc_templated",
            docx_path=fallback_path,
        )

        fb_result = apply_pandoc_templated(input_file, fallback_path, template_file)

        if fb_result.get("status") == "OK":
            fallback_attempt.post_validation = post_validate_docx(fallback_path, docx_spec, validation_mode=validation_mode)
            overall = fallback_attempt.post_validation.get("status", "UNKNOWN")
            fc = fallback_attempt.post_validation.get("overall_failure_codes", [])
            if overall == "PASS":
                fallback_attempt.success = True
            else:
                fallback_attempt.success = False
                fallback_attempt.failure_codes = fc
            if not fallback_attempt.success:
                if not (validation_mode == "compat" and overall == "REVIEW"):
                    _cleanup_failed_output(fallback_path)
        else:
            fallback_attempt.error_message = fb_result.get("error", "未知错误")
            fallback_attempt.failure_codes = ["DOCX_RENDER_01"]
            _cleanup_failed_output(fallback_path)

        attempts.append(fallback_attempt)

    # 汇总
    summary = get_history_summary(attempts)
    success_attempt = next((a for a in attempts if a.success), None)

    if success_attempt:
        return {
            "status": "OK",
            "output_file": success_attempt.docx_path,
            "preflight_file": preflight_path,
            "validation_mode": validation_mode,
            "summary": summary,
        }

    # 兼容模式下 REVIEW 返回可人工复核的产物；strict 模式下 REVIEW 已映射为 FAILED
    if validation_mode == "compat":
        review_attempt = next(
            (a for a in attempts if a.post_validation.get("status") == "REVIEW"),
            None,
        )
        if review_attempt:
            return {
                "status": "REVIEW",
                "output_file": review_attempt.docx_path,
                "preflight_file": preflight_path,
                "validation_mode": validation_mode,
                "summary": summary,
            }

    return {
        "status": "FAILED",
        "preflight_file": preflight_path,
        "error": "排版失败（主链 + fallback 均未通过校验）",
        "validation_mode": validation_mode,
        "summary": summary,
    }


def _cleanup_failed_output(file_path: str) -> None:
    """安全删除失败的输出文件。"""
    try:
        p = _validate_path(file_path)
        if p.is_file():
            p.unlink()
    except (OSError, ValueError):
        pass


def _analyze_template(source_path: str, template_path: str) -> dict:
    """执行一次模板分析，缓存结果。"""
    from paper_tools_mcp.tools.formatting import _run_minimax_cli

    analysis: dict = {}

    src_resolved = str(Path(source_path).resolve())
    tpl_resolved = str(Path(template_path).resolve())

    analyze_src = _run_minimax_cli("analyze", "--input", src_resolved, "--json")
    analysis["source"] = {
        "returncode": analyze_src.returncode,
        "stdout": analyze_src.stdout[:1000] if analyze_src.returncode == 0 else "",
        "stderr": analyze_src.stderr[:500] if analyze_src.returncode != 0 else "",
    }

    analyze_tpl = _run_minimax_cli("analyze", "--input", tpl_resolved, "--json")
    analysis["template"] = {
        "returncode": analyze_tpl.returncode,
        "stdout": analyze_tpl.stdout[:1000] if analyze_tpl.returncode == 0 else "",
        "stderr": analyze_tpl.stderr[:500] if analyze_tpl.returncode != 0 else "",
    }

    return analysis
