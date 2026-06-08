"""
GPTZero检测器客户端

API文档: https://gptzero.me/docs
"""

import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class GPTZeroClient:
    """GPTZero AI检测器客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.gptzero.me/v2"):
        """
        初始化GPTZero客户端

        Args:
            api_key: GPTZero API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def detect(self, text: str, multilingual: bool = False) -> Dict:
        """
        检测文本AI概率

        Args:
            text: 待检测文本
            multilingual: 是否使用多语言模型

        Returns:
            {
                "overall": 0.78,  # 整体AI概率
                "sentences": [     # 句子级别详情
                    {"sentence": "...", "score": 0.85},
                    ...
                ],
                "paragraphs": [...], # 段落级别详情
                "completely_generated_prob": 0.65,
                "average_generated_prob": 0.72
            }

        Raises:
            requests.HTTPError: API请求失败
        """
        endpoint = f"{self.base_url}/predict/text"

        payload = {
            "document": text,
            "multilingual": multilingual
        }

        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            logger.info(f"GPTZero检测成功: 整体AI分={result.get('documents', [{}])[0].get('average_generated_prob', 0):.2f}")
            return self._parse_response(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"GPTZero API请求失败: {e}")
            raise

    def detect_batch(self, texts: List[str], multilingual: bool = False) -> List[Dict]:
        """
        批量检测文本

        Args:
            texts: 待检测文本列表
            multilingual: 是否使用多语言模型

        Returns:
            检测结果列表
        """
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.detect(text, multilingual)
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
        documents = raw_response.get("documents", [])
        if not documents:
            return {
                "overall": 0.0,
                "sentences": [],
                "paragraphs": [],
                "completely_generated_prob": 0.0,
                "average_generated_prob": 0.0
            }

        doc = documents[0]

        return {
            "overall": doc.get("average_generated_prob", 0.0),
            "sentences": doc.get("sentences", []),
            "paragraphs": doc.get("paragraphs", []),
            "completely_generated_prob": doc.get("completely_generated_prob", 0.0),
            "average_generated_prob": doc.get("average_generated_prob", 0.0),
            "class_probabilities": doc.get("class_probabilities", {})
        }

    def check_credits(self) -> Dict:
        """
        检查API额度

        Returns:
            {
                "credits_remaining": 1000,
                "credits_used": 234
            }
        """
        endpoint = f"{self.base_url}/credits"

        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"检查GPTZero额度失败: {e}")
            raise
