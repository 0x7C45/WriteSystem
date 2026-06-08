"""Shared pytest fixtures for paper-tools-mcp unit tests."""

from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace

import pytest


class MockStyle:
    def __init__(self, name: str = "Normal", style_id: str | None = None, style_type: int = 1) -> None:
        self.name = name
        self.style_id = style_id
        self.type = style_type


class MockFonts:
    def __init__(self, east_asia: str | None = None) -> None:
        self.east_asia = east_asia

    def get(self, _name: str) -> str | None:
        return self.east_asia


class MockRunProperties:
    def __init__(self, east_asia: str | None = None) -> None:
        self.east_asia = east_asia

    def find(self, name: str) -> MockFonts | None:
        if name.endswith("rFonts"):
            return MockFonts(self.east_asia)
        return None


class MockRunElement:
    def __init__(self, east_asia: str | None = None) -> None:
        self.east_asia = east_asia

    def find(self, name: str) -> MockRunProperties | None:
        if name.endswith("rPr"):
            return MockRunProperties(self.east_asia)
        return None


class MockRun:
    def __init__(self, text: str, east_asia: str | None = None) -> None:
        self.text = text
        self._element = MockRunElement(east_asia)


class MockParagraph:
    def __init__(
        self,
        text: str,
        style_name: str | None = "Normal",
        style_id: str | None = None,
        runs: list[MockRun] | None = None,
    ) -> None:
        self.text = text
        self.style = MockStyle(style_name, style_id) if style_name is not None else None
        self.runs = runs if runs is not None else ([MockRun(text)] if text else [])


class MockSection:
    def __init__(
        self,
        page_width: int = 7772400,
        page_height: int = 10058400,
        top_margin: int = 914400,
        bottom_margin: int = 914400,
        left_margin: int = 914400,
        right_margin: int = 914400,
        orientation: int = 0,
    ) -> None:
        self.page_width = page_width
        self.page_height = page_height
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.orientation = orientation


class MockDocument:
    def __init__(
        self,
        paragraphs: list[MockParagraph] | None = None,
        sections: list[MockSection] | None = None,
        styles: list[MockStyle] | None = None,
    ) -> None:
        self.paragraphs = paragraphs if paragraphs is not None else []
        self.sections = sections if sections is not None else [MockSection()]
        self.styles = styles if styles is not None else []


@pytest.fixture
def mock_docx_module(monkeypatch):
    def install(document: MockDocument) -> MockDocument:
        monkeypatch.setitem(sys.modules, "docx", SimpleNamespace(Document=lambda _path: document))
        return document

    return install


@pytest.fixture
def mock_completed_process():
    def make(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(args=["mock"], returncode=returncode, stdout=stdout, stderr=stderr)

    return make
