"""
噪声注入主逻辑模块。
负责加载配置、选择噪声类型、应用噪声到文本中。
"""

import json
import random
import re
import string
from typing import Dict, Any, List, Optional, Tuple

from .noise_types import NOISE_TYPE_MAP, extract_main_info

class NoiseInjector:
    """噪声注入器，负责向文本中注入各种类型的噪声"""
    
    def __init__(self, config_path: str = 'config/noise_config.json'):
        """
        初始化噪声注入器
        
        Args:
            config_path: 噪声配置文件路径
        """
        self.config = self.load_noise_config(config_path)
        self.ocr_errors = {
            "0": ["O", "o", "D"],
            "1": ["l", "I", "i"],
            "2": ["Z", "z"],
            "3": ["8", "B"],
            "4": ["A", "a"],
            "5": ["S", "s"],
            "6": ["G", "g"],
            "7": ["T", "t"],
            "8": ["B", "b"],
            "9": ["g", "q"],
            "O": ["0", "o"],
            "l": ["1", "I"],
            "I": ["1", "l"],
            "S": ["5", "s"],
            "Z": ["2", "z"],
            "G": ["6", "g"],
            "B": ["8", "b"],
            "T": ["7", "t"]
        }
    
    def load_noise_config(self, config_path: str) -> Dict[str, Any]:
        """加载噪声配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告：未找到噪声配置文件 {config_path}，使用默认配置")
            return self.get_default_config()
        except Exception as e:
            print(f"警告：加载噪声配置失败 - {e}，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认噪声配置"""
        return {
            "noise_types": {
                "administrative": {"prob": 0.2, "length": [50, 100]},
                "hospital_info": {"prob": 0.1, "length": [30, 80]},
                "examination": {"prob": 0.1, "length": [50, 200]},
                "electronic_trace": {"prob": 0.1, "length": [50, 100]},
                "address": {"prob": 0.1, "length": [50, 100]},
                "duplicate": {"prob": 0.1, "length": [50, 100]},
                "covid_test": {"prob": 0.05, "length": [30, 80]},
                "table_header": {"prob": 0.1, "length": [30, 80]},
                "table_row_merge": {"prob": 0.1, "length": [50, 120]},
                "detailed_lab_result": {"prob": 0.1, "length": [100, 300]},
                "serial_merge": {"prob": 0.1, "length": [80, 200]},
                "doctor_advice": {"prob": 0.1, "length": [30, 80]},
                "remove_space": {"prob": 0.2},
                "computer_menu": {"prob": 0.1, "length": [30, 80]}
            },
            "injection_stages": {
                "content_level": {"prob": 0.7, "num_noise": [1, 3]},
                "ocr_level": {"prob": 0.3, "char_error_rate": 0.02}
            }
        }
    
    def select_noise_types(self) -> List[str]:
        """根据配置选择噪声类型"""
        noise_types = list(self.config['noise_types'].keys())
        noise_probs = [self.config['noise_types'][nt]['prob'] for nt in noise_types]
        
        # 选择1-3个噪声类型
        num_noise = random.randint(1, 3)
        chosen_types = random.choices(noise_types, weights=noise_probs, k=num_noise)
        
        return list(set(chosen_types))  # 去重
    
    def inject_content_level_noise(self, text: str, main_info: Optional[Tuple[str, str]] = None) -> str:
        """注入内容级噪声"""
        if random.random() > self.config['injection_stages']['content_level']['prob']:
            return text
        
        chosen_types = self.select_noise_types()
        noisy_text = text
        
        for noise_type in chosen_types:
            if noise_type == 'remove_space':
                # 删除空格噪声直接应用到原文本
                noisy_text = NOISE_TYPE_MAP[noise_type](noisy_text)
            else:
                # 其他噪声类型生成新内容并追加
                noise_content = NOISE_TYPE_MAP[noise_type](noisy_text, main_info=main_info)
                if noise_content:
                    noisy_text += '\n' + noise_content
        
        return noisy_text
    
    def inject_ocr_level_noise(self, text: str) -> str:
        """注入OCR级噪声"""
        if random.random() > self.config['injection_stages']['ocr_level']['prob']:
            return text
        
        char_error_rate = self.config['injection_stages']['ocr_level']['char_error_rate']
        chars = list(text)
        
        for i, char in enumerate(chars):
            if random.random() < char_error_rate and char in self.ocr_errors:
                # 随机替换为OCR错误字符
                chars[i] = random.choice(self.ocr_errors[char])
        
        return ''.join(chars)
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的换行符
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 移除行首行尾空白
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
        return text
    
    def inject_noise(self, text: str, case_data: Optional[Dict[str, Any]] = None) -> str:
        """
        向文本中注入噪声
        
        Args:
            text: 原始文本
            case_data: 病例数据，用于提取主要信息
            
        Returns:
            注入噪声后的文本
        """
        # 提取主要信息
        main_info = None
        if case_data:
            main_info = extract_main_info(case_data)
        
        # 第一阶段：内容级噪声注入
        noisy_text = self.inject_content_level_noise(text, main_info)
        
        # 第二阶段：OCR级噪声注入
        noisy_text = self.inject_ocr_level_noise(noisy_text)
        
        # 清理文本
        noisy_text = self.clean_text(noisy_text)
        
        return noisy_text
    
    def batch_inject_noise(self, texts: List[str], case_data_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        批量注入噪声
        
        Args:
            texts: 原始文本列表
            case_data_list: 病例数据列表
            
        Returns:
            注入噪声后的文本列表
        """
        results = []
        
        for i, text in enumerate(texts):
            case_data = case_data_list[i] if case_data_list and i < len(case_data_list) else None
            noisy_text = self.inject_noise(text, case_data)
            results.append(noisy_text)
        
        return results

def load_noise_config(path: str = 'config/noise_config.json') -> Dict[str, Any]:
    """加载噪声配置的便捷函数"""
    injector = NoiseInjector(path)
    return injector.config

def inject_noise(text: str, main_info: Optional[Tuple[str, str]] = None, config: Optional[Dict[str, Any]] = None) -> str:
    """
    注入噪声的便捷函数
    
    Args:
        text: 原始文本
        main_info: 主要信息 (姓名, 年龄)
        config: 噪声配置
        
    Returns:
        注入噪声后的文本
    """
    injector = NoiseInjector()
    if config:
        injector.config = config
    
    case_data = None
    if main_info:
        case_data = {"name": main_info[0], "age": main_info[1]}
    
    return injector.inject_noise(text, case_data) 