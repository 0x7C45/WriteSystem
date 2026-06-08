"""文献工具：读取索引卡集合 + 按注册表组装参考文献列表。"""

import re
from pathlib import Path

from paper_tools_mcp.utils.safe_path import safe_read, safe_list_dir


def _normalize_key_fragment(value: str) -> str:
    """归一化 key/文件名片段，便于兼容旧命名。"""
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def _legacy_lookup_keys(cite_key: str) -> list[str]:
    """为 cite_key 生成兼容旧文件名的候选 key。"""
    keys: list[str] = []
    current = cite_key
    while current:
        keys.append(current)
        if "_" not in current:
            break
        current = current.rsplit("_", 1)[0]
    return keys


def get_literature_cards(
    cards_dir: str,
    filter_keyword: str | None = None,
) -> dict:
    """读取索引卡集合。

    Args:
        cards_dir: 索引卡目录路径（包含 .md 文件）。
        filter_keyword: 可选关键词过滤。
    """
    try:
        md_files = safe_list_dir(cards_dir, "*.md")
    except ValueError as e:
        return {"error": str(e)}

    cards: list[dict] = []
    for md_file in md_files:
        try:
            _, text = safe_read(str(md_file))
        except ValueError as e:
            return {"error": f"读取索引卡失败: {md_file.name}: {e}"}
        except Exception as e:
            return {"error": f"读取索引卡失败: {md_file.name}: {e}"}

        card: dict = {"file": md_file.name}

        title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        if title_match:
            card["title"] = title_match.group(1).strip()

        author_match = re.search(r'作者[：:]\s*(.+)', text)
        if author_match:
            card["author"] = author_match.group(1).strip()

        cite_key_match = re.search(r'cite_key[：:]\s*(.+)', text)
        if cite_key_match:
            card["cite_key"] = cite_key_match.group(1).strip()
        else:
            card["cite_key"] = Path(md_file.name).stem

        year_match = re.search(r'年份[：:]\s*(\d{4})', text)
        if year_match:
            card["year"] = int(year_match.group(1))

        source_match = re.search(r'(?:来源|期刊)[：:]\s*(.+)', text)
        if source_match:
            card["source"] = source_match.group(1).strip()

        keywords_match = re.search(r'关键词[：:]\s*(.+)', text)
        if keywords_match:
            card["keywords"] = [k.strip() for k in keywords_match.group(1).split(',')]

        url_match = re.search(r'(?:DOI[/|]?URL|链接|地址)[：:]\s*(.+)', text)
        if url_match:
            card["url"] = url_match.group(1).strip()

        findings_match = re.search(
            r'(?:核心发现|主要发现|研究结论)[：:]\s*(.+?)(?=\n##|\n#|\Z)', text, re.DOTALL,
        )
        if findings_match:
            card["findings"] = findings_match.group(1).strip()[:300]

        method_match = re.search(
            r'(?:研究方法|方法)[：:]\s*(.+?)(?=\n##|\n#|\n核心|\Z)', text, re.DOTALL,
        )
        if method_match:
            card["method"] = method_match.group(1).strip()[:200]

        if filter_keyword:
            if filter_keyword.lower() not in text.lower():
                continue

        cards.append(card)

    return {
        "directory": cards_dir,
        "total": len(cards),
        "cards": cards,
    }


def build_reference_list(
    registry_path: str,
    cards_dir: str,
) -> dict:
    """按注册表编号顺序，从文献索引卡组装编号列表。

    Args:
        registry_path: 引用编号注册表路径。
        cards_dir: 文献索引卡目录路径。
    """
    try:
        _, reg_text = safe_read(registry_path)
    except ValueError as e:
        return {"error": str(e), "status": "REVISE"}

    cards_result = get_literature_cards(cards_dir)
    if "error" in cards_result:
        return {"error": cards_result["error"], "status": "REVISE"}

    card_map: dict[str, dict] = {}
    legacy_stem_map: dict[str, list[dict]] = {}
    normalized_legacy_map: dict[str, list[dict]] = {}
    for c in cards_result.get("cards", []):
        card_map[c["cite_key"]] = c
        stem = Path(c.get("file", "")).stem
        legacy_stem_map.setdefault(stem, []).append(c)
        normalized_legacy_map.setdefault(_normalize_key_fragment(stem), []).append(c)

    entries = re.findall(
        r'\|\s*(\d+)\s*\|\s*(\S+)\s*\|', reg_text,
    )
    if not entries:
        return {"error": "注册表中未找到编号映射条目", "status": "REVISE"}

    registry_rows: list[tuple[int, str]] = []
    seen_nums: set[int] = set()
    for num_str, cite_key in entries:
        num = int(num_str)
        if num in seen_nums:
            continue
        seen_nums.add(num)
        registry_rows.append((num, cite_key.strip()))

    registry_rows.sort(key=lambda x: x[0])

    lines: list[str] = []
    missing_cards: list[str] = []
    missing_details: list[dict] = []
    total = 0

    for num, cite_key in registry_rows:
        total += 1
        card = card_map.get(cite_key)
        if card:
            author = card.get("author", "未知作者")
            title = card.get("title", "未知标题")
            source = card.get("source", "")
            year = card.get("year", "")
            entry = f"[{num}] {author}. {title}"
            if source:
                entry += f". {source}"
            if year:
                entry += f", {year}."
            url = card.get("url", "")
            if url and url != "未获取":
                entry += f" {url}."
            lines.append(entry)
        else:
            legacy_matches: list[dict] = []
            for key in _legacy_lookup_keys(cite_key):
                legacy_matches.extend(legacy_stem_map.get(key, []))
                normalized_matches = normalized_legacy_map.get(_normalize_key_fragment(key), [])
                legacy_matches.extend(normalized_matches)
            deduped_matches: list[dict] = []
            seen_files: set[str] = set()
            for match in legacy_matches:
                file_name = match.get("file", "")
                if file_name in seen_files:
                    continue
                seen_files.add(file_name)
                deduped_matches.append(match)
            if legacy_matches:
                reason = (
                    f"未匹配显式 cite_key；可能仍在使用旧版文件名/未写入 cite_key 字段 "
                    f"(候选: {', '.join(c['file'] for c in deduped_matches)})"
                )
            else:
                reason = "索引卡缺失"
            lines.append(f"[{num}] (cite_key={cite_key}，{reason})")
            missing_cards.append(cite_key)
            missing_details.append({"num": num, "cite_key": cite_key, "reason": reason})

    return {
        "status": "PASS" if not missing_cards else "REVISE",
        "total_entries": total,
        "missing_cards": missing_cards,
        "missing_details": missing_details,
        "reference_list_text": "\n".join(lines),
    }
