"""paper-tools-mcp: 论文工具 MCP Server.

工具清单：
- validate_word_count: 字数统计（总量 + 按章节）
- validate_citations: 引用标记与文献列表一致性检查
- validate_markdown_structure: Markdown 结构合法性检查
- validate_assets: Markdown 资源锚点检查
- validate_docx_styles: DOCX 样式命中检查
- validate_docx_layout: DOCX 页面布局检查（第二阶段）
- validate_docx_fonts: DOCX 字体命中检查（第二阶段）
- validate_docx_sections: DOCX 分节/分页检查
- validate_docx_references: DOCX 参考文献段落样式检查（第二阶段）
- assess_aigc_risk: AIGC 风险评估（困惑度/突发性/N-gram）
- build_preflight_docx: Markdown → DOCX 结构基线
- apply_minimax_c2: minimax-docx C-2 Base-Replace 排版
- apply_pandoc_templated: pandoc 带模板排版
- pandoc_to_docx: 向后兼容别名
- run_format_pipeline: 排版主链（自动降级 + 单次 fallback）
- get_literature_cards: 读取索引卡集合
- search_blocks: 滑动窗口切片 + all-MiniLM-L6-v2 无状态检索
- query_data_facts: 按关键词检索 data_facts.md
- analyze_docx_template: 分析 DOCX 模板样式结构（基于 minimax-docx）
- query_excel_data: 查询 Excel 数据（概览/精确点查，基于 minimax-xlsx）
- validate_excel_formulas: 静态校验 Excel 公式（基于 minimax-xlsx）
"""

import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# 确保项目根目录在 sys.path 中（用于 utils 导入）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from paper_tools_mcp.tools.validation import (
    validate_word_count,
    validate_citations,
    validate_markdown_structure,
    validate_assets,
    validate_docx_styles,
    validate_docx_layout,
    validate_docx_fonts,
    validate_docx_sections,
    validate_docx_references,
    validate_chapter_citations,
    validate_citation_order,
)
from paper_tools_mcp.tools.aigc import assess_aigc_risk
from paper_tools_mcp.tools.formatting import (
    pandoc_to_docx,
    build_preflight_docx,
    apply_minimax_c2,
    apply_pandoc_templated,
)
from paper_tools_mcp.tools.retry import run_format_pipeline
from paper_tools_mcp.tools.literature import get_literature_cards, build_reference_list
from paper_tools_mcp.tools.retrieval import search_blocks, query_data_facts
from paper_tools_mcp.tools.docx_template import analyze_docx_template
from paper_tools_mcp.tools.xlsx_tools import query_excel_data, validate_excel_formulas


# ── 启动时环境检测 ────────────────────────────────────────

def _check_docx_env() -> bool:
    """启动时检查 .NET + minimax-docx CLI 是否就绪。"""
    script = Path.home() / ".claude" / "skills" / "minimax-docx" / "scripts" / "env_check.sh"
    if not script.exists():
        return False
    try:
        r = subprocess.run(
            ["bash", str(script)],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0 and "READY" in r.stdout
    except Exception:
        return False


MINIMAX_DOCX_READY = _check_docx_env()

mcp = FastMCP("paper-tools-mcp", json_response=True)

# ── 注册工具 ──────────────────────────────────────────────

mcp.tool()(validate_word_count)
mcp.tool()(validate_citations)
mcp.tool()(validate_markdown_structure)
mcp.tool()(validate_assets)
mcp.tool()(validate_docx_styles)
mcp.tool()(validate_docx_layout)
mcp.tool()(validate_docx_fonts)
mcp.tool()(validate_docx_sections)
mcp.tool()(validate_docx_references)
mcp.tool()(validate_chapter_citations)
mcp.tool()(validate_citation_order)
mcp.tool()(build_reference_list)
mcp.tool()(assess_aigc_risk)
mcp.tool()(pandoc_to_docx)
mcp.tool()(build_preflight_docx)
mcp.tool()(apply_minimax_c2)
mcp.tool()(apply_pandoc_templated)
mcp.tool()(run_format_pipeline)
mcp.tool()(get_literature_cards)
mcp.tool()(search_blocks)
mcp.tool()(query_data_facts)
mcp.tool()(analyze_docx_template)
mcp.tool()(query_excel_data)
mcp.tool()(validate_excel_formulas)

if __name__ == "__main__":
    mcp.run(transport="stdio")
