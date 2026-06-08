"""
ZeroGPT检测器客户端

API文档: https://zerogpt.com/api
"""

import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ZeroGPTClient:
    """ZeroGPT AI检测器客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.zerogpt.com/api/detect/detectText"):
        """
        初始化ZeroGPT客户端

        Args:
            api_key: ZeroGPT API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "ApiKey": self.api_key,
            "Content-Type": "application/json"
        })

    def detect(self, text: str) -> Dict:
        """
        检测文本AI概率

        Args:
            text: 待检测文本

        Returns:
            {
                "score": 0.78,           # AI分数 (0-1)
                "is_ai_generated": True, # 是否AI生成
                "sentences": [           # 句子级别详情
                    {"sentence": "...", "is_ai": True},
                    ...
                ],
                "ai_words": 123,         # AI单词数
                "text_words": 150,       # 总单词数
                "fake_percentage": 78.5  # AI百分比
            }

        Raises:
            requests.HTTPError: API请求失败
        """
        payload = {
            "input_text": text
        }

        try:
            response = self.session.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            logger.info(f"ZeroGPT检测成功: AI分={result.get('data', {}).get('fakePercentage', 0) / 100:.2f}")
            return self._parse_response(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"ZeroGPT API请求失败: {e}")
            raise

    def detect_batch(self, texts: List[str]) -> List[Dict]:
        """
        批量检测文本

        Args:
            texts: 待检测文本列表

        Returns:
            检测结果列表
        """
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.detect(text)
                results.append(result)
            except Exception as e:
                logger.error(f"批量检测第{i+1}个文本失败: {e}")
                results.append(None)

        return results

    def _parse_response(self, raw_response: Dict) -> Dict:
        """
        解析API响应

        Args:
            raw_response: 原始API响应

        Returns:
            标准化的检测结果
        """
        data = raw_response.get("data", {})

        if not data:
            return {
                "score": 0.0,
                "is_ai_generated": False,
                "sentences": [],
                "ai_words": 0,
                "text_words": 0,
                "fake_percentage": 0.0
            }

        # ZeroGPT返回的是百分比(0-100)，需要转换为0-1
        fake_percentage = data.get("fakePercentage", 0.0)
        score = fake_percentage / 100.0

        return {
            "score": score,
            "is_ai_generated": data.get("isHuman", True) == False,
            "sentences": self._parse_sentences(data.get("sentences", [])),
            "ai_words": data.get("aiWords", 0),
            "text_words": data.get("textWords", 0),
            "fake_percentage": fake_percentage,
            "feedback": data.get("feedback", "")
        }

    def _parse_sentences(self, sentences: List[Dict]) -> List[Dict]:
        """
        解析句子级别检测结果

        Args:
            sentences: 原始句子列表

        Returns:
            标准化的句子列表
        """
        parsed = []
        for sent in sentences:
            parsed.append({
                "sentence": sent.get("sentence", ""),
                "is_ai": sent.get("isHighlighted", False),
                "percentage": sent.get("fakePercentage", 0.0)
            })
        return parsed

    def get_usage(self) -> Dict:
        """
        获取API使用情况（如果API支持）

        Returns:
            使用情况统计

        Note:
            ZeroGPT可能不提供此接口，根据实际API文档调整
        """
        logger.warning("ZeroGPT API可能不支持使用情况查询")
        return {
            "message": "Usage statistics not available for ZeroGPT"
        }
