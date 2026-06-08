"""Unit tests for retry and pipeline orchestration."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_tools_mcp.tools import formatting, retry, validation


INPUT_FILE = "/safe/input.md"
OUTPUT_DIR = "/safe/output"
TEMPLATE_FILE = "/templates/school.docx"
MISSING_TEMPLATE = "/templates/missing.docx"


def _install_pipeline_mocks(
    monkeypatch,
    *,
    template_exists: bool = True,
    env_ready: bool = False,
    main_result: dict | None = None,
    fallback_result: dict | None = None,
    post_statuses: list[str] | None = None,
    output_dir_allowed: bool = True,
) -> dict:
    calls = {"pandoc": 0, "minimax_c2": 0, "post_validate": 0, "cleanup": []}
    post_statuses = post_statuses if post_statuses is not None else ["PASS"]

    monkeypatch.setattr(retry, "safe_path_exists", lambda path: path == INPUT_FILE)
    monkeypatch.setattr(retry, "template_path_exists", lambda path: template_exists and path == TEMPLATE_FILE)
    monkeypatch.setattr(retry.os, "makedirs", lambda *_args, **_kwargs: None)

    def fake_validate_path(path: str) -> Path:
        if not output_dir_allowed:
            raise ValueError("outside sandbox")
        return Path(path)

    monkeypatch.setattr(retry, "_validate_path", fake_validate_path)
    monkeypatch.setattr(retry, "_cleanup_failed_output", lambda path: calls["cleanup"].append(path))
    monkeypatch.setattr(
        retry,
        "_analyze_template",
        lambda *_args, **_kwargs: {"source": {"returncode": 0}, "template": {"returncode": 0}},
    )
    monkeypatch.setattr(formatting, "_check_docx_env", lambda: env_ready)
    monkeypatch.setattr(
        formatting,
        "build_preflight_docx",
        lambda _input, output: {"status": "OK", "output_file": output},
    )

    def fake_minimax_c2(*_args, **_kwargs) -> dict:
        calls["minimax_c2"] += 1
        return main_result or {"status": "OK", "output_file": _args[1]}

    def fake_pandoc(_input: str, output: str, template_file: str | None = None) -> dict:
        calls["pandoc"] += 1
        if template_file and not template_exists:
            return {
                "status": "FAILED",
                "error": f"模板文件不存在: {template_file}",
                "failure_code": "DOCX_RENDER_01",
            }
        if env_ready:
            return fallback_result or {"status": "OK", "output_file": output}
        if calls["pandoc"] == 1:
            return main_result or {"status": "OK", "output_file": output}
        return fallback_result or {"status": "OK", "output_file": output}

    def fake_post_validate(docx_path: str, spec_path: str | None, validation_mode: str = "strict") -> dict:
        calls["post_validate"] += 1
        status = post_statuses[min(calls["post_validate"] - 1, len(post_statuses) - 1)]
        return {
            "docx_path": docx_path,
            "status": status,
            "validation_mode": validation_mode,
            "overall_failure_codes": [] if status == "PASS" else ["DOCX_FONT_01"],
        }

    monkeypatch.setattr(formatting, "apply_minimax_c2", fake_minimax_c2)
    monkeypatch.setattr(formatting, "apply_pandoc_templated", fake_pandoc)
    monkeypatch.setattr(validation, "post_validate_docx", fake_post_validate)

    return calls


def test_should_fallback_only_for_all_fallback_codes() -> None:
    assert retry.should_fallback(["DOCX_STYLE_01", "DOCX_RENDER_01"]) is True
    assert retry.should_fallback(["DOCX_RENDER_01", "CLI_01"]) is False
    assert retry.should_fallback(["DOCX_RENDER_01", "MD_STRUCT_01"]) is False
    assert retry.should_fallback([]) is False


def test_run_format_pipeline_strict_mode_missing_template_fails(monkeypatch) -> None:
    _install_pipeline_mocks(monkeypatch, template_exists=False)

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=MISSING_TEMPLATE,
        validation_mode="strict",
    )

    assert result["status"] == "FAILED"
    assert result["validation_mode"] == "strict"
    assert "template_file" in result["error"]


def test_run_format_pipeline_compat_missing_template_path_fails_at_formatter(monkeypatch) -> None:
    _install_pipeline_mocks(monkeypatch, template_exists=False)

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=MISSING_TEMPLATE,
        validation_mode="compat",
    )

    assert result["status"] == "FAILED"
    assert result["validation_mode"] == "compat"


def test_run_format_pipeline_env_ready_invalid_template_records_pandoc_attempt(monkeypatch) -> None:
    calls = _install_pipeline_mocks(monkeypatch, template_exists=False, env_ready=True)

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=MISSING_TEMPLATE,
        validation_mode="compat",
    )

    assert result["status"] == "FAILED"
    assert result["summary"]["attempts"][0]["formatter"] == "pandoc_templated"
    assert calls["minimax_c2"] == 0


def test_run_format_pipeline_main_chain_ok_and_post_validation_pass_returns_ok(monkeypatch) -> None:
    _install_pipeline_mocks(monkeypatch, post_statuses=["PASS"])

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=TEMPLATE_FILE,
        validation_mode="strict",
    )

    assert result["status"] == "OK"
    assert result["output_file"].endswith("论文终稿_标准版.docx")


def test_run_format_pipeline_main_chain_ok_and_post_validation_review_strict_fails(monkeypatch) -> None:
    _install_pipeline_mocks(monkeypatch, post_statuses=["REVIEW"])

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=TEMPLATE_FILE,
        validation_mode="strict",
    )

    assert result["status"] == "FAILED"
    assert result["validation_mode"] == "strict"


def test_run_format_pipeline_main_chain_ok_and_post_validation_review_compat_reviews(monkeypatch) -> None:
    _install_pipeline_mocks(monkeypatch, post_statuses=["REVIEW"])

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=TEMPLATE_FILE,
        validation_mode="compat",
    )

    assert result["status"] == "REVIEW"
    assert result["validation_mode"] == "compat"
    assert result["output_file"].endswith("论文终稿_标准版.docx")


def test_run_format_pipeline_main_chain_fails_and_fallback_ok_returns_ok(monkeypatch) -> None:
    _install_pipeline_mocks(
        monkeypatch,
        env_ready=True,
        main_result={"status": "FAILED", "failure_code": "DOCX_RENDER_01", "error": "render failed"},
        fallback_result={"status": "OK"},
        post_statuses=["PASS"],
    )

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir=OUTPUT_DIR,
        template_file=TEMPLATE_FILE,
        validation_mode="strict",
    )

    assert result["status"] == "OK"
    assert result["output_file"].endswith("论文终稿_标准版_fallback.docx")
    assert result["summary"]["degraded"] is True


def test_run_format_pipeline_output_dir_path_traversal_fails(monkeypatch) -> None:
    _install_pipeline_mocks(monkeypatch, output_dir_allowed=False)

    result = retry.run_format_pipeline(
        INPUT_FILE,
        output_dir="/safe/../outside",
        template_file=TEMPLATE_FILE,
        validation_mode="strict",
    )

    assert result["status"] == "FAILED"
    assert "输出路径在允许范围外" in result["error"]


def test_format_attempt_defaults_success_false() -> None:
    attempt = retry.FormatAttempt(
        attempt_id="attempt_1",
        formatter="pandoc_templated",
        docx_path="/safe/out.docx",
    )

    assert attempt.success is False
    assert attempt.failure_codes == []
    assert attempt.timestamp
