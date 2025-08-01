#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API模块
用于与大模型进行交互
"""

import os
import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path

# Optional import for requests
try:
    import requests
except ImportError:
    print("警告: requests 包未安装，HTTP API 功能将不可用")
    print("请运行: pip install requests")
    requests = None


class LLMAPI:
    """LLM API类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化LLM API
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.model_config = self.config['model']
        self.default_model = self.model_config['default_model']
        
        # 初始化API客户端
        self._init_clients()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def _init_clients(self):
        """初始化API客户端"""
        # 简化初始化，只保留必要的设置
        pass
    
    def call_llm(self, 
                 prompt: str, 
                 model: Optional[str] = None,
                 system_prompt: str = "",
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> str:
        """
        调用LLM API
        
        Args:
            prompt: 用户提示词
            model: 模型名称
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            LLM响应内容
        """
        model = model or self.default_model
        
        try:
            if model.startswith('local'):
                return self._call_local_model(prompt, model)
            elif model.startswith('qwen'):
                return self._call_qwen_model(prompt, model)
            else:
                raise ValueError(f"不支持的模型类型: {model}")
                
        except Exception as e:
            print(f"调用LLM API失败: {e}")
            return ""
    

    
    def batch_call(self, 
                   prompts: List[str], 
                   model: Optional[str] = None,
                   system_prompt: str = "",
                   batch_size: int = 5) -> List[str]:
        """
        批量调用LLM API
        
        Args:
            prompts: 提示词列表
            model: 模型名称
            system_prompt: 系统提示词
            batch_size: 批处理大小
            
        Returns:
            响应列表
        """
        results = []
        
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            batch_results = []
            
            for prompt in batch:
                result = self.call_llm(prompt, model, system_prompt)
                batch_results.append(result)
            
            results.extend(batch_results)
            print(f"已处理 {min(i + batch_size, len(prompts))}/{len(prompts)} 条数据")
        
        return results
    
    def _call_local_model(self, prompt: str, model: str) -> str:
        """调用本地模型API"""
        if requests is None:
            print("requests模块未安装，无法调用本地模型")
            return ""
            
        try:
            url_local_model = "http://192.168.19.211:8000/v1/model/single_report"
            response = requests.post(url_local_model, json={"report": prompt})
            
            if response.status_code == 200:
                res = response.json()
                return res.get("llm_ret", "")
            else:
                print(f"本地模型API调用失败: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"本地模型API调用异常: {e}")
            return ""
    
    def _call_qwen_model(self, prompt: str, model: str) -> str:
        """调用Qwen模型API"""
        if requests is None:
            print("requests模块未安装，无法调用Qwen模型")
            return ""
            
        try:
            response = requests.post(
                "http://qwen3.aistarfish.net/v1/model/single_report",
                headers={
                    "accept": "application/json",
                    "Authorization": "Bearer haixin_csco1435tG8y98hTa717",
                    "Content-Type": "application/json",
                },
                json={"report": prompt},
                timeout=30,
            )
            
            if response.status_code == 200:
                res = response.json()
                return res.get("llm_ret", "")
            else:
                print(f"Qwen模型API调用失败: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Qwen模型API调用异常: {e}")
            return ""
    



if __name__ == "__main__":
    # 测试LLM API
    llm = LLMAPI()
    
    # 测试调用
    test_prompt = "请简单介绍一下乳腺癌的基本信息"
    response = llm.call_llm(test_prompt)
    print(f"测试响应: {response}") 