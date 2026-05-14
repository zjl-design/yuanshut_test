# -*- coding: utf-8 -*-
"""生成测试统计摘要"""
import json
import os

summary_file = 'reports/summary.txt'
os.makedirs('reports', exist_ok=True)

try:
    with open('reports/test_results.json', 'r') as f:
        data = json.load(f)

    total = data.get('summary', {}).get('total', 0)
    passed = data.get('summary', {}).get('passed', 0)
    failed = data.get('summary', {}).get('failed', 0)
    error = data.get('summary', {}).get('error', 0)
    skipped = data.get('summary', {}).get('skipped', 0)
    duration = data.get('duration', 0)

    lines = []
    lines.append("=== 测试统计 ===")
    lines.append(f"总用例数: {total}")
    lines.append(f"通过: {passed}")
    lines.append(f"失败: {failed}")
    lines.append(f"错误: {error}")
    lines.append(f"跳过: {skipped}")
    lines.append(f"耗时: {duration:.2f}s")
    if total > 0:
        lines.append(f"通过率: {passed/total*100:.1f}%")
    else:
        lines.append("通过率: N/A")

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print('\n'.join(lines))
except Exception as e:
    print(f"生成摘要失败: {e}")