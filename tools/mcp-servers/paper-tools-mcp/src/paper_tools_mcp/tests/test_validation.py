"""Unit tests for DOCX validation helpers."""

from __future__ import annotations

from pathlib import Path

from paper_tools_mcp.tests.conftest import MockDocument, MockParagraph, MockRun
from paper_tools_mcp.tools import literature
from paper_tools_mcp.tools import validation


def test_is_heading_style_recognizes_english_and_numeric_ids() -> None:
    assert validation._is_heading_style("Heading 1", None) is True
    assert validation._is_heading_style("", "1") is True
    assert validation._is_heading_style("", "4") is False
    assert validation._is_heading_style("Normal", None) is False


def test_load_docx_uses_template_path_check(monkeypatch, mock_docx_module) -> None:
    mock_docx_module(MockDocument())
    monkeypatch.setattr(validation, "safe_path_exists", lambda _path: True)
    monkeypatch.setattr(validation, "template_path_exists", lambda _path: False)

    assert validation._load_docx("/templates/outside.docx", template=True) is None


def test_load_docx_returns_document_when_template_path_valid(monkeypatch, mock_docx_module) -> None:
    doc = MockDocument()
    mock_docx_module(doc)
    monkeypatch.setattr(validation, "safe_path_exists", lambda _path: False)
    monkeypatch.setattr(validation, "template_path_exists", lambda _path: True)

    result = validation._load_docx("/templates/school.docx", template=True)

    assert result is doc


def test_load_docx_returns_document_when_regular_path_valid(monkeypatch, mock_docx_module) -> None:
    doc = MockDocument()
    mock_docx_module(doc)
    monkeypatch.setattr(validation, "safe_path_exists", lambda _path: True)
    monkeypatch.setattr(validation, "template_path_exists", lambda _path: False)

    result = validation._load_docx("/safe/output.docx", template=False)

    assert result is doc


def test_validate_docx_fonts_reviews_missing_east_asia(monkeypatch, mock_docx_module) -> None:
    doc = MockDocument(
        paragraphs=[
            MockParagraph("正文", runs=[MockRun("正文", east_asia=None)]),
        ],
    )
    mock_docx_module(doc)
    monkeypatch.setattr(validation, "safe_path_exists", lambda _path: True)

    result = validation.validate_docx_fonts("/safe/out.docx", "/templates/school.docx")

    assert result["status"] == "REVIEW"
    assert "DOCX_FONT_01" in result["failure_codes"]


def test_validate_docx_references_reviews_missing_reference_section(monkeypatch, mock_docx_module) -> None:
    doc = MockDocument(
        paragraphs=[
            MockParagraph("第一章 绪论"),
            MockParagraph("正文段落"),
        ],
    )
    mock_docx_module(doc)
    monkeypatch.setattr(validation, "safe_path_exists", lambda _path: True)

    result = validation.validate_docx_references("/safe/out.docx")

    assert result["status"] == "REVIEW"
    assert "DOCX_REF_01" in result["failure_codes"]


def test_post_validate_docx_strict_mode_single_review_fails(monkeypatch) -> None:
    def pass_check(*_args, **_kwargs):
        return {"status": "PASS", "failure_codes": []}

    def review_check(*_args, **_kwargs):
        return {"status": "REVIEW", "failure_codes": ["DOCX_FONT_01"]}

    monkeypatch.setattr(validation, "validate_docx_styles", pass_check)
    monkeypatch.setattr(validation, "validate_docx_sections", pass_check)
    monkeypatch.setattr(validation, "validate_docx_fonts", review_check)
    monkeypatch.setattr(validation, "validate_docx_references", pass_check)
    monkeypatch.setattr(validation, "validate_docx_layout", pass_check)

    result = validation.post_validate_docx("/safe/out.docx", "/templates/school.docx", validation_mode="strict")

    assert result["raw_status"] == "REVIEW"
    assert result["status"] == "FAILED"
    assert result["overall_failure_codes"] == ["DOCX_FONT_01"]


def test_post_validate_docx_compat_mode_single_review_remains_review(monkeypatch) -> None:
    def pass_check(*_args, **_kwargs):
        return {"status": "PASS", "failure_codes": []}

    def review_check(*_args, **_kwargs):
        return {"status": "REVIEW", "failure_codes": ["DOCX_FONT_01"]}

    monkeypatch.setattr(validation, "validate_docx_styles", pass_check)
    monkeypatch.setattr(validation, "validate_docx_sections", pass_check)
    monkeypatch.setattr(validation, "validate_docx_fonts", review_check)
    monkeypatch.setattr(validation, "validate_docx_references", pass_check)
    monkeypatch.setattr(validation, "validate_docx_layout", pass_check)

    result = validation.post_validate_docx("/safe/out.docx", "/templates/school.docx", validation_mode="compat")

    assert result["raw_status"] == "REVIEW"
    assert result["status"] == "REVIEW"
    assert result["overall_failure_codes"] == ["DOCX_FONT_01"]


def test_validate_chapter_citations_uses_current_chapter_registry_rows(monkeypatch) -> None:
    chapter_path = "/safe/第2章_方法.md"
    registry_path = "/safe/_引用编号注册表.md"
    files = {
        chapter_path: "# 第2章 方法\n正文引用 [3][4][5]\n",
        registry_path: (
            "# 引用编号注册表\n\n"
            "| 编号 | cite_key | 首次出现章节 |\n"
            "|------|----------|-------------|\n"
            "| 1 | A_2024_1 | 第1章 |\n"
            "| 2 | B_2024_1 | 第1章 |\n"
            "| 3 | C_2024_1 | 第2章 |\n"
            "| 4 | D_2024_1 | 第2章 |\n"
            "| 5 | E_2024_1 | 第2章 |\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))

    result = validation.validate_chapter_citations(chapter_path, registry_path)

    assert result["status"] == "PASS"
    assert result["current_chapter_nums"] == [3, 4, 5]


def test_validate_chapter_citations_reports_cards_error(monkeypatch) -> None:
    chapter_path = "/safe/第2章_方法.md"
    registry_path = "/safe/_引用编号注册表.md"
    files = {
        chapter_path: "# 第2章 方法\n正文引用 [2]\n",
        registry_path: (
            "# 引用编号注册表\n\n"
            "| 编号 | cite_key | 首次出现章节 |\n"
            "|------|----------|-------------|\n"
            "| 1 | A_2024_1 | 第1章 |\n"
            "| 2 | B_2024_1 | 第1章 |\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))
    monkeypatch.setattr(literature, "get_literature_cards", lambda _path: {"error": "boom"})

    result = validation.validate_chapter_citations(
        chapter_path,
        registry_path,
        cards_dir="/safe/cards",
    )

    assert result["status"] == "REVISE"
    assert any("boom" in issue for issue in result["issues"])


def test_parse_registry_entries_supports_two_and_three_columns() -> None:
    reg_text = (
        "| 编号 | cite_key | 首次出现章节 |\n"
        "|------|----------|-------------|\n"
        "| 1 | A_2024_1 | 第1章 |\n"
        "| 2 | B_2024_1 |\n"
    )

    result = validation._parse_registry_entries(reg_text)

    assert result == [
        {"num": 1, "cite_key": "A_2024_1", "first_chapter": "第1章"},
        {"num": 2, "cite_key": "B_2024_1", "first_chapter": ""},
    ]


def test_validate_chapter_citations_reports_fallback_mode_without_chapter_label(monkeypatch) -> None:
    chapter_path = "/safe/chapter_without_label.md"
    registry_path = "/safe/_引用编号注册表.md"
    files = {
        chapter_path: "正文引用 [4][6]\n",
        registry_path: (
            "| 编号 | cite_key | 首次出现章节 |\n"
            "|------|----------|-------------|\n"
            "| 1 | A_2024_1 | 第1章 |\n"
            "| 2 | B_2024_1 | 第1章 |\n"
            "| 3 | C_2024_1 | 第1章 |\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))

    result = validation.validate_chapter_citations(chapter_path, registry_path)

    assert result["validation_mode"] == "legacy_diff_fallback"
    assert result["status"] == "REVISE"
    assert any("新编号不连续" in issue for issue in result["issues"])


def test_validate_chapter_citations_reports_unregistered_numbers(monkeypatch) -> None:
    chapter_path = "/safe/第2章_方法.md"
    registry_path = "/safe/_引用编号注册表.md"
    files = {
        chapter_path: "# 第2章 方法\n正文引用 [2][9]\n",
        registry_path: (
            "| 编号 | cite_key | 首次出现章节 |\n"
            "|------|----------|-------------|\n"
            "| 1 | A_2024_1 | 第1章 |\n"
            "| 2 | B_2024_1 | 第1章 |\n"
            "| 3 | C_2024_1 | 第1章 |\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))

    result = validation.validate_chapter_citations(chapter_path, registry_path)

    assert result["status"] == "REVISE"
    assert any("未登记的编号: [9]" in issue for issue in result["issues"])


def test_validate_citation_order_reports_missing_and_extra_entries(monkeypatch) -> None:
    doc_path = "/safe/full.md"
    files = {
        doc_path: (
            "# 正文\n"
            "先引用 [1]，再引用 [2]，最后引用 [3]。\n\n"
            "# 参考文献\n"
            "[1] 作者甲. 文献甲.\n"
            "[3] 作者丙. 文献丙.\n"
            "[9] 作者外. 文献外.\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))

    result = validation.validate_citation_order(doc_path)

    assert result["status"] == "REVISE"
    assert any("缺失正文已引用条目: [2]" in issue for issue in result["issues"])
    assert any("存在正文未引用条目: [9]" in issue for issue in result["issues"])


def test_validate_citation_order_reports_position_violations(monkeypatch) -> None:
    doc_path = "/safe/full.md"
    files = {
        doc_path: (
            "# 正文\n"
            "先引用 [1]，再引用 [3]，最后引用 [2]。\n\n"
            "# 参考文献\n"
            "[1] 作者甲. 文献甲.\n"
            "[2] 作者乙. 文献乙.\n"
            "[3] 作者丙. 文献丙.\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))

    result = validation.validate_citation_order(doc_path)

    assert result["status"] == "REVISE"
    assert result["order_check"]["violations"]
    assert any("位置错误" in issue for issue in result["issues"])


def test_validate_citation_order_passes_happy_path(monkeypatch) -> None:
    doc_path = "/safe/full.md"
    files = {
        doc_path: (
            "# 正文\n"
            "先引用 [1]，再引用 [3]，最后引用 [2]。\n\n"
            "# 参考文献\n"
            "[1] 作者甲. 文献甲.\n"
            "[3] 作者丙. 文献丙.\n"
            "[2] 作者乙. 文献乙.\n"
        ),
    }

    monkeypatch.setattr(validation, "safe_read", lambda path: (path, files[path]))

    result = validation.validate_citation_order(doc_path)

    assert result["status"] == "PASS"
    assert result["issues"] == []


def test_build_reference_list_marks_legacy_stem_mismatch(monkeypatch) -> None:
    registry_path = "/safe/_引用编号注册表.md"
    registry_text = (
        "# 引用编号注册表\n\n"
        "| 编号 | cite_key | 首次出现章节 |\n"
        "|------|----------|-------------|\n"
        "| 1 | Zhang_2023_1 | 第1章 |\n"
    )

    monkeypatch.setattr(literature, "safe_read", lambda path: (path, registry_text))
    monkeypatch.setattr(
        literature,
        "get_literature_cards",
        lambda _path: {
            "cards": [
                {
                    "file": "Zhang_2023.md",
                    "cite_key": "Zhang_2023",
                    "author": "张三",
                    "title": "旧卡片",
                },
            ],
        },
    )

    result = literature.build_reference_list(registry_path, "/safe/cards")

    assert result["status"] == "REVISE"
    assert result["missing_cards"] == ["Zhang_2023_1"]
    assert "旧版文件名" in result["missing_details"][0]["reason"]


def test_get_literature_cards_returns_error_when_single_file_is_broken(monkeypatch) -> None:
    broken_path = Path("/safe/cards/broken.md")

    monkeypatch.setattr(literature, "safe_list_dir", lambda _dir, _glob: [broken_path])

    def broken_safe_read(path: str):
        raise ValueError(f"坏文件: {path}")

    monkeypatch.setattr(literature, "safe_read", broken_safe_read)

    result = literature.get_literature_cards("/safe/cards")

    assert "error" in result
    assert "broken.md" in result["error"]
