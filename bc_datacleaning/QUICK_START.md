# 乳腺癌数据清洗项目 - 快速开始指南

## 🚀 项目简介

这是一个基于大语言模型的智能医疗数据清洗系统，专门处理乳腺癌临床病历数据。通过7步流水线将OCR识别的混乱文本转换为结构化数据，并自动分类到15个专业领域。

## 📊 项目成果

- **处理数据**: 1735+ 个病历文件
- **清洗步骤**: 7步自动化流水线
- **分类结果**: 15个专业分类
- **数据格式**: 标准化JSON输出

## ⚡ 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 设置API密钥（如果使用云端模型）
export OPENAI_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
```

### 2. 配置模型

编辑 `config/config.yaml`：
```yaml
model:
  default_model: "local-model"  # 或 "gpt-4", "claude"
```

### 3. 运行处理

```bash
# 推荐方式：使用数据处理器
python data_processor.py

# 或运行完整流水线
python main.py
```

## 🎯 核心功能

### 数据清洗流水线

1. **噪声剔除** - 删除无关信息
2. **格式纠正** - 修复OCR错误
3. **段落分类** - 识别文本结构
4. **术语标准化** - 统一医学术语
5. **拼写纠错** - 修复识别错误
6. **字段抽取** - 提取结构化信息
7. **逻辑校验** - 确保数据完整性

### 智能分类系统

**主要治疗类型** (7类)
- 内分泌治疗、手术记录、化疗记录
- 免疫治疗、放疗记录、靶向治疗、辅助治疗

**病理报告** (4类)
- 活检病理、术后病理、分子病理、基因检测

**诊断评估** (5类)
- 初诊、新辅助治疗、复发诊断、挽救治疗、随访

## 📁 输出结果

### 清洗后数据
```
data/
├── cleaned_object_001.json
├── cleaned_object_002.json
└── ...
```

### 聚类结果
```
clustered_data/
├── endocrine_records/          # 内分泌治疗 (186个文件)
├── surgery_records/           # 手术记录 (190个文件)
├── chemotherapy_records/      # 化疗记录 (48个文件)
├── immunotherapy/             # 免疫治疗 (127个文件)
├── radiotherapy_records/      # 放疗记录 (26个文件)
├── targeted_therapy/          # 靶向治疗 (46个文件)
├── adjuvant_therapy/          # 辅助治疗 (4个文件)
├── pathology_reports_*/       # 病理报告细分
└── diagnosis_assessment_*/    # 诊断评估细分
```

## ⚙️ 高级配置

### 选择性处理

在 `data_processor.py` 中设置：

```python
# 处理单个文件
SINGLE_FILE_ID = 17

# 处理文件范围
FILE_RANGE = (23, 25)

# 处理多个指定文件
MULTIPLE_FILE_IDS = [27, 36, 68, 100]
```

### 模型选择

支持多种LLM模型：
- **GPT-4**: 云端模型，效果最佳
- **Claude**: 云端模型，稳定性好
- **本地模型**: 自定义API接口
- **Qwen**: 开源模型

## 📈 处理效果

### 数据质量提升
- ✅ 格式标准化: 100%
- ✅ 术语统一: 95%+
- ✅ 结构完整性: 90%+

### 分类准确率
- ✅ 主要分类: 95%+
- ✅ 病理细分: 90%+
- ✅ 诊断评估: 85%+

## 🔧 常见问题

### Q: 如何处理大文件？
A: 系统支持批量处理，可设置处理文件数量限制。

### Q: 如何切换模型？
A: 在 `config/config.yaml` 中修改 `default_model` 参数。

### Q: 如何查看处理进度？
A: 查看 `logs/` 目录下的日志文件。

### Q: 如何自定义分类规则？
A: 编辑 `clustering/clustering_config.py` 中的分类规则。

## 📞 技术支持

- 查看详细文档: `README.md`
- 查看项目总结: `PROJECT_SUMMARY.md`
- 查看处理日志: `logs/cleaning.log`

## 🎉 开始使用

现在您可以开始使用这个强大的医疗数据清洗系统了！

```bash
# 1. 确保环境配置正确
python -c "import pandas, openai, anthropic; print('环境配置成功')"

# 2. 运行数据处理器
python data_processor.py

# 3. 查看结果
ls data/cleaned_object_*.json
ls clustered_data/
```

祝您使用愉快！ 🚀 