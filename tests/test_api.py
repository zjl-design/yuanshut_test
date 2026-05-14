# -*- coding: utf-8 -*-
"""
数据驱动 API 测试
从 collection.json 提取用例，自动参数化运行
"""
import pytest
import requests
import json
import logging
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any

# 导入断言模块
from tests.assertions import run_assertions

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent
COLLECTION_PATH = PROJECT_ROOT / "collection.json"


def load_collection() -> Dict[str, Any]:
    """加载 Postman Collection"""
    with open(COLLECTION_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_test_cases(collection: Dict) -> List[Dict]:
    """从 Collection 提取所有测试用例，并对 Header 做 URL 解码"""
    cases = []
    for item in collection.get("item", []):
        request = item["request"]
        
        # 构建完整 URL
        url_data = request["url"]
        url = f"{url_data['protocol']}://{'.'.join(url_data['host'])}/{'/'.join(url_data['path'])}"
        if url_data.get("query"):
            query = "&".join([f"{q['key']}={q['value']}" for q in url_data["query"]])
            url += f"?{query}"
        
        # 解析 headers，并对关键字段做 URL 解码（防止双重编码导致鉴权失败）
        headers = {}
        for h in request["header"]:
            key = h["key"]
            value = h["value"]
            # 对 robot-key 和 robot-token 做 URL 解码
            if key in ["cybertron-robot-key", "cybertron-robot-token"]:
                value = urllib.parse.unquote(value)
            headers[key] = value
        
        # 解析 body
        body = json.loads(request["body"]["raw"])
        
        # 提取 ask/answer 用于标识
        conv = body["payload"]["conversation"]
        ask = conv["dialog_5"]["content"]
        answer = conv["dialog_6"]["content"]
        
        cases.append({
            "name": item["name"],
            "url": url,
            "headers": headers,
            "body": body,
            "ask": ask,
            "answer": answer,
        })
    
    logger.info(f"提取到 {len(cases)} 条测试用例")
    return cases


# 加载用例数据
COLLECTION = load_collection()
TEST_CASES = extract_test_cases(COLLECTION)


@pytest.fixture(scope="session")
def api_session():
    """创建会话，保持连接复用"""
    session = requests.Session()
    yield session
    session.close()


def case_id(case: Dict) -> str:
    """生成用例显示名称"""
    ask_short = case["ask"][:20] + "..." if len(case["ask"]) > 20 else case["ask"]
    return f"{case['name']}: {ask_short}"


@pytest.mark.parametrize("case", TEST_CASES, ids=case_id)
def test_api_request(api_session, case: Dict):
    """
    数据驱动测试：每个用例自动发送请求
    """
    # 在 test_api_request 里加这行，看实际发送的 key
    print(f"解码后的 key: {case['headers'].get('cybertron-robot-key')}")
    logger.info(f"▶️ 执行: {case['name']}")
    logger.info(f"   询问: {case['ask'][:50]}")
    logger.info(f"   回答: {case['answer'][:50]}")
    
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
    
    # 基础断言：HTTP 状态码
    assert response.status_code == 200, \
        f"HTTP状态码错误: {response.status_code}\n响应: {response.text[:200]}"
    
    # 尝试解析 JSON
    try:
        result = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"响应不是有效JSON: {response.text[:200]}")
    
    # 如果鉴权失败，记录警告但不报错（用于调试）
    if result.get("code") == "400000":
        logger.warning(f"  ⚠️ 鉴权失败: {result.get('message')}")
        logger.warning(f"  发送的 key: {case['headers'].get('cybertron-robot-key', 'N/A')[:30]}...")
    
    # 业务断言（抽离到单独文件）
    run_assertions(result, case)
    
    logger.info(f"✅ {case['name']} 通过")


def test_collection_loaded():
    """验证 Collection 加载成功"""
    assert COLLECTION is not None
    assert "item" in COLLECTION
    assert len(TEST_CASES) > 0