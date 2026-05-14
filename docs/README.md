# Postman测试集合生成框架

## 🏗️ 架构概览

```
test_framework/
├── config/                 # 配置管理
│   ├── settings.py         # 集中配置（支持环境变量）
│   └── test_data.yaml      # 测试数据配置
├── src/                    # 核心源码
│   ├── csv_reader.py       # CSV读取（编码自动检测）
│   ├── payload_builder.py  # Payload动态构建
│   ├── postman_generator.py # Postman Collection生成
│   └── validators.py       # 数据校验
├── tests/                  # 单元测试
│   ├── test_csv_reader.py
│   ├── test_payload_builder.py
│   └── test_postman_generator.py
├── fixtures/               # 测试夹具
│   ├── sample.csv
│   └── base_template.json
├── scripts/                # 执行脚本
│   └── generate_collection.py
├── docs/                   # 文档
│   ├── README.md
│   └── API.md
├── requirements.txt        # 依赖管理
├── pytest.ini            # 测试配置
└── Makefile              # 快捷命令
```

## 🚀 快速开始

```bash
# 1. 安装依赖
make install

# 2. 运行测试
make test

# 3. 生成Postman集合
python scripts/generate_collection.py --csv data.csv --output collection.json

# 4. 带外部模板生成
python scripts/generate_collection.py --csv data.csv --template custom_template.json --output collection.json
```

## 🔧 环境变量配置

```bash
export CYBERTRON_API_KEY="your-api-key"
export CYBERTRON_API_TOKEN="your-token"
export API_USERNAME="your-username"
export API_ENDPOINT="https://..."
export TENANT_NAME="AiopsTest"
```

## 📊 测试报告

运行测试后查看：
- HTML报告: `reports/report.html`
- 覆盖率报告: `reports/coverage/index.html`
