# -*- coding: utf-8 -*-
import argparse
import logging
import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    CSV_CONFIG, POSTMAN_CONFIG, API_ENDPOINT,
    TENANT_NAME, TEMPLATE_CONFIG, OUTPUT_CONFIG
)
from src.csv_reader import CSVReader
from src.payload_builder import PayloadBuilder, PayloadConfig
from src.postman_generator import PostmanGenerator, PostmanConfig


def setup_logging(level: str = "INFO"):
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    parser = argparse.ArgumentParser(description="生成Postman测试集合")
    parser.add_argument("--csv", required=True, help="输入CSV文件路径")
    parser.add_argument("--output", default=OUTPUT_CONFIG["default_filename"], help="输出JSON路径")
    parser.add_argument("--template", help="外部模板JSON路径（可选）")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()
    setup_logging(args.log_level)

    logger = logging.getLogger(__name__)
    logger.info("🚀 开始生成Postman测试集合...")

    # 1. 读取CSV
    reader = CSVReader(encoding_priority=CSV_CONFIG["encoding_priority"])
    cases = reader.read(Path(args.csv))

    if not cases:
        logger.error("❌ 未找到有效测试用例")
        sys.exit(1)

    # 2. 构建Payload
    payload_config = PayloadConfig(
        flow_uuid=TEMPLATE_CONFIG["flow_uuid"],
        car_type=TEMPLATE_CONFIG["default_car_type"],
        first_tag="人工核保需协助",
        plate_city=TEMPLATE_CONFIG["default_city"],
        tenant_name=TENANT_NAME,
        api_endpoint=API_ENDPOINT
    )
    builder = PayloadBuilder(payload_config)

    if args.template:
        builder.load_template_from_file(args.template)

    payloads = []
    for idx, case in enumerate(cases, 1):
        payload = builder.build(idx, case.ask, case.answer)
        payloads.append(payload)

    # 3. 生成Postman Collection
    postman_config = PostmanConfig(
        collection_name="报价后异议测试集合",
        schema=POSTMAN_CONFIG["schema"],
        api_key=POSTMAN_CONFIG["api_key"],
        api_token=POSTMAN_CONFIG["api_token"],
        username=POSTMAN_CONFIG["username"],
        api_endpoint=API_ENDPOINT,
        tenant_name=TENANT_NAME
    )
    generator = PostmanGenerator(postman_config)
    output_path = generator.generate(payloads, Path(args.output))

    logger.info(f"✅ 全部完成！输出文件: {output_path}")


if __name__ == "__main__":
    main()
