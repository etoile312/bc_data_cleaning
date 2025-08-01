# 乳腺癌病历数据增强生成系统（重构版）

## 项目结构

```
bc_medical_augmenter/
  ├── structured/           # 结构化数据生成相关
  │     ├── segment_groups.py
  │     ├── field_parser.py
  │     ├── field_sampler.py
  │     ├── combine_segments.py
  │     └── generate_structured.py
  ├── clinical/             # 临床风格文本生成相关
  │     ├── preprocess_rules.py
  │     ├── text_generator.py
  │     └── generate_clinical.py
  ├── noise/                # 噪声注入相关
  │     ├── noise_types.py
  │     ├── noise_injector.py
  │     └── generate_noisy.py
  ├── core/                 # 通用API、工具
  │     └── llm_api.py
  ├── config/               # 配置与提示语模板
  │     ├── model_api.json
  │     ├── noise_config.json
  │     └── prompts/
  │           ├── clinical_generation.txt
  │           ├── clinical_refine.txt
  │           └── noise/
  │                 ├── administrative.txt
  │                 └── computer_menu.txt
  ├── data/                 # 数据目录
  ├── rules/                # 规则目录
  ├── requirements.txt
  └── README_REFACTORED.md
```

## 工作流

1. **结构化数据生成**
   - 入口：`structured/generate_structured.py`
   - 输出：`data/combined_cases.json`

2. **临床风格文本生成**
   - 入口：`clinical/generate_clinical.py`
   - 输入：`data/combined_cases.json`
   - 输出：`data/generated_cases/*.json`、`*.txt`

3. **带噪声文本生成**
   - 入口：`noise/generate_noisy.py`
   - 输入：`data/generated_cases/*.json`
   - 输出：`data/generated_cases/*_noisy.txt`

## 配置与扩展
- 所有大模型提示语、噪声注入参数、API地址均在 `config/` 下可灵活配置
- 新增噪声类型只需在 `noise/noise_types.py` 增加函数、在 `config/noise_config.json` 配置概率、在 `config/prompts/noise/` 增加模板
- 字段预处理规则集中在 `clinical/preprocess_rules.py`，便于维护

## 依赖
- Python 3.7+
- requests

## 运行示例
```bash
python structured/generate_structured.py
python clinical/generate_clinical.py
python noise/generate_noisy.py
```

---

如需自定义提示语、噪声类型、注入概率等，直接修改 `config/` 下相关文件即可。 