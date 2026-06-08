"""Unit tests for formatting pipeline helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from paper_tools_mcp.tools import formatting


class FakePath:
    suffix = ".docx"

    def __init__(self, name: str, exists: bool = True, size: int = 4096) -> None:
        self.name = name
        self.exists_value = exists
        self.size = size
        self.unlinked = False
        self.replaced_with: str | None = None
        self.tmp_path: FakePath | None = None

    def exists(self) -> bool:
        return self.exists_value

    def stat(self) -> SimpleNamespace:
        return SimpleNamespace(st_size=self.size)

    def with_suffix(self, suffix: str) -> "FakePath":
        self.tmp_path = FakePath(self.name + suffix, exists=False, size=self.size)
        return self.tmp_path

    def unlink(self) -> None:
        self.unlinked = True
        self.exists_value = False

    def replace(self, target: str) -> None:
        self.replaced_with = target

    def __str__(self) -> str:
        return self.name


class FakeZipFile:
    def __init__(self, names: list[str]) -> None:
        self.names = names

    def __enter__(self) -> "FakeZipFile":
        return self

    def __exit__(self, *_args) -> None:
        return None

    def namelist(self) -> list[str]:
        return self.names


def _patch_verify_path(monkeypatch, fake_path: FakePath) -> FakePath:
    monkeypatch.setattr(formatting, "Path", lambda _path: fake_path)
    return fake_path


def test_verify_docx_minimal_rejects_nonexistent_file(monkeypatch) -> None:
    _patch_verify_path(monkeypatch, FakePath("/safe/out.docx", exists=False))

    result = formatting._verify_docx_minimal("/safe/out.docx")

    assert result == {"valid": False, "reason": "文件不存在"}


def test_verify_docx_minimal_rejects_empty_file(monkeypatch) -> None:
    _patch_verify_path(monkeypatch, FakePath("/safe/out.docx", exists=True, size=0))

    result = formatting._verify_docx_minimal("/safe/out.docx")

    assert result == {"valid": False, "reason": "文件大小为 0"}


def test_verify_docx_minimal_rejects_non_zip_file(monkeypatch) -> None:
    _patch_verify_path(monkeypatch, FakePath("/safe/out.docx", exists=True, size=4096))

    def raise_bad_zip(*_args, **_kwargs):
        raise formatting.zipfile.BadZipFile()

    monkeypatch.setattr(formatting.zipfile, "ZipFile", raise_bad_zip)

    result = formatting._verify_docx_minimal("/safe/out.docx")

    assert result == {"valid": False, "reason": "不是有效的 zip/DOCX 文件"}


def test_verify_docx_minimal_accepts_valid_docx_shape(monkeypatch) -> None:
    _patch_verify_path(monkeypatch, FakePath("/safe/out.docx", exists=True, size=4096))
    monkeypatch.setattr(
        formatting.zipfile,
        "ZipFile",
        lambda *_args, **_kwargs: FakeZipFile(["[Content_Types].xml", "word/document.xml"]),
    )

    result = formatting._verify_docx_minimal("/safe/out.docx")

    assert result == {"valid": True}


def test_safe_write_output_cleans_temp_when_content_writer_fails(monkeypatch) -> None:
    final = FakePath("/safe/final.docx", exists=False)
    monkeypatch.setattr(formatting, "Path", lambda _path: final)

    def writer(tmp_path: str) -> dict:
        assert tmp_path == str(final.tmp_path)
        final.tmp_path.exists_value = True
        return {"status": "FAILED", "error": "writer failed"}

    result = formatting._safe_write_output("/safe/final.docx", writer)

    assert result == {"status": "FAILED", "error": "writer failed"}
    assert final.tmp_path is not None
    assert final.tmp_path.unlinked is True


def test_safe_write_output_cleans_temp_when_safety_check_fails(monkeypatch) -> None:
    final = FakePath("/safe/final.docx", exists=False)
    monkeypatch.setattr(formatting, "Path", lambda _path: final)
    monkeypatch.setattr(
        formatting,
        "_verify_docx_minimal",
        lambda _path: {"valid": False, "reason": "不是有效的 zip/DOCX 文件"},
    )

    def writer(tmp_path: str) -> dict:
        assert tmp_path == str(final.tmp_path)
        final.tmp_path.exists_value = True
        return {"status": "OK", "output_file": tmp_path}

    result = formatting._safe_write_output("/safe/final.docx", writer)

    assert result["status"] == "FAILED"
    assert "输出文件安全检查失败" in result["error"]
    assert final.tmp_path is not None
    assert final.tmp_path.unlinked is True
    assert final.tmp_path.replaced_with is None


@pytest.mark.parametrize(
    "formatter",
    [formatting.apply_minimax_c2, formatting.apply_minimax_c1],
)
def test_minimax_formatters_use_template_path_check(monkeypatch, formatter) -> None:
    monkeypatch.setattr(formatting, "safe_path_exists", lambda _path: True)
    monkeypatch.setattr(formatting, "template_path_exists", lambda _path: False)

    result = formatter(
        "/safe/input.docx",
        "/safe/out.docx",
        "/templates/outside.docx",
        env_ready=True,
    )

    assert result["status"] == "FAILED"
    assert "模板不存在" in result["error"]
