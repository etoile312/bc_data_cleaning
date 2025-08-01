# 乳腺癌医学数据增强系统 (重构版本)

## 📋 项目概述

本项目是乳腺癌医学数据增强系统的重构版本，采用模块化、配置化的架构设计，提供完整的医学数据生成流水线。

### 🎯 主要功能

1. **结构化数据生成** - 基于规则和逻辑生成符合医学逻辑的结构化病例数据
2. **临床风格文本生成** - 将结构化数据转换为自然、专业的临床风格文本
3. **噪声注入** - 模拟OCR识别错误，生成带噪声的医学文本
4. **配置化管理** - 所有参数、提示词、API配置均可外部化配置

### 🏗️ 架构设计

```
refactored_bc_medical_augmenter/
├── structured/           # 结构化数据生成模块
│   ├── segment_groups.py      # 字段分组定义
│   ├── field_parser.py        # 字段规则解析器
│   ├── field_sampler.py       # 字段值采样器
│   ├── combine_segments.py    # 段落组合器
│   └── generate_structured.py # 结构化数据生成主入口
├── clinical/            # 临床风格文本生成模块
│   ├── preprocess_rules.py    # 字段预处理规则
│   ├── text_generator.py      # 文本生成器
│   └── generate_clinical.py   # 临床文本生成主入口
├── noise/              # 噪声注入模块
│   ├── noise_types.py         # 噪声类型定义
│   ├── noise_injector.py      # 噪声注入器
│   └── generate_noisy.py      # 噪声注入主入口
├── core/               # 核心功能模块
│   └── llm_api.py            # LLM API调用
├── config/             # 配置管理
│   ├── model_api.json        # 模型API配置
│   ├── noise_config.json     # 噪声配置
│   └── prompts/              # 提示词模板
│       ├── clinical_generation.txt
│       ├── clinical_refine.txt
│       └── noise/            # 噪声提示词
└── main.py             # 主入口脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖包：`requests`, `json`, `random`, `re`, `string`

### 安装依赖

```bash
pip install requests
```

### 运行方式

#### 1. 完整流水线 (推荐)

```bash
python main.py --mode full
```

#### 2. 分模块运行

```bash
# 仅生成结构化数据
python main.py --mode structured

# 仅生成临床风格文本
python main.py --mode clinical

# 仅注入噪声
python main.py --mode noise
```

#### 3. 模块测试

```bash
python main.py --mode test
```

## 📊 功能模块详解

### 1. 结构化数据生成 (structured/)

**功能**：根据医学规则和逻辑生成符合真实病例特征的结构化数据

**核心组件**：
- `FieldRuleParser`: 解析字段定义和逻辑规则
- `FieldSampler`: 根据规则采样字段值
- `SegmentCombiner`: 组合不同字段组生成完整病例

**输出**：`data/combined_cases.json`

### 2. 临床风格文本生成 (clinical/)

**功能**：将结构化数据转换为自然、专业的临床风格文本

**核心组件**：
- `preprocess_rules.py`: 字段预处理和表达规则
- `text_generator.py`: 文本生成主逻辑
- 两阶段生成：结构化转初稿 → 临床风格润色

**输出**：`data/generated_cases/`

### 3. 噪声注入 (noise/)

**功能**：模拟OCR识别错误，生成带噪声的医学文本

**噪声类型**：
- 行政信息冗余
- 医院信息噪声
- 检查记录噪声
- 电子记录痕迹
- 地址信息噪声
- 重复内容噪声
- 核酸检测记录
- 表格噪声
- 详细检验结果
- 串行噪声
- 医生建议
- 删除空格
- 电脑菜单

**输出**：`data/generated_cases/` (带 `_noisy` 后缀)

### 4. 配置管理 (config/)

**配置文件**：
- `model_api.json`: LLM API配置
- `noise_config.json`: 噪声类型和概率配置
- `prompts/`: 各种提示词模板

## ⚙️ 配置说明

### 模型API配置 (config/model_api.json)

```json
{
  "url": "http://192.168.19.211:8000/v1/model/single_report",
  "timeout": 10,
  "headers": {
    "Content-Type": "application/json"
  }
}
```

### 噪声配置 (config/noise_config.json)

```json
{
  "noise_types": {
    "administrative": {"prob": 0.2, "length": [50, 100]},
    "hospital_info": {"prob": 0.1, "length": [30, 80]}
  },
  "injection_stages": {
    "content_level": {"prob": 0.7, "num_noise": [1, 3]},
    "ocr_level": {"prob": 0.3, "char_error_rate": 0.02}
  }
}
```

## 📁 输出文件结构

```
data/
├── combined_cases.json              # 结构化病例数据
├── segments/                        # 字段组样本池
│   ├── basic_info_pool.json
│   ├── pathology_pool.json
│   └── ...
└── generated_cases/                 # 生成的文本文件
    ├── case_001.json               # 临床风格文本 (JSON)
    ├── case_001.txt                # 临床风格文本 (TXT)
    ├── case_001_noisy.txt          # 带噪声文本
    ├── all_cases.json              # 合并结果
    └── all_cases_with_noise.json   # 带噪声合并结果
```

## 🔧 自定义配置

### 修改噪声类型

1. 在 `noise/noise_types.py` 中添加新的噪声生成函数
2. 在 `NOISE_TYPE_MAP` 中注册新函数
3. 在 `config/noise_config.json` 中配置概率和参数

### 修改提示词

直接编辑 `config/prompts/` 目录下的提示词模板文件。

### 修改字段规则

编辑 `rules/breast_cancer_rules.json` 文件，修改字段定义和逻辑规则。

## 🧪 测试

运行模块测试：

```bash
python main.py --mode test
```

测试内容包括：
- 结构化数据模块功能测试
- 临床文本模块功能测试
- 噪声注入模块功能测试
- API调用模块功能测试

## 📈 性能优化

1. **批量处理**：支持批量生成和批量API调用
2. **配置缓存**：配置文件加载后缓存，避免重复读取
3. **错误处理**：完善的异常处理和重试机制
4. **内存优化**：流式处理大文件，避免内存溢出

## 🔍 故障排除

### 常见问题

1. **API调用失败**
   - 检查 `config/model_api.json` 中的URL配置
   - 确认网络连接和API服务状态

2. **配置文件错误**
   - 检查JSON格式是否正确
   - 确认文件路径和权限

3. **模块导入失败**
   - 确认Python路径设置
   - 检查依赖包安装

### 日志输出

系统会输出详细的执行日志，包括：
- 处理进度
- 错误信息
- 生成统计
- 模块状态

## 📝 开发指南

### 添加新功能

1. 在对应模块目录下创建新文件
2. 实现功能逻辑
3. 在主入口脚本中集成
4. 添加测试用例

### 代码规范

- 使用类型注解
- 添加详细的文档字符串
- 遵循PEP 8代码风格
- 添加异常处理

## 📄 许可证

本项目遵循原项目的许可证条款。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

---

**重构版本特点**：
- ✅ 模块化架构，职责清晰
- ✅ 配置外部化，易于维护
- ✅ 完整的错误处理
- ✅ 详细的文档说明
- ✅ 全面的测试覆盖
- ✅ 高性能批量处理 