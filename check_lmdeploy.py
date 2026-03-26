#!/usr/bin/env python3
"""
检查 LMDeployAPI 导入问题的诊断脚本
在另一台机器上运行: python check_lmdeploy.py
"""

import sys
sys.path.insert(0, '/home/xingao/code/VLMEvalKit')

print("=== 1. 检查 api/__init__.py 是否导入 LMDeployAPI ===")
with open('/home/xingao/code/VLMEvalKit/vlmeval/api/__init__.py') as f:
    content = f.read()
    if 'LMDeployAPI' in content:
        print("✓ api/__init__.py 中有 LMDeployAPI")
        for i, line in enumerate(content.split('\n'), 1):
            if 'LMDeployAPI' in line and ('from' in line or 'import' in line):
                print(f"  第 {i} 行: {line.strip()}")
    else:
        print("✗ api/__init__.py 中没有 LMDeployAPI")

print("\n=== 2. 检查 config.py custom_api_series ===")
with open('/home/xingao/code/VLMEvalKit/vlmeval/config.py') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[2575:2590], 2576):
        if 'custom_api_series' in line or 'LMDeployAPI' in line:
            print(f"第 {i} 行: {line.rstrip()}")

print("\n=== 3. 尝试直接导入 LMDeployAPI ===")
try:
    from vlmeval.api.lmdeploy import LMDeployAPI
    print("✓ 直接导入 LMDeployAPI 成功")
    print(f"  LMDeployAPI = {LMDeployAPI}")
except Exception as e:
    print(f"✗ 直接导入失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 4. 尝试从 api 模块导入 LMDeployAPI ===")
try:
    from vlmeval.api import LMDeployAPI
    print("✓ from vlmeval.api import LMDeployAPI 成功")
    print(f"  LMDeployAPI = {LMDeployAPI}")
except Exception as e:
    print(f"✗ 从 api 导入失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 5. 检查 api 模块的 __all__ ===")
try:
    import vlmeval.api as api_module
    if hasattr(api_module, '__all__'):
        print(f"__all__ 包含 {len(api_module.__all__)} 个项目")
        if 'LMDeployAPI' in api_module.__all__:
            print("✓ LMDeployAPI 在 __all__ 中")
        else:
            print("✗ LMDeployAPI 不在 __all__ 中")
            print(f"  __all__ = {api_module.__all__}")
    else:
        print("✗ api 模块没有 __all__ 属性")
except Exception as e:
    print(f"✗ 检查失败: {type(e).__name__}: {e}")

print("\n=== 6. 检查 LMDeployAPI 是否在 api 模块命名空间中 ===")
try:
    import vlmeval.api as api_module
    if hasattr(api_module, 'LMDeployAPI'):
        print(f"✓ LMDeployAPI 在命名空间中: {api_module.LMDeployAPI}")
    else:
        print("✗ LMDeployAPI 不在命名空间中")
        print(f"  可用的属性: {[x for x in dir(api_module) if not x.startswith('_')][:10]}...")
except Exception as e:
    print(f"✗ 检查失败: {type(e).__name__}: {e}")

print("\n=== 7. 尝试导入 config ===")
try:
    from vlmeval import config
    print("✓ 导入 config 成功")
except Exception as e:
    print(f"✗ 导入 config 失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
