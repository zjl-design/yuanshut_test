# -*- coding: utf-8 -*-
"""CSV读取器单元测试"""
import pytest
from pathlib import Path
from src.csv_reader import CSVReader, TestCase


class TestCSVReader:
    """测试CSV读取功能"""

    def test_read_valid_csv(self, tmp_path):
        """测试读取有效CSV"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("询问方式,回答方式\n你好,您好\n在吗,在的", encoding="utf-8-sig")

        reader = CSVReader()
        cases = reader.read(csv_file)

        assert len(cases) == 2
        assert cases[0].ask == "你好"
        assert cases[0].answer == "您好"

    def test_skip_empty_ask(self, tmp_path):
        """测试跳过空询问方式"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("询问方式,回答方式\n,回答\n你好,", encoding="utf-8-sig")

        reader = CSVReader()
        cases = reader.read(csv_file)

        assert len(cases) == 1
        assert cases[0].ask == "你好"

    def test_file_not_found(self):
        """测试文件不存在异常"""
        reader = CSVReader()
        with pytest.raises(FileNotFoundError):
            reader.read(Path("nonexistent.csv"))

    def test_gbk_encoding(self, tmp_path):
        """测试GBK编码文件"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("询问方式,回答方式\n测试,测试回答", encoding="gbk")

        reader = CSVReader()
        cases = reader.read(csv_file)

        assert len(cases) == 1
        assert cases[0].ask == "测试"
