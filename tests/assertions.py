# -*- coding: utf-8 -*-
"""
业务断言库
根据 ask/answer 内容，定义不同的断言规则
"""
import json
import logging
from typing import Dict, Any, Callable, List

logger = logging.getLogger(__name__)

# 断言规则注册表
ASSERTION_RULES: List[Dict] = []


def register_rule(keyword: str, assert_func: Callable, description: str = ""):
    """注册断言规则"""
    ASSERTION_RULES.append({
        "keyword": keyword,
        "func": assert_func,
        "desc": description
    })
    logger.debug(f"注册断言规则: {keyword}")


# ========== 具体断言函数 ==========

def assert_status_ok(result: Dict, case: Dict) -> None:
    """基础断言：状态码检查"""
    assert result.get("code") == 0 or result.get("status") == "success", \
        f"业务状态异常: {result}"


def assert_not_empty_response(result: Dict, case: Dict) -> None:
    """断言：响应非空"""
    assert result, "响应为空"


def assert_contains_discount(result: Dict, case: Dict) -> None:
    """断言：返回包含优惠信息"""
    text = json.dumps(result, ensure_ascii=False)
    keywords = ["优惠", "discount", "降价", "活动"]
    assert any(k in text for k in keywords), \
        f"预期返回优惠信息，实际: {text[:500]}"


def assert_contains_price(result: Dict, case: Dict) -> None:
    """断言：返回包含价格信息"""
    text = json.dumps(result, ensure_ascii=False)
    keywords = ["价格", "保费", "元", "price", "amount"]
    assert any(k in text for k in keywords), \
        f"预期返回价格信息，实际: {text[:500]}"


def assert_contains_renewal(result: Dict, case: Dict) -> None:
    """断言：返回包含续保信息"""
    text = json.dumps(result, ensure_ascii=False)
    keywords = ["续保", "renewal", "到期", "续费"]
    assert any(k in text for k in keywords), \
        f"预期返回续保信息，实际: {text[:500]}"


def assert_contains_complaint_handler(result: Dict, case: Dict) -> None:
    """断言：返回包含投诉处理信息"""
    text = json.dumps(result, ensure_ascii=False)
    keywords = ["投诉", "客服", "处理", "反馈"]
    assert any(k in text for k in keywords), \
        f"预期返回投诉处理信息，实际: {text[:500]}"


# ========== 注册规则 ==========

# 根据 answer 内容匹配
register_rule("优惠", assert_contains_discount, "回答含优惠，预期返回优惠信息")
register_rule("降价", assert_contains_discount, "回答含降价，预期返回优惠信息")
register_rule("折扣", assert_contains_discount, "回答含折扣，预期返回优惠信息")
register_rule("价格", assert_contains_price, "回答含价格，预期返回价格信息")
register_rule("保费", assert_contains_price, "回答含保费，预期返回价格信息")
register_rule("续保", assert_contains_renewal, "回答含续保，预期返回续保信息")
register_rule("到期", assert_contains_renewal, "回答含到期，预期返回续保信息")
register_rule("投诉", assert_contains_complaint_handler, "回答含投诉，预期返回处理信息")


def run_assertions(result: Dict[str, Any], case: Dict) -> None:
    """
    执行所有匹配的断言
    """
    # 1. 基础断言（所有用例都执行）
    assert_not_empty_response(result, case)
    
    # 如果鉴权失败，跳过业务断言，只记录日志
    if result.get("code") == "400000":
        logger.warning("  ⚠️ 鉴权失败 (400000)，跳过业务断言")
        return
    
    # 2. 根据 answer 内容匹配规则
    answer = case.get("answer", "")
    matched = False
    
    for rule in ASSERTION_RULES:
        if rule["keyword"] in answer:
            logger.info(f"  🔍 匹配断言规则: {rule['desc']}")
            rule["func"](result, case)
            matched = True
    
    # 3. 如果没有匹配到特定规则，执行通用断言
    if not matched:
        logger.info("  🔍 执行通用断言")
        assert_status_ok(result, case)
    
    logger.info("  ✅ 断言通过")