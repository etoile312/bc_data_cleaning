# 乳腺癌数据清洗项目

## 项目概述

本项目旨在对来自临床电子报告单扫描件、OCR识别文本或图像识别结果中提取的非结构化病历信息进行清洗、规范化。由于原始文本往往存在信息混杂、格式错乱、误识别频繁等问题，直接进行信息抽取会导致大量噪声或错误字段。

## 系统整体流程设计

整个清洗任务被拆解为若干个明确子任务，每个子任务由一个独立的 LLM 模块负责处理，且在执行前嵌入该步骤专属的知识库提示，以确保大模型只执行当前任务相关的内容，避免引入冗余信息。

### 清洗流程

1. **数据准备** - 从Excel文件中提取指定条件的数据
2. **Step 1: 噪声剔除与段落切分** - 删除与病历无关的信息，按段落组织
3. **Step 2: 格式纠正** - 修复OCR导致的格式错误
4. **Step 3: 段落分类** - 对段落进行粗粒度结构识别
5. **Step 4: 术语标准化** - 将缩写、俗称替换为规范医学术语
6. **Step 5: 拼写与字符识别错误修复** - 基于OCR常见误识别模式纠错
7. **Step 6: 结构化字段抽取** - 从文本中抽取结构化字段数据
8. **Step 7: 字段校验与逻辑补全** - 对提取字段进行语义校验与逻辑推理

## 项目结构

```
bc_datacleaning/
├── config/                     # 配置文件
│   └── config.yaml            # 主配置文件
├── data/                      # 数据目录
│   ├── hx_data.xls           # 原始数据文件
│   └── cleaned_objects.json  # 清洗后的数据
├── knowledge_base/            # 知识库
│   ├── step1_noise_fields.json
│   ├── step2_ocr_errors.json
│   └── step3_paragraph_keywords.json
├── prompts/                   # 提示词模板
│   ├── step1_noise_removal.json
│   ├── step2_format_fix.json
│   └── step3_paragraph_classification.json
├── scripts/                   # 处理脚本
│   ├── data_preparation.py   # 数据准备模块
│   ├── llm_api.py           # LLM API模块
│   ├── step1_noise_removal.py
│   ├── step2_format_fix.py
│   └── step3_paragraph_classification.py
├── main.py                   # 主控脚本
├── requirements.txt          # 依赖包
└── README.md                # 项目说明
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

设置API密钥：

```bash
export OPENAI_API_KEY="your_openai_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

### 3. 配置模型参数

编辑 `config/config.yaml` 文件，根据需要调整模型配置和流程控制参数。

## 使用方法

### 运行完整流水线

```bash
python main.py
```

### 运行单个步骤

```bash
# 运行数据准备
python main.py --step data_preparation

# 运行噪声剔除
python main.py --step step1_noise_removal

# 运行格式纠正
python main.py --step step2_format_fix

# 运行段落分类
python main.py --step step3_paragraph_classification
```

### 使用自定义配置文件

```bash
python main.py --config your_config.yaml
```

## 数据格式

### 输入数据

- 文件格式：Excel (.xls/.xlsx)
- 数据位置：C列为疾病类型，J列为OCR识别结果
- 筛选条件：C列内容为"乳腺癌"

### 输出数据

清洗后的数据以JSON格式保存，包含以下信息：

- 原始文本
- 清洗后的文本
- 段落分类结果
- 处理步骤的详细信息

## 配置说明

### 模型配置

```yaml
model:
  default_model: "gpt-4"
  models:
    gpt-4:
      api_key: "${OPENAI_API_KEY}"
      temperature: 0.1
      max_tokens: 4000
```

### 流程控制

```yaml
pipeline:
  steps:
    step1_noise_removal: true
    step2_format_fix: true
    step3_paragraph_classification: true
  batch_size: 10
  save_intermediate: true
```

## 扩展和定制

### 添加新的清洗步骤

1. 在 `scripts/` 目录下创建新的步骤模块
2. 在 `knowledge_base/` 目录下添加相应的知识库文件
3. 在 `prompts/` 目录下添加提示词模板
4. 在 `main.py` 中集成新步骤

### 自定义知识库

编辑 `knowledge_base/` 目录下的JSON文件，添加或修改相应的规则和映射关系。

### 调整提示词

编辑 `prompts/` 目录下的JSON文件，根据实际需求调整LLM提示词。

## 注意事项

1. 确保API密钥正确设置
2. 大文件处理时注意内存使用
3. 建议先在小数据集上测试
4. 定期备份重要的中间结果

## 故障排除

### 常见问题

1. **API调用失败**：检查API密钥和网络连接
2. **内存不足**：减少批处理大小
3. **文件读取错误**：检查文件路径和格式

### 日志查看

日志文件保存在 `logs/cleaning.log`，可以查看详细的处理过程和错误信息。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。在提交代码前，请确保：

1. 代码符合PEP 8规范
2. 添加适当的注释和文档
3. 通过所有测试

## 许可证

本项目采用MIT许可证。 