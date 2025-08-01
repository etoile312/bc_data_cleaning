#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签解析器
解析乳腺癌结构化标签文件，提取聚类所需的字段信息
"""

import json
from typing import Dict, List, Any
from pathlib import Path


class LabelParser:
    """标签解析器类"""
    
    def __init__(self, label_file_path: str):
        """
        初始化标签解析器
        
        Args:
            label_file_path: 标签文件路径
        """
        self.label_file_path = Path(label_file_path)
        self.labels = self._load_labels()
        self.category_fields = self._extract_category_fields()
    
    def _load_labels(self) -> Dict[str, Any]:
        """加载标签文件"""
        try:
            with open(self.label_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载标签文件失败: {e}")
            return {}
    
    def _extract_category_fields(self) -> Dict[str, List[str]]:
        """
        提取每个分类下的字段列表
        
        Returns:
            分类字段字典
        """
        category_fields = {}
        
        for category_name, category_data in self.labels.items():
            fields = []
            
            # 处理分类数据（可能是列表或字典）
            if isinstance(category_data, list):
                # 如果是列表，取第一个元素作为模板
                if category_data:
                    template = category_data[0]
                    if isinstance(template, dict):
                        fields = list(template.keys())
            elif isinstance(category_data, dict):
                fields = list(category_data.keys())
            
            category_fields[category_name] = fields
        
        return category_fields
    
    def get_category_fields(self, category_name: str) -> List[str]:
        """
        获取指定分类的字段列表
        
        Args:
            category_name: 分类名称
            
        Returns:
            字段列表
        """
        return self.category_fields.get(category_name, [])
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有分类名称
        
        Returns:
            分类名称列表
        """
        return list(self.labels.keys())
    
    def get_subcategory_field(self, category_name: str) -> str:
        """
        获取需要细分的分类字段名
        
        Args:
            category_name: 分类名称
            
        Returns:
            细分字段名
        """
        sub_categories = {
            "病理报告": "病理类型",
            "病情诊断与评估": "患者所处阶段"
        }
        return sub_categories.get(category_name, "")
    
    def get_subcategory_values(self, category_name: str) -> List[str]:
        """
        获取需要细分的分类字段值列表
        
        Args:
            category_name: 分类名称
            
        Returns:
            字段值列表
        """
        sub_category_values = {
            "病理报告": ["活检病理", "术后病理", "分子病理", "基因检测"],
            "病情诊断与评估": ["初诊", "新辅助治疗中", "复发确诊", "解救治疗中", "随访跟踪记录"]
        }
        return sub_category_values.get(category_name, [])
    
    def is_subcategory(self, category_name: str) -> bool:
        """
        判断是否为需要细分的分类
        
        Args:
            category_name: 分类名称
            
        Returns:
            是否为细分分类
        """
        return category_name in ["病理报告", "病情诊断与评估"]
    
    def print_category_info(self):
        """打印分类信息"""
        print("=== 标签分类信息 ===")
        for category_name, fields in self.category_fields.items():
            print(f"\n分类: {category_name}")
            print(f"字段数量: {len(fields)}")
            print(f"字段列表: {fields}")
            
            if self.is_subcategory(category_name):
                sub_field = self.get_subcategory_field(category_name)
                sub_values = self.get_subcategory_values(category_name)
                print(f"细分字段: {sub_field}")
                print(f"细分值: {sub_values}") 