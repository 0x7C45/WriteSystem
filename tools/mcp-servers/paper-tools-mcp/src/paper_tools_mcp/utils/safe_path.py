"""paper-tools-mcp: 论文工具 MCP Server — 安全路径工具。"""

import os
from pathlib import Path


# 允许访问的基础目录（通过环境变量配置，默认为当前工作目录）
_ALLOWED_BASE: Path | None = None


def get_allowed_base() -> Path:
    """获取允许访问的基础目录。"""
    global _ALLOWED_BASE
    if _ALLOWED_BASE is None:
        env_dir = os.environ.get("PAPER_TOOLS_BASE_DIR", "")
        _ALLOWED_BASE = Path(env_dir).resolve() if env_dir else Path.cwd().resolve()
    return _ALLOWED_BASE


def set_allowed_base(directory: str | Path) -> None:
    """设置允许访问的基础目录。"""
    global _ALLOWED_BASE
    _ALLOWED_BASE = Path(directory).resolve()


def safe_read(file_path: str, encoding: str = 'utf-8') -> tuple[Path, str]:
    """安全读取文件，验证路径在允许范围内。

    Returns:
        (resolved_path, file_content)

    Raises:
        ValueError: 路径在允许范围外或文件不存在。
    """
    resolved = _validate_path(file_path)
    if not resolved.exists():
        raise ValueError(f"文件不存在: {file_path}")
    return resolved, resolved.read_text(encoding=encoding)


def safe_write(file_path: str, content: str, encoding: str = 'utf-8') -> Path:
    """安全写入文件，验证路径在允许范围内。

    Returns:
        resolved_path

    Raises:
        ValueError: 路径在允许范围外。
    """
    resolved = _validate_path(file_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding=encoding)
    return resolved


def safe_list_dir(dir_path: str, pattern: str = "*.md") -> list[Path]:
    """安全列出目录中的文件。

    Raises:
        ValueError: 路径在允许范围外或目录不存在。
    """
    resolved = _validate_path(dir_path)
    if not resolved.is_dir():
        raise ValueError(f"目录不存在: {dir_path}")
    return sorted(resolved.glob(pattern))


def safe_path_exists(file_path: str) -> bool:
    """检查路径是否存在且在允许范围内。"""
    try:
        resolved = _validate_path(file_path)
        return resolved.exists()
    except ValueError:
        return False


def template_path_exists(file_path: str) -> bool:
    """检查模板文件是否存在且在模板目录允许范围内。

    通过 PAPER_TOOLS_TEMPLATE_DIR 环境变量配置模板目录。
    若未配置，回退到主沙箱检查（safe_path_exists）。
    """
    template_dir = os.environ.get("PAPER_TOOLS_TEMPLATE_DIR", "")
    if not template_dir:
        return safe_path_exists(file_path)

    resolved = Path(file_path).resolve()
    base = Path(template_dir).resolve()

    try:
        resolved.relative_to(base)
    except ValueError:
        # 不在模板目录下，回退到主沙箱检查（向后兼容）
        return safe_path_exists(file_path)

    return resolved.is_file()


def _validate_path(user_path: str) -> Path:
    """验证路径在允许的基础目录范围内。"""
    resolved = Path(user_path).resolve()
    base = get_allowed_base()

    # 确保解析后的路径以基础目录开头
    try:
        resolved.relative_to(base)
    except ValueError:
        raise ValueError(
            f"路径在允许范围外: {user_path} (解析为: {resolved})"
        )

    return resolved
