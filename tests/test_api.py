# -*- coding: utf-8 -*-
"""
数据驱动 API 测试 - 真实接口，只验证发送成功
"""
import pytest
import requests
import json
import logging
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any

from tests.assertions import run_assertions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
COLLECTION_PATH = PROJECT_ROOT / "collection.json"


def load_collection() -> Dict[str, Any]:
    with open(COLLECTION_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_test_cases(collection: Dict) -> List[Dict]:
    cases = []
    for item in collection.get("item", []):
        request = item["request"]
        url_data = request["url"]
        url = f"{url_data['protocol']}://{'.'.join(url_data['host'])}/{'/'.join(url_data['path'])}"
        if url_data.get("query"):
            query = "&".join([f"{q['key']}={q['value']}" for q in url_data["query"]])
            url += f"?{query}"
        
        headers = {}
        for h in request["header"]:
            key = h["key"]
            value = h["value"]
            if key in ["cybertron-robot-key", "cybertron-robot-token"]:
                value = urllib.parse.unquote(value)
            headers[key] = value
        
        body = json.loads(request["body"]["raw"])
        conv = body["payload"]["conversation"]
        
        cases.append({
            "name": item["name"],
            "url": url,
            "headers": headers,
            "body": body,
            "ask": conv["dialog_5"]["content"],
            "answer": conv["dialog_6"]["content"],
        })
    
    logger.info(f"提取到 {len(cases)} 条测试用例")
    return cases


COLLECTION = load_collection()
TEST_CASES = extract_test_cases(COLLECTION)


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    yield session
    session.close()


def case_id(case: Dict) -> str:
    ask_short = case["ask"][:20] + "..." if len(case["ask"]) > 20 else case["ask"]
    return f"{case['name']}: {ask_short}"


@pytest.mark.parametrize("case", TEST_CASES, ids=case_id)
def test_api_request(api_session, case: Dict):
    """
    数据驱动测试：只验证请求发送成功
    业务结果通过另一个接口查询
    """
    logger.info(f"▶️ 执行: {case['name']}")
    logger.info(f"   询问: {case['ask'][:50]}")
    
    # 发送请求
    try:
        response = api_session.post(
            case["url"],
            headers=case["headers"],
            json=case["body"],
            timeout=30
        )
    except requests.exceptions.RequestException as e:
        pytest.fail(f"请求异常: {e}")
    
    # 断言1: HTTP 200
    assert response.status_code == 200, \
        f"HTTP状态码错误: {response.status_code}\n响应: {response.text[:200]}"
    
    # 断言2: 解析 JSON
    try:
        result = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"响应不是有效JSON: {response.text[:200]}")
    
    # 断言3: 业务码检查（00000=成功, 40000=失败）
    run_assertions(result, case)
    
    logger.info(f"✅ {case['name']} 通过")


def test_collection_loaded():
    assert len(TEST_CASES) > 0