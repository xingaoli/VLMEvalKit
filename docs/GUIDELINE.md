# VLMEvalKit 使用指南 - LLaMA-Factory API 模式部署

本文档记录如何使用 VLMEvalKit 通过 LLaMA-Factory 部署的 Qwen3.5-0.8B 模型进行评估。

## 环境要求

- Python 3.12.12
- uv (Python 包管理器)
- NVIDIA CUDA 12.5 (或兼容版本)
- 16GB+ 内存
- LLaMA-Factory 环境
- Qwen3.5-0.8B 模型

## 目录结构

```
/home/xingao/code/
├── LLaMA-Factory/          # LLaMAFactory 项目
│   ├── ckpts/Qwen3.5-0.8B/ # 模型权重
│   └── .venv/              # LLaMA-Factory 虚拟环境
└── VLMEvalKit/             # VLMEvalKit 项目
    ├── .venv/              # VLMEvalKit 虚拟环境
    ├── data/               # 数据集存储
    └── docs/               # 文档
```

## 步骤 1: 创建 VLMEvalKit 虚拟环境

```bash
cd /home/xingao/code/VLMEvalKit

# 使用 uv 创建 Python 3.12.12 虚拟环境
uv venv .venv --python 3.12.12

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖（包含 nest-asyncio）
uv pip install -r requirements.txt
uv pip install nest-asyncio

# 安装 rouge 包（某些评估需要）
uv pip install rouge
```

**注意**: 如果使用 torch，需要安装与 CUDA 12.5 兼容的版本：
```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

## 步骤 2: 启动 LLaMA-Factory API 服务

```bash
cd /home/xingao/code/LLaMA-Factory
source .venv/bin/activate

# 启动 API 服务（模型: Qwen3.5-0.8B, template: qwen3_vl_nothink）
python src/api.py \
  --model_name_or_path ckpts/Qwen3.5-0.8B \
  --template qwen3_vl_nothink \
  --infer_backend huggingface
```

服务启动后，访问 http://localhost:8000/docs 查看 API 文档。

## 步骤 3: 配置 VLMEvalKit 模型

在 `vlmeval/config.py` 中添加自定义模型配置（第 2577 行附近）：

```python
# Custom API Models (User-defined)
custom_api_series = {
    'Qwen3.5-0.8B-LMDeploy': partial(
        LMDeployAPI,
        api_base='http://127.0.0.1:8000/v1/chat/completions',
        model='gpt-3.5-turbo',
        max_tokens=16384,
        temperature=0.0,
        retry=5,
        timeout=120,
    )
}

# 添加到 model_groups 列表
model_groups.extend([custom_api_series])
```

## 步骤 4: 设置数据集目录

数据集默认下载到 `~/LMUData`，可通过环境变量自定义：

```bash
# 方式 1: 环境变量
export LMUData="/home/xingao/code/VLMEvalKit/data"

# 方式 2: 代码中设置（推荐）
# 在运行命令中添加
```

数据集文件结构：
```
data/
├── MMBench_DEV_EN_V11.tsv   # 数据集文件
├── images/MMBench_V11/      # 图像文件
└── POPE.tsv                  # 其他数据集
```

## 步骤 5: 运行评估

### 清除代理（重要！）

```bash
export ALL_PROXY=""
export all_proxy=""
export http_proxy=""
export https_proxy=""
```

### 运行完整评估

```bash
cd /home/xingao/code/VLMEvalKit
source .venv/bin/activate

# 设置数据集目录
export LMUData="$(pwd)/data"

# 运行 MMBench 评估
python run.py --data MMBench_DEV_EN_V11 --model Qwen3.5-0.8B-LMDeploy
```

### 快速测试（10 个样本）

```bash
python quick_test.py
```

## API 服务连接测试

换机器或排查问题时，先测试 API 连接：

```bash
python test_api_connection.py
```

## 常见问题

### 1. 代理设置导致 API 调用失败

**症状**: `Failed to obtain answer via API` 或连接超时

**解决**:
```bash
# 清除所有代理环境变量
export ALL_PROXY=""
export all_proxy=""
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""

# 或者设置 NO_PROXY
export NO_PROXY="localhost,127.0.0.1"
```

### 2. API 端点错误

**症状**: 404 Not Found 或连接被拒绝

**解决**: 确保 `api_base` 包含完整路径：
```bash
# 正确
export LMDEPLOY_API_BASE="http://127.0.0.1:8000/v1/chat/completions"

# 错误
export LMDEPLOY_API_BASE="http://127.0.0.1:8000/v1"
```

### 3. 图像处理问题

**症状**: 图像无法加载

**解决**: 完整评估流程会自动处理图像：
- base64 解码 → 临时文件 → API 调用
- 无需手动干预

### 4. 内存不足 (OOM)

**症状**: API 服务被 SIGKILL (退出码 137) 杀死

**解决**:
- 使用更小的模型
- 或减小 batch size
- 或增加系统内存

## 支持的数据集

运行以下命令查看所有支持的数据集：

```bash
python -c "
from vlmeval.dataset import SUPPORTED_DATASETS
print('支持的数据集:')
for ds in sorted(SUPPORTED_DATASETS):
    print(f'  - {ds}')
"
```

## 文件清单

### 配置文件
- `vlmeval/config.py` - 模型配置

### 测试脚本
- `quick_test.py` - 快速测试（10样本）
- `test_api_connection.py` - API 连接验证

### 数据目录
- `data/` - 数据集存储

## API 服务重启

如果 API 服务崩溃或需要重启：

```bash
# 1. 停止旧进程
pkill -f "python src/api.py"

# 2. 重新启动
cd /home/xingao/code/LLaMA-Factory
source .venv/bin/activate
python src/api.py \
  --model_name_or_path ckpts/Qwen3.5-0.8B \
  --template qwen3_vl_nothink \
  --infer_backend huggingface
```

## 性能参考

- Qwen3.5-0.8B + MMBench_DEV_EN_V11
- 样本数: 4876
- 速度: ~6 秒/样本
- 预计时间: ~8 小时

## 注意事项

1. **代理问题**: 必须清除所有代理设置，否则会导致 API 调用失败
2. **API 端点**: 必须包含完整路径 `/v1/chat/completions`
3. **数据集路径**: 使用 `LMUData` 环境变量指定
4. **内存占用**: Qwen3.5-0.8B 约占用 563Mi GPU 内存
5. **API 服务稳定性**: 长时间运行可能需要监控和自动重启

## 更新日期

2026-03-25
