# -*- coding: utf-8 -*-
"""
Mock 测试 - 不调用真实 API
"""
import pytest
import json
import responses
from pathlib import Path
from typing import List, Dict, Any

from tests.assertions import run_assertions


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
        
        headers = {h["key"]: h["value"] for h in request["header"]}
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
    return cases


COLLECTION = load_collection()
TEST_CASES = extract_test_cases(COLLECTION)


def case_id(case: Dict) -> str:
    ask_short = case["ask"][:20] + "..." if len(case["ask"]) > 20 else case["ask"]
    return f"{case['name']}: {ask_short}"


# 模拟不同场景的返回
def get_mock_response(case: Dict) -> Dict:
    """根据用例内容返回模拟数据"""
    answer = case["answer"]
    
    # 价格相关
    if any(k in answer for k in ["价格", "保费", "贵"]):
        return {
            "code": "0",
            "message": "success",
            "data": {
                "reply": "您的保费是根据车型、使用年限、出险记录综合计算的，具体价格如下：交强险950元，商业险3200元...",
                "price_detail": {"交强险": 950, "商业险": 3200}
            }
        }
    
    # 优惠相关
    if any(k in answer for k in ["优惠", "折扣", "降价"]):
        return {
            "code": "0",
            "message": "success",
            "data": {
                "reply": "目前我们有续保优惠活动，可享9折优惠，还送保养一次",
                "discount": "9折",
                "gift": "保养一次"
            }
        }
    
    # 续保相关
    if any(k in answer for k in ["续保", "到期"]):
        return {
            "code": "0",
            "message": "success",
            "data": {
                "reply": "您的保单将于2025-11-01到期，建议提前30天续保",
                "renewal_date": "2025-11-01"
            }
        }
    
    # 默认
    return {
        "code": "0",
        "message": "success",
        "data": {"reply": "已收到您的咨询，客服将尽快回复"}
    }


@pytest.mark.parametrize("case", TEST_CASES, ids=case_id)
@responses.activate
def test_api_mock(case: Dict):
    """Mock 测试：模拟 API 返回"""
    print(f"\n▶️ {case['name']}: {case['ask'][:30]}...")
    
    # 注册 mock 响应
    mock_resp = get_mock_response(case)
    responses.add(
        responses.POST,
        case["url"],
        json=mock_resp,
        status=200
    )
    
    # 发送请求（实际打到 mock）
    import requests
    response = requests.post(
        case["url"],
        headers=case["headers"],
        json=case["body"],
        timeout=30
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # 业务断言
    run_assertions(result, case)
    
    print(f"✅ 通过")


def test_collection_loaded():
    assert len(TEST_CASES) > 0