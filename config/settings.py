# -*- coding: utf-8 -*-
"""配置管理 - 支持环境变量覆盖"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent.parent

# CSV配置
CSV_CONFIG = {
    "encoding_priority": ["utf-8-sig", "gbk", "utf-8"],
    "required_columns": ["询问方式"],  # 回答方式可为空
    "delimiter": ",",
}

# Postman配置
POSTMAN_CONFIG = {
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "default_headers": [
        {"key": "Content-Type", "value": "application/json"},
        {"key": "Accept", "value": "*/*"},
    ],
    # 敏感信息通过环境变量注入
    "api_key": os.getenv("CYBERTRON_API_KEY", ""),
    "api_token": os.getenv("CYBERTRON_API_TOKEN", ""),
    "username": os.getenv("API_USERNAME", "1233_hunan_yushu@agentos.com"),
}

# API端点
API_ENDPOINT = os.getenv(
    "API_ENDPOINT",
    "https://agentos.resultscloud.com/openapi/v1/tasks/flow/upload/"
)
TENANT_NAME = os.getenv("TENANT_NAME", "AiopsTest")

# 模板配置
TEMPLATE_CONFIG = {
    "flow_uuid": "be57e2a2-2687-11f1-b2b7-8e31698fca76",
    "default_car_type": "1",
    "default_city": "长沙",
}

# 输出配置
OUTPUT_CONFIG = {
    "indent": 2,
    "ensure_ascii": False,
    "default_filename": "postman_collection.json",
}
