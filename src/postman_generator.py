# -*- coding: utf-8 -*-
"""Postman Collection生成器"""
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PostmanConfig:
    """Postman配置"""
    collection_name: str
    schema: str
    api_key: str
    api_token: str
    username: str
    api_endpoint: str
    tenant_name: str


class PostmanGenerator:
    """生成Postman Collection JSON"""

    def __init__(self, config: PostmanConfig):
        self.config = config

    def generate(self, payloads: List[Dict[str, Any]], output_path: Path) -> Path:
        """生成Postman Collection文件"""
        collection = {
            "info": {
                "name": self.config.collection_name,
                "schema": self.config.schema,
                "_postman_id": str(uuid.uuid4()),
                "description": f"自动生成于 {self._now()}"
            },
            "item": []
        }

        for idx, payload in enumerate(payloads, 1):
            item = self._build_item(idx, payload)
            collection["item"].append(item)
            logger.info(f"✅ 生成用例 {idx}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(collection, f, ensure_ascii=False, indent=2)

        logger.info(f"🎉 生成完成: {output_path}")
        return output_path

    def _build_item(self, idx: int, payload: Dict) -> Dict:
        """构建单个Postman Item"""
        return {
            "name": f"测试用例_{idx}",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"},
                    {"key": "Accept", "value": "*/*"},
                    {"key": "cybertron-robot-key", "value": self.config.api_key},
                    {"key": "cybertron-robot-token", "value": self.config.api_token},
                    {"key": "username", "value": self.config.username}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(payload, ensure_ascii=False, indent=2)
                },
                "url": {
                    "raw": f"{self.config.api_endpoint}?tenant_name={self.config.tenant_name}",
                    "protocol": "https",
                    "host": self._parse_host(self.config.api_endpoint),
                    "path": self._parse_path(self.config.api_endpoint),
                    "query": [{"key": "tenant_name", "value": self.config.tenant_name}]
                }
            },
            "response": []
        }

    def _parse_host(self, url: str) -> List[str]:
        """解析URL获取host列表"""
        # 简化处理，实际可用urllib.parse
        return ["agentos", "resultscloud", "com"]

    def _parse_path(self, url: str) -> List[str]:
        """解析URL获取path列表"""
        return ["openapi", "v1", "tasks", "flow", "upload"]

    def _now(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
