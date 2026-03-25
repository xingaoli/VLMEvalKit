#!/usr/bin/env python3
"""快速测试 - 只测试 10 个样本"""

import os

# 清除代理
for var in ['http_proxy', 'https_proxy', 'all_proxy', 'ALL_PROXY',
            'HTTP_PROXY', 'HTTPS_PROXY']:
    if var in os.environ:
        del os.environ[var]

os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['LMUData'] = os.path.join(os.getcwd(), 'data')

from vlmeval.dataset import build_dataset
from vlmeval.api import LMDeployAPI

print('=== 创建 API 模型 ===')
model = LMDeployAPI(
    api_base='http://127.0.0.1:8000/v1/chat/completions',
    model='gpt-3.5-turbo',
    max_tokens=256,
    retry=2,
    timeout=60
)

print('\n=== 加载数据集 ===')
ds = build_dataset('MMBench_DEV_EN_V11')
print(f'总样本数: {len(ds)}')
print(f'将测试前 10 个样本\n')

# 测试前 10 个样本
for i in range(10):
    sample = ds[i]
    print(f"\n--- 样本 {i+1} ---")
    print(f"问题: {sample['question'][:80]}...")
    print(f"答案: {sample['answer']}")

    # 使用数据集自带的格式化方法
    # get_data 会返回正确的格式，包括图像
    from vlmeval.vlm.qwen2_vl.prompt import Qwen2VLPromptMixin

    # 使用数据集内部的方式构建输入
    # MMBench 使用 ImageMCQDataset，它会正确处理图像
    msg = ds.dump_image(sample)
    if isinstance(msg, list):
        inputs = [{'type': 'image', 'value': p} for p in msg]
    else:
        inputs = [msg]

    # 添加问题文本
    question_text = f"{sample['question']}\nA: {sample['A']}\nB: {sample['B']}\nC: {sample['C']}\nD: {sample['D']}"
    inputs.append({'type': 'text', 'value': question_text})

    result = model.generate(inputs)
    print(f"预测: {result[:100]}...")

    # 简单检查是否正确
    if sample['answer'] in result:
        print('✓ 正确!')
    else:
        print('✗ 错误')

print('\n=== 测试完成 ===')
