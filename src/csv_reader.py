# -*- coding: utf-8 -*-
"""CSV读取器 - 带编码自动检测和校验"""
import csv
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """测试用例数据类"""
    ask: str
    answer: str
    row_number: int

    def is_valid(self) -> bool:
        return bool(self.ask.strip())


class CSVReader:
    """CSV读取器"""

    def __init__(self, encoding_priority: List[str] = None):
        self.encoding_priority = encoding_priority or ["utf-8-sig", "gbk", "utf-8"]

    def read(self, file_path: Path) -> List[TestCase]:
        """读取CSV文件并返回测试用例列表"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"CSV文件不存在: {file_path}")

        content = self._read_with_encoding(file_path)
        return self._parse_cases(content)

    def _read_with_encoding(self, file_path: Path) -> str:
        """尝试多种编码读取文件"""
        for encoding in self.encoding_priority:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.info(f"✅ 使用编码 {encoding} 读取成功")
                return content
            except UnicodeDecodeError:
                logger.warning(f"⚠️ 编码 {encoding} 失败，尝试下一个...")
                continue
        raise ValueError(f"无法使用任何编码读取文件: {self.encoding_priority}")

    def _parse_cases(self, content: str) -> List[TestCase]:
        """解析CSV内容为测试用例"""
        lines = content.strip().splitlines()
        reader = csv.DictReader(lines)

        cases = []
        for idx, row in enumerate(reader, start=2):  # 从第2行开始（跳过表头）
            ask = row.get("询问方式", "").strip()
            ans = row.get("回答方式", "").strip()

            case = TestCase(ask=ask, answer=ans, row_number=idx)
            if case.is_valid():
                cases.append(case)
            else:
                logger.warning(f"⚠️ 第 {idx} 行询问方式为空，已跳过")

        logger.info(f"✅ 提取有效用例: {len(cases)} 条")
        return cases
