#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 1: 格式纠正与拼写修复
修复OCR导致的换行错误、标点混乱、字符错位等问题，并进行拼写与字符识别错误修复
"""

import json
import re
from typing import List, Dict, Any
from pathlib import Path
from .llm_api import LLMAPI


class FormatFix:
    """格式纠正与拼写修复类"""
    
    def __init__(self, llm_api: LLMAPI):
        """
        初始化格式纠正与拼写修复器
        
        Args:
            llm_api: LLM API实例
        """
        self.llm_api = llm_api
        self.knowledge_base = self._load_knowledge_base()
        self.prompt_template = self._load_prompt_template()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """加载知识库"""
        knowledge_file = Path("knowledge_base/step1_ocr_errors.json")
        
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
                "common_ocr_errors": {
                    "10^9": "109",
                    "10^12": "1012",
                    "10^6": "106",
                    "l0": "10",
                    "O": "0",
                    "l": "1",
                    "S": "5",
                    "B": "8",
                    "G": "6",
                    "Z": "2"
                },
                "punctuation_fixes": {
                    "，": ",",
                    "。": ".",
                    "；": ";",
                    "：": ":",
                    "？": "?",
                    "！": "!"
                },
                "line_break_patterns": [
                    r"(\w+)\n(\w+)",  # 单词间的不当换行
                    r"(\d+)\n(\w+)",  # 数字后的不当换行
                    r"(\w+)\n(\d+)",  # 单词后的数字换行
                ]
            }
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        prompt_file = Path("prompts/step1_format_fix.json")
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("prompt", "")
        else:
            return ""
    
    def _load_prompt_config(self) -> Dict[str, Any]:
        """加载完整的提示词配置"""
        prompt_file = Path("prompts/step1_format_fix.json")
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_config = json.load(f)
            return prompt_config
        except Exception as e:
            print(f"加载提示词配置失败: {e}")
            return {}
    
    def fix_common_ocr_errors(self, text: str) -> str:
        """
        修复常见OCR错误和拼写错误
        
        Args:
            text: 原始文本
            
        Returns:
            修复后的文本
        """
        # 检查知识库是否正确加载
        if self.knowledge_base is None:
            print("警告：知识库未正确加载，跳过OCR错误修复")
            return text
        
        # 应用OCR错误映射
        if "common_ocr_errors" in self.knowledge_base:
            for error, correction in self.knowledge_base["common_ocr_errors"].items():
                text = text.replace(error, correction)
        
        # 修复标点符号
        if "punctuation_fixes" in self.knowledge_base:
            for chinese_punct, english_punct in self.knowledge_base["punctuation_fixes"].items():
                text = text.replace(chinese_punct, english_punct)
        
        # 修复医学术语拼写错误
        if "medical_spelling_fixes" in self.knowledge_base:
            for error, correction in self.knowledge_base["medical_spelling_fixes"].items():
                text = text.replace(error, correction)
        
        return text
    
    def fix_line_breaks(self, text: str) -> str:
        """
        修复不当换行
        
        Args:
            text: 原始文本
            
        Returns:
            修复后的文本
        """
        # 修复单词间的不当换行
        text = re.sub(r"(\w+)\n(\w+)", r"\1\2", text)
        
        # 修复数字后的不当换行
        text = re.sub(r"(\d+)\n(\w+)", r"\1\2", text)
        
        # 修复单词后的数字换行
        text = re.sub(r"(\w+)\n(\d+)", r"\1\2", text)
        
        return text
    
    def fix_format_with_llm(self, text: str) -> str:
        """
        使用LLM进行格式修复
        
        Args:
            text: 原始文本
            
        Returns:
            修复后的文本
        """
        # 构建完整的提示词，包含知识库内容
        knowledge_base_content = json.dumps(self.knowledge_base, ensure_ascii=False, indent=2)
        prompt = self.prompt_template.format(text=text, knowledge_base=knowledge_base_content)
        
        # 从prompt模板文件中读取system_prompt
        prompt_config = self._load_prompt_config()
        system_prompt = prompt_config.get("system_prompt", "")
        temperature = prompt_config.get("temperature", 0.1)
        max_tokens = prompt_config.get("max_tokens", 4000)
        
        # 调用LLM进行格式修复
        fixed_text = self.llm_api.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return fixed_text.strip()
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        处理单个文本
        
        Args:
            text: 原始文本
            
        Returns:
            处理结果字典
        """
        # 先进行基础OCR错误和拼写修复
        basic_fixed = self.fix_common_ocr_errors(text)
        
        # 修复不当换行
        line_fixed = self.fix_line_breaks(basic_fixed)
        
        # 使用LLM进行高级格式和拼写修复
        llm_fixed = self.fix_format_with_llm(line_fixed)
        
        return {
            "original_text": text,
            "basic_fixed": basic_fixed,
            "line_fixed": line_fixed,
            "cleaned_text": llm_fixed,
            "changes_made": {
                "ocr_errors_fixed": text != basic_fixed,
                "line_breaks_fixed": basic_fixed != line_fixed,
                "llm_format_fixed": line_fixed != llm_fixed
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
            print(f"格式修复与拼写纠错第 {i+1}/{len(texts)} 条文本...")
            
            try:
                result = self.process_text(text)
                results.append(result)
            except Exception as e:
                print(f"处理第 {i+1} 条文本时出错: {e}")
                results.append({
                    "original_text": text,
                    "basic_fixed": text,
                    "line_fixed": text,
                    "cleaned_text": text,
                    "changes_made": {
                        "ocr_errors_fixed": False,
                        "line_breaks_fixed": False,
                        "llm_format_fixed": False
                    },
                    "error": str(e)
                })
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = "data/step2_results.json"):
        """保存处理结果"""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Step 2 结果已保存到: {output_path}")


 