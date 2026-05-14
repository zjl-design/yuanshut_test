# -*- coding: utf-8 -*-
"""Payload构建器 - 动态生成请求体"""
import json
import uuid
from copy import deepcopy
from typing import Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PayloadConfig:
    """Payload配置"""
    flow_uuid: str
    car_type: str
    first_tag: str
    plate_city: str
    tenant_name: str
    api_endpoint: str


class PayloadBuilder:
    """动态构建Postman请求Payload"""

    def __init__(self, config: PayloadConfig, base_template: Dict = None):
        self.config = config
        self.base_template = base_template or self._default_template()

    def _default_template(self) -> Dict[str, Any]:
        """默认模板（可从外部JSON加载）"""
        return {
            "flow_uuid": self.config.flow_uuid,
            "payload": {
                "car_type": self.config.car_type,
                "first_tag": "人工核保需协助",
                "is_all_quote_fail": "2",
                "is_buy_svc_pkg": "1",
                "is_traded": "1",
                "plate_city": self.config.plate_city,
                "quotation_date": "2025-10-04",
                "quote_success_insurer": "",
                "rN_number": "RNobjzjl1",
                "seat_name": "谢郑依",
                "quote_result": [
                    {"is_all_quote_fail": "2", "over_time": "2025-11-01 18:00:00"}
                ],
                "tags": [],
                "conversation": {
                    "dialog_1": {
                        "content": "Hongda Ren 通过了你的朋友验证请求，以上是打招呼的消息。",
                        "role": "客户",
                        "talk_time": "2025-11-02 09:30:39"
                    },
                    "dialog_2": {
                        "content": "Hi，特斯拉车主！我是您的在线续保顾问小爱...",
                        "role": "客服",
                        "talk_time": "2025-11-02 09:35:39"
                    },
                    "dialog_3": {
                        "content": "您好 在吗？",
                        "role": "客户",
                        "talk_time": "2025-11-03 13:38:40"
                    },
                    "dialog_4": {
                        "content": "您好久等啦~这是根据您的车辆提供的店内几家保司的保险方案及报价...",
                        "role": "客服",
                        "talk_time": "2025-11-03 13:40:36"
                    },
                    "dialog_5": {"content": "", "role": "客户", "talk_time": "2025-11-09 08:45:36"},
                    "dialog_6": {"content": "", "role": "客服", "talk_time": "2025-11-09 08:50:13"}
                },
                "first_tag_time": "2025-11-01 20:01:02",
                "lead_assign_time": "2025-11-01 09:01:03",
                "lead_first_call_time": "2025-11-02 10:29:02"
            }
        }

    def build(self, case_idx: int, ask_content: str, answer_content: str) -> Dict[str, Any]:
        """为单个测试用例构建Payload"""
        payload = deepcopy(self.base_template)

        # 更新动态字段
        payload["payload"]["rN_number"] = f"RNobjzjl{case_idx}"
        payload["payload"]["conversation"]["dialog_5"]["content"] = ask_content
        payload["payload"]["conversation"]["dialog_6"]["content"] = answer_content

        # 更新时间戳为当前时间（可选）
        # self._update_timestamps(payload)

        return payload

    def load_template_from_file(self, path: str) -> None:
        """从外部JSON文件加载模板"""
        with open(path, 'r', encoding='utf-8') as f:
            self.base_template = json.load(f)
        logger.info(f"✅ 从 {path} 加载模板成功")
