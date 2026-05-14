# -*- coding: utf-8 -*-
"""
业务断言库 - 仅校验 HTTP 状态码和响应
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def run_assertions(result: Dict[str, Any], case: Dict) -> None:
    """
    执行断言：仅检查响应非空 + 业务状态码
    """
    # 1. 响应非空
    assert result, "响应为空"

    # 2. 业务状态码检查（支持字符串和数字）
    code = result.get("code")
    is_success = code in ["00000", 0, "0", 200, "200", "success", "SUCCESS"]
    assert is_success, \
        f"业务状态异常: code={code}, message={result.get('message', '')}"

    logger.info(f"  ✅ 断言通过: code={code}")