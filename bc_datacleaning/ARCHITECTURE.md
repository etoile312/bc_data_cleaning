# 乳腺癌数据清洗项目 - 技术架构文档

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        乳腺癌数据清洗系统                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   数据输入   │    │   数据清洗   │    │   数据输出   │         │
│  │  (Excel)    │───▶│  (7步流水线) │───▶│  (JSON)     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                              │                                 │
│                              ▼                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   知识库     │    │   智能聚类   │    │   分类结果   │         │
│  │  (规则库)    │◀───│  (15分类)   │───▶│  (目录结构)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心模块设计

### 1. 数据输入模块

#### 功能职责
- Excel文件读取和解析
- 数据格式验证
- 乳腺癌数据筛选

#### 技术实现
```python
class DataPreparation:
    def __init__(self):
        self.excel_file = "hx_data.xls"
        self.disease_column = "C"  # 疾病类型列
        self.content_column = "J"  # OCR内容列
    
    def extract_breast_cancer_data(self):
        # 读取Excel文件
        # 筛选乳腺癌数据
        # 返回清洗对象列表
```

#### 数据流
```
Excel文件 → Pandas读取 → 数据筛选 → 清洗对象列表
```

### 2. LLM API模块

#### 功能职责
- 多模型API统一接口
- 请求管理和错误处理
- 响应解析和格式化

#### 技术实现
```python
class LLMAPI:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.models = {
            'gpt-4': OpenAIClient,
            'claude': AnthropicClient,
            'local-model': LocalModelClient,
            'qwen-model': QwenClient
        }
    
    def call_model(self, prompt, model_name=None):
        # 选择模型
        # 发送请求
        # 处理响应
        # 错误重试
```

#### 支持的模型
- **GPT-4**: OpenAI API
- **Claude**: Anthropic API  
- **本地模型**: 自定义API接口
- **Qwen**: 开源模型API

### 3. 数据清洗流水线

#### 流水线架构
```
原始文本 → Step1 → Step2 → Step3 → Step4 → Step5 → Step6 → Step7 → 结构化数据
```

#### Step 1: 噪声剔除与段落切分
```python
class NoiseRemoval:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.noise_patterns = self._load_noise_patterns()
    
    def remove_noise(self, text):
        # 识别噪声内容
        # 删除无关信息
        # 段落重新组织
```

#### Step 2: 格式纠正
```python
class FormatFix:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.ocr_errors = self._load_ocr_errors()
    
    def fix_format(self, text):
        # 修复OCR错误
        # 统一格式
        # 纠正标点符号
```

#### Step 3: 段落分类
```python
class ParagraphClassification:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.paragraph_keywords = self._load_keywords()
    
    def classify_paragraphs(self, text):
        # 段落分割
        # 内容分析
        # 分类标注
```

#### Step 4: 术语标准化
```python
class TerminologyStandardization:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.terminology_dict = self._load_terminology()
    
    def standardize_terminology(self, text):
        # 术语识别
        # 标准化替换
        # 一致性检查
```

#### Step 5: 拼写与字符识别错误修复
```python
class SpellingCorrection:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.spelling_patterns = self._load_spelling_patterns()
    
    def correct_spelling(self, text):
        # 拼写错误检测
        # 字符识别纠错
        # 上下文验证
```

#### Step 6: 结构化字段抽取
```python
class FieldExtraction:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.field_schema = self._load_field_schema()
    
    def extract_fields(self, text):
        # 字段识别
        # 信息抽取
        # 结构化输出
```

#### Step 7: 字段校验与逻辑补全
```python
class FieldValidation:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.validation_rules = self._load_validation_rules()
    
    def validate_fields(self, fields):
        # 语义校验
        # 逻辑推理
        # 信息补全
```

### 4. 智能聚类模块

#### 聚类架构
```
清洗后数据 → 标签解析 → 内容匹配 → 分类决策 → 文件复制 → 聚类结果
```

#### 标签解析器
```python
class LabelParser:
    def __init__(self):
        self.category_mapping = self._load_category_mapping()
    
    def parse_labels(self, text):
        # 关键词匹配
        # 标签识别
        # 分类映射
```

#### 数据聚类器
```python
class DataClusterer:
    def __init__(self, label_parser):
        self.label_parser = label_parser
        self.clusters = {}
    
    def cluster_data(self, data_dir, output_dir):
        # 文件遍历
        # 内容分析
        # 分类决策
        # 文件复制
```

#### 分类体系
```
主要治疗类型 (7类)
├── 内分泌治疗记录
├── 手术记录
├── 化疗记录
├── 免疫治疗
├── 放疗记录
├── 靶向治疗
└── 辅助治疗

病理报告细分 (4类)
├── 活检病理
├── 术后病理
├── 分子病理
└── 基因检测

诊断评估细分 (5类)
├── 初诊评估
├── 新辅助治疗
├── 复发诊断
├── 挽救治疗
└── 随访评估
```

### 5. 知识库模块

#### 知识库结构
```
knowledge_base/
├── step1_ocr_errors.json      # OCR错误模式
├── step2_noise_fields.json    # 噪声字段识别
├── step3_paragraph_keywords.json # 段落关键词
├── step4_terminology_dict.json  # 医学术语词典
├── step5_spelling_patterns.json # 拼写错误模式
├── step6_field_schema.json    # 字段抽取模式
└── step7_validation_rules.json # 校验规则
```

#### 知识库管理
```python
class KnowledgeBase:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.knowledge = {}
    
    def load_knowledge(self, step_name):
        # 加载知识库文件
        # 解析JSON格式
        # 缓存到内存
```

### 6. 配置管理模块

#### 配置文件结构
```yaml
# config/config.yaml
model:
  default_model: "local-model"
  models:
    gpt-4:
      api_key: "${OPENAI_API_KEY}"
      temperature: 0.1
      max_tokens: 4000

pipeline:
  steps:
    step1_noise_removal: true
    step2_format_fix: true
    # ... 其他步骤

data:
  input_file: "hx_data.xls"
  output_dir: "data"
  temp_dir: "temp"

logging:
  level: "INFO"
  file: "logs/cleaning.log"
```

#### 配置管理器
```python
class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_config()
    
    def get_model_config(self, model_name):
        # 获取模型配置
        # 环境变量替换
        # 默认值处理
```

### 7. 日志监控模块

#### 日志系统设计
```python
class LogManager:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        # 配置日志格式
        # 设置日志级别
        # 创建日志处理器
```

#### 日志内容
- 处理进度跟踪
- 错误信息记录
- 性能指标统计
- 质量评估结果

## 数据流设计

### 主数据流
```
1. 数据输入
   Excel文件 → 数据提取 → 乳腺癌筛选 → 清洗对象列表

2. 数据清洗
   原始文本 → Step1(噪声剔除) → Step2(格式纠正) → Step3(段落分类) 
   → Step4(术语标准化) → Step5(拼写纠错) → Step6(字段抽取) 
   → Step7(逻辑校验) → 结构化数据

3. 数据聚类
   清洗后数据 → 标签解析 → 内容匹配 → 分类决策 → 文件复制 → 聚类结果
```

### 控制流
```
1. 配置加载
   配置文件 → 配置解析 → 参数验证 → 系统初始化

2. 模型选择
   模型配置 → API客户端 → 连接测试 → 模型就绪

3. 错误处理
   异常捕获 → 错误分类 → 重试机制 → 降级处理
```

## 性能优化设计

### 1. 批处理机制
```python
class BatchProcessor:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
        self.batch_queue = []
    
    def process_batch(self, items):
        # 批量处理
        # 并发控制
        # 内存管理
```

### 2. 缓存机制
```python
class CacheManager:
    def __init__(self):
        self.knowledge_cache = {}
        self.model_cache = {}
    
    def get_cached_result(self, key):
        # 缓存查找
        # 缓存更新
        # 缓存清理
```

### 3. 并发处理
```python
import concurrent.futures

class ConcurrentProcessor:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers)
    
    def process_concurrently(self, tasks):
        # 任务分发
        # 并发执行
        # 结果收集
```

## 扩展性设计

### 1. 插件化架构
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name, plugin):
        # 插件注册
        # 接口验证
        # 依赖检查
    
    def execute_plugin(self, name, *args, **kwargs):
        # 插件调用
        # 参数传递
        # 结果返回
```

### 2. 模块化设计
- 每个清洗步骤独立模块
- 标准化的接口定义
- 可插拔的组件设计

### 3. 配置驱动
- 基于配置的流程控制
- 动态参数调整
- 运行时配置更新

## 安全性设计

### 1. 数据安全
- 敏感信息脱敏
- 数据访问控制
- 传输加密

### 2. API安全
- API密钥管理
- 请求频率限制
- 错误信息过滤

### 3. 系统安全
- 输入验证
- 异常处理
- 资源限制

## 监控和运维

### 1. 性能监控
- 处理时间统计
- 内存使用监控
- API调用统计

### 2. 质量监控
- 清洗质量评估
- 分类准确率统计
- 错误率监控

### 3. 运维支持
- 日志分析
- 问题诊断
- 性能调优

## 总结

本系统采用模块化、可扩展的架构设计，通过7步流水线实现医疗数据的自动化清洗，通过智能聚类实现数据的专业分类。系统具有良好的性能、可维护性和扩展性，能够有效处理大规模的医疗数据清洗任务。 