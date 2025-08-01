#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2: 噪声剔除与段落切分
删除与病历无关的信息，如医院地址、签名、页码、行政字段等，同时将正文内容按段落清晰切分
"""

import json
import re
from typing import List, Dict, Any
from pathlib import Path
from .llm_api import LLMAPI


class NoiseRemoval:
    """噪声剔除与段落切分类"""
    
    def __init__(self, llm_api: LLMAPI):
        """
        初始化噪声剔除器
        
        Args:
            llm_api: LLM API实例
        """
        self.llm_api = llm_api
        self.knowledge_base = self._load_knowledge_base()
        self.prompt_template = self._load_prompt_template()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """从知识库文件中加载数据"""
        knowledge_base_ref = "step2_noise_fields"
        # 使用相对于项目根目录的路径
        project_root = Path(__file__).parent.parent
        knowledge_file = project_root / f"knowledge_base/{knowledge_base_ref}.json"
        
        if knowledge_file.exists():
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"警告: 知识库文件 {knowledge_file} 不存在")
            return {}
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        # 使用相对于项目根目录的路径
        project_root = Path(__file__).parent.parent
        prompt_file = project_root / "prompts/step2_noise_removal.json"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("prompt", "")
        else:
            return ""
    
    def _load_prompt_config(self) -> Dict[str, Any]:
        """加载完整的提示词配置"""
        project_root = Path(__file__).parent.parent
        prompt_file = project_root / "prompts/step2_noise_removal.json"
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_config = json.load(f)
            return prompt_config
        except Exception as e:
            print(f"加载提示词配置失败: {e}")
            return {}
    
    def remove_noise(self, text: str) -> str:
        """
        去除噪声信息
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 格式化知识库内容
        knowledge_base_str = self._format_knowledge_base()
        
        # 构建完整的提示词（组合知识库和提示词模板）
        prompt = self.prompt_template.format(
            text=text,
            knowledge_base=knowledge_base_str
        )
        
        # 从prompt模板文件中读取system_prompt
        prompt_config = self._load_prompt_config()
        system_prompt = prompt_config.get("system_prompt", "")
        temperature = prompt_config.get("temperature", 0.1)
        max_tokens = prompt_config.get("max_tokens", 4000)
        
        # 调用LLM进行清洗
        cleaned_text = self.llm_api.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return cleaned_text.strip()
    
    def _format_knowledge_base(self) -> str:
        """格式化知识库内容为字符串"""
        if not self.knowledge_base:
            return ""
        
        formatted_kb = []
        for category, items in self.knowledge_base.items():
            if isinstance(items, list):
                formatted_kb.append(f"{category}: {', '.join(items)}")
            elif isinstance(items, dict):
                formatted_kb.append(f"{category}:")
                for key, value in items.items():
                    if isinstance(value, list):
                        formatted_kb.append(f"  {key}: {', '.join(value)}")
                    else:
                        formatted_kb.append(f"  {key}: {value}")
            else:
                formatted_kb.append(f"{category}: {items}")
        
        return "\n".join(formatted_kb)
    
    def split_paragraphs(self, text: str) -> List[str]:
        """
        将文本按段落切分
        
        Args:
            text: 清洗后的文本
            
        Returns:
            段落列表
        """
        # 使用多种分隔符进行段落切分
        paragraph_separators = [
            r'\n\s*\n',  # 空行
            r'\n(?=[A-Z\u4e00-\u9fff])',  # 换行后跟大写字母或中文
            r'。\s*\n',  # 句号后换行
            r'；\s*\n',  # 分号后换行
        ]
        
        paragraphs = [text]
        
        for separator in paragraph_separators:
            new_paragraphs = []
            for para in paragraphs:
                if separator in para:
                    split_paras = re.split(separator, para)
                    new_paragraphs.extend([p.strip() for p in split_paras if p.strip()])
                else:
                    new_paragraphs.append(para)
            paragraphs = new_paragraphs
        
        # 过滤掉过短的段落
        paragraphs = [p for p in paragraphs if len(p.strip()) > 10]
        
        return paragraphs
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        处理单个文本
        
        Args:
            text: 原始文本
            
        Returns:
            处理结果字典
        """
        # 去除噪声
        cleaned_text = self.remove_noise(text)
        
        # 段落切分
        paragraphs = self.split_paragraphs(cleaned_text)
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "paragraphs": paragraphs,
            "paragraph_count": len(paragraphs)
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
            print(f"处理第 {i+1}/{len(texts)} 条文本...")
            
            try:
                result = self.process_text(text)
                results.append(result)
            except Exception as e:
                print(f"处理第 {i+1} 条文本时出错: {e}")
                results.append({
                    "original_text": text,
                    "cleaned_text": text,
                    "paragraphs": [text],
                    "paragraph_count": 1,
                    "error": str(e)
                })
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = "data/step1_results.json"):
        """保存处理结果"""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Step 1 结果已保存到: {output_path}")


 