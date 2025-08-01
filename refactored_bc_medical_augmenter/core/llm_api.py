"""
LLM API调用模块。
集中管理大模型API调用，提供统一的接口。
"""

import json
import requests
from typing import Dict, Any, Optional

def load_api_config(path: str = 'config/model_api.json') -> Dict[str, Any]:
    """加载API配置"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"警告：未找到API配置文件 {path}，使用默认配置")
        return get_default_api_config()
    except Exception as e:
        print(f"警告：加载API配置失败 - {e}，使用默认配置")
        return get_default_api_config()

def get_default_api_config() -> Dict[str, Any]:
    """获取默认API配置"""
    return {
        "url": "http://192.168.19.211:8000/v1/model/single_report",
        "timeout": 10,
        "headers": {
            "Content-Type": "application/json"
        }
    }

def call_llm(prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    调用大模型API
    
    Args:
        prompt: 提示词
        config: API配置
        
    Returns:
        模型返回的文本
    """
    if config is None:
        config = load_api_config()
    
    url = config['url']
    timeout = config.get('timeout', 10)
    headers = config.get('headers', {"Content-Type": "application/json"})
    
    try:
        response = requests.post(
            url, 
            json={'report': prompt}, 
            timeout=timeout,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        text = result.get('llm_ret', '')
        
        if text:
            # 清理文本
            text = text.replace("**", "").strip()
        
        return text
        
    except requests.exceptions.Timeout:
        print("警告：API调用超时")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"警告：API调用失败 - {e}")
        return ""
    except Exception as e:
        print(f"警告：处理API响应失败 - {e}")
        return ""

def call_llm_with_retry(prompt: str, max_retries: int = 3, config: Optional[Dict[str, Any]] = None) -> str:
    """
    带重试的LLM API调用
    
    Args:
        prompt: 提示词
        max_retries: 最大重试次数
        config: API配置
        
    Returns:
        模型返回的文本
    """
    for attempt in range(max_retries):
        try:
            result = call_llm(prompt, config)
            if result:
                return result
        except Exception as e:
            print(f"第 {attempt + 1} 次调用失败: {e}")
            if attempt == max_retries - 1:
                print("所有重试都失败了")
                return ""
    
    return ""

def batch_call_llm(prompts: list, config: Optional[Dict[str, Any]] = None) -> list:
    """
    批量调用LLM API
    
    Args:
        prompts: 提示词列表
        config: API配置
        
    Returns:
        模型返回的文本列表
    """
    results = []
    
    for i, prompt in enumerate(prompts):
        print(f"调用LLM API ({i+1}/{len(prompts)})...")
        result = call_llm(prompt, config)
        results.append(result)
    
    return results

# 兼容性函数
def ask_model(query: str) -> str:
    """兼容原有函数名"""
    return call_llm(query) 