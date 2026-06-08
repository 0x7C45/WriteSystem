"""AIGC 工具：风险评估。"""

import logging
import math
import re

logger = logging.getLogger(__name__)

# ── 风险评估阈值 ──────────────────────────────────

MIN_TEXT_LENGTH_FOR_PERPLEXITY = 50
MIN_SENTENCES_FOR_BURSTINESS = 3
LOW_PERPLEXITY_THRESHOLD = 5.0
MEDIUM_PERPLEXITY_THRESHOLD = 6.5
LOW_BURSTINESS_THRESHOLD = 0.4
MEDIUM_BURSTINESS_THRESHOLD = 0.6
HIGH_NGRAM_UNIFORMITY_THRESHOLD = 0.85
MEDIUM_NGRAM_UNIFORMITY_THRESHOLD = 0.75

# ── AIGC 风险评估 ──────────────────────────────────────


def _sentence_lengths(text: str) -> list[int]:
    """按句号/问号/叹号分割，返回每句字符数。"""
    sentences = re.split(r'[。！？!?.]+', text)
    return [len(s.strip()) for s in sentences if s.strip()]


def _character_ngram_distribution(text: str, n: int = 3) -> dict[str, int]:
    """计算字符 N-gram 频率分布。"""
    clean = re.sub(r'\s+', '', text)
    ngrams: dict[str, int] = {}
    for i in range(len(clean) - n + 1):
        gram = clean[i:i + n]
        ngrams[gram] = ngrams.get(gram, 0) + 1
    return ngrams


def _perplexity_estimate(text: str) -> float:
    """简化的困惑度估算（基于字符频率熵）。

    AI 文本通常熵较低（~4-6），人类文本较高（~6-9）。
    """
    clean = re.sub(r'\s+', '', text)
    if len(clean) < MIN_TEXT_LENGTH_FOR_PERPLEXITY:
        return 0.0

    freq: dict[str, int] = {}
    for ch in clean:
        freq[ch] = freq.get(ch, 0) + 1

    total = len(clean)
    entropy = -sum(
        (count / total) * math.log2(count / total)
        for count in freq.values()
    )

    return round(entropy, 2)


def _burstiness_estimate(sentence_lengths: list[int]) -> float:
    """突发性估算（变异系数 = 标准差/均值）。

    AI 文本突发性低，人类文本突发性高。
    """
    if len(sentence_lengths) < MIN_SENTENCES_FOR_BURSTINESS:
        return 0.0

    mean = sum(sentence_lengths) / len(sentence_lengths)
    if mean == 0:
        return 0.0

    variance = sum((l - mean) ** 2 for l in sentence_lengths) / len(sentence_lengths)
    return round(math.sqrt(variance) / mean, 2)


def _ngram_uniformity(ngrams: dict[str, int]) -> float:
    """N-gram 均匀度（低均匀度 = AI 特征）。

    AI 文本的 N-gram 分布更均匀。
    """
    if not ngrams:
        return 0.0

    total = sum(ngrams.values())
    if total == 0:
        return 0.0

    entropy = -sum(
        (count / total) * math.log2(count / total)
        for count in ngrams.values()
    )
    max_entropy = math.log2(len(ngrams)) if len(ngrams) > 1 else 1.0

    return round(entropy / max_entropy, 2) if max_entropy > 0 else 0.0


def assess_aigc_risk(
    file_path: str,
) -> dict:
    """AIGC 风险评估（困惑度/突发性/N-gram 启发式）。

    Args:
        file_path: 章节 Markdown 文件路径。
    """
    from paper_tools_mcp.utils.safe_path import safe_read

    try:
        _, text = safe_read(file_path)
    except ValueError as e:
        return {"error": str(e)}

    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]

    overall_perplexity = _perplexity_estimate(text)
    sentences = _sentence_lengths(text)
    overall_burstiness = _burstiness_estimate(sentences)
    trigrams = _character_ngram_distribution(text)
    overall_ngram_uniformity = _ngram_uniformity(trigrams)

    risky_paragraphs: list[dict] = []
    for i, para in enumerate(paragraphs):
        p_perplexity = _perplexity_estimate(para)
        p_sentences = _sentence_lengths(para)
        p_burstiness = _burstiness_estimate(p_sentences)

        if p_perplexity < LOW_PERPLEXITY_THRESHOLD or p_burstiness < LOW_BURSTINESS_THRESHOLD:
            risky_paragraphs.append({
                "index": i + 1,
                "preview": para[:80] + "..." if len(para) > 80 else para,
                "perplexity": p_perplexity,
                "burstiness": p_burstiness,
            })

    # 综合风险评分（0-100）
    risk_score = 0
    if overall_perplexity < MEDIUM_PERPLEXITY_THRESHOLD:
        risk_score += 25
    elif overall_perplexity < MEDIUM_PERPLEXITY_THRESHOLD + 1:
        risk_score += 10

    if overall_burstiness < MEDIUM_BURSTINESS_THRESHOLD:
        risk_score += 25
    elif overall_burstiness < MEDIUM_BURSTINESS_THRESHOLD + 0.2:
        risk_score += 10

    if overall_ngram_uniformity > HIGH_NGRAM_UNIFORMITY_THRESHOLD:
        risk_score += 25
    elif overall_ngram_uniformity > MEDIUM_NGRAM_UNIFORMITY_THRESHOLD:
        risk_score += 10

    if len(risky_paragraphs) > len(paragraphs) * 0.5:
        risk_score += 25
    elif len(risky_paragraphs) > len(paragraphs) * 0.3:
        risk_score += 15

    risk_level = "LOW" if risk_score < 30 else "MEDIUM" if risk_score < 60 else "HIGH"

    return {
        "file": file_path,
        "overall_risk_score": risk_score,
        "risk_level": risk_level,
        "metrics": {
            "perplexity": overall_perplexity,
            "burstiness": overall_burstiness,
            "ngram_uniformity": overall_ngram_uniformity,
        },
        "risky_paragraphs": risky_paragraphs[:10],
        "risky_ratio": f"{len(risky_paragraphs)}/{len(paragraphs)}",
    }
