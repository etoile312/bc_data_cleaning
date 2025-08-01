#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4: 术语标准化
将缩写、俗称或OCR偏误词替换为统一、规范的医学术语
"""

import json
import re
from typing import List, Dict, Any
from pathlib import Path
from .llm_api import LLMAPI


class TerminologyStandardization:
    """术语标准化类"""
    
    def __init__(self, llm_api: LLMAPI):
        """
        初始化术语标准化器
        
        Args:
            llm_api: LLM API实例
        """
        self.llm_api = llm_api
        self.knowledge_base = self._load_knowledge_base()
        self.prompt_template = self._load_prompt_template()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """加载知识库"""
        knowledge_file = Path("knowledge_base/step4_terminology_dict.json")
        
        print(f"尝试加载知识库文件: {knowledge_file.absolute()}")
        
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"成功加载知识库，包含 {len(data)} 个类别")
                    return data
            except Exception as e:
                print(f"加载知识库文件失败: {e}")
                return self._get_default_knowledge_base()
        else:
            print(f"知识库文件不存在: {knowledge_file.absolute()}")
            return self._get_default_knowledge_base()
    
    def _get_default_knowledge_base(self) -> Dict[str, Any]:
        """获取默认知识库"""
        return {
                "medical_abbreviations": {
                    "WBC": "白细胞",
                    "RBC": "红细胞", 
                    "Hb": "血红蛋白",
                    "PLT": "血小板",
                    "ER": "雌激素受体",
                    "PR": "孕激素受体",
                    "HER2": "人表皮生长因子受体2",
                    "Ki67": "增殖指数",
                    "Ca": "癌",
                    "Ca.": "癌",
                    "CA": "癌",
                    "CA.": "癌"
                },
                "unit_standardization": {
                    "g/l": "g/L",
                    "mg/dl": "mg/dL", 
                    "ng/ml": "ng/mL",
                    "pg/ml": "pg/mL",
                    "u/l": "U/L",
                    "mmol/l": "mmol/L",
                    "10^9/l": "109/L",
                    "10^12/l": "1012/L",
                    "10^6/l": "106/L"
                },
                "breast_cancer_terms": {
                    "乳腺Ca": "乳腺癌",
                    "乳腺ca": "乳腺癌",
                    "乳腺CA": "乳腺癌",
                    "乳腺恶性肿瘤": "乳腺癌",
                    "乳腺浸润性癌": "浸润性乳腺癌",
                    "乳腺导管癌": "导管癌",
                    "乳腺小叶癌": "小叶癌"
                }
            }
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        prompt_file = Path("prompts/step4_terminology_standardization.json")
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("prompt", "")
        else:
            return ""
    
    def _load_prompt_config(self) -> Dict[str, Any]:
        """加载完整的提示词配置"""
        prompt_file = Path("prompts/step4_terminology_standardization.json")
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_config = json.load(f)
            return prompt_config
        except Exception as e:
            print(f"加载提示词配置失败: {e}")
            return {}
    
    def standardize_terminology_with_dict(self, text: str) -> str:
        """
        使用字典进行术语标准化
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        # 检查知识库是否正确加载
        if self.knowledge_base is None:
            print("警告：知识库未正确加载，使用默认映射")
            return text
        
        # 应用医学术语映射
        if "medical_abbreviations" in self.knowledge_base:
            for abbreviation, full_term in self.knowledge_base["medical_abbreviations"].items():
                text = re.sub(r'\b' + re.escape(abbreviation) + r'\b', full_term, text, flags=re.IGNORECASE)
        
        # 应用单位标准化
        if "unit_standardization" in self.knowledge_base:
            for old_unit, new_unit in self.knowledge_base["unit_standardization"].items():
                text = text.replace(old_unit, new_unit)
        
        # 应用乳腺癌术语标准化
        if "breast_cancer_terms" in self.knowledge_base:
            for old_term, new_term in self.knowledge_base["breast_cancer_terms"].items():
                text = text.replace(old_term, new_term)
        
        return text
    
    def standardize_terminology_with_llm(self, text: str) -> str:
        """
        使用LLM进行术语标准化
        
        Args:
            text: 原始文本
            
        Returns:
            标准化后的文本
        """
        # 构建完整的提示词，包含知识库内容
        knowledge_base_content = json.dumps(self.knowledge_base, ensure_ascii=False, indent=2)
        prompt = self.prompt_template.format(text=text, knowledge_base=knowledge_base_content)
        
        # 从prompt模板文件中读取system_prompt
        prompt_config = self._load_prompt_config()
        system_prompt = prompt_config.get("system_prompt", "")
        temperature = prompt_config.get("temperature", 0.1)
        max_tokens = prompt_config.get("max_tokens", 4000)
        
        # 调用LLM进行术语标准化
        standardized_text = self.llm_api.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return standardized_text.strip()
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        处理单个文本
        
        Args:
            text: 原始文本
            
        Returns:
            处理结果字典
        """
        # 先进行字典标准化
        dict_standardized = self.standardize_terminology_with_dict(text)
        
        # 使用LLM进行高级术语标准化
        llm_standardized = self.standardize_terminology_with_llm(dict_standardized)
        
        return {
            "original_text": text,
            "dict_standardized": dict_standardized,
            "cleaned_text": llm_standardized,
            "changes_made": {
                "dict_changes": text != dict_standardized,
                "llm_changes": dict_standardized != llm_standardized
            }
        }
    
    def batch_process(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量处理文本
        
        Args:
            texts: 文本列表
            
        Returns:
            处理结果列表
        """
        results = []
        
        for i, text in enumerate(texts):
            print(f"术语标准化第 {i+1}/{len(texts)} 条文本...")
            
            try:
                result = self.process_text(text)
                results.append(result)
            except Exception as e:
                print(f"处理第 {i+1} 条文本时出错: {e}")
                results.append({
                    "original_text": text,
                    "dict_standardized": text,
                    "cleaned_text": text,
                    "changes_made": {
                        "dict_changes": False,
                        "llm_changes": False
                    },
                    "error": str(e)
                })
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = "data/step4_results.json"):
        """保存处理结果"""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Step 4 结果已保存到: {output_path}")


 