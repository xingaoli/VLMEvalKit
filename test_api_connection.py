#!/usr/bin/env python3
"""测试连接到 LLaMA-Factory API 服务"""

import os

# 清除代理设置，避免 socks 代理干扰
for var in ['http_proxy', 'https_proxy', 'all_proxy', 'ALL_PROXY',
            'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy']:
    if var in os.environ:
        del os.environ[var]

os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['LMDEPLOY_API_BASE'] = 'http://127.0.0.1:8000/v1/chat/completions'
os.environ['LMDEPLOY_API_KEY'] = 'sk-xxx'

from vlmeval.api import LMDeployAPI

# 创建模型客户端（启用详细日志）
model = LMDeployAPI(model='qwen3.5-0.8b', verbose=True)

# 测试纯文本
print("=== 测试纯文本 ===")
response = model.generate(['你好，请介绍一下你自己'])
print(f"回答: {response}\n")

# 测试图像理解（如果有测试图片）
print("=== 测试图像理解 ===")
from PIL import Image

# 创建一个简单的测试图片
test_img = Image.new('RGB', (100, 100), color='red')
test_img.save('/tmp/test_image.png')

response = model.generate([
    {'type': 'image', 'value': '/tmp/test_image.png'},
    {'type': 'text', 'value': '这张图片是什么颜色？'}
])
print(f"回答: {response}\n")

print("✓ 测试完成！API 连接正常")
