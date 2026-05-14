# -*- coding: utf-8 -*-
"""Payload构建器单元测试"""
import pytest
from src.payload_builder import PayloadBuilder, PayloadConfig


class TestPayloadBuilder:
    """测试Payload构建"""

    @pytest.fixture
    def config(self):
        return PayloadConfig(
            flow_uuid="test-uuid",
            car_type="1",
            first_tag="测试标签",
            plate_city="测试城市",
            tenant_name="TestTenant",
            api_endpoint="https://test.com/api"
        )

    def test_build_basic(self, config):
        """测试基本构建"""
        builder = PayloadBuilder(config)
        payload = builder.build(1, "询问内容", "回答内容")

        assert payload["payload"]["rN_number"] == "RNobjzjl1"
        assert payload["payload"]["conversation"]["dialog_5"]["content"] == "询问内容"
        assert payload["payload"]["conversation"]["dialog_6"]["content"] == "回答内容"

    def test_build_multiple(self, config):
        """测试多个用例索引递增"""
        builder = PayloadBuilder(config)

        for i in range(1, 4):
            payload = builder.build(i, f"ask{i}", f"ans{i}")
            assert payload["payload"]["rN_number"] == f"RNobjzjl{i}"
