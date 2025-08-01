"""
字段规则解析器模块。
用于解析字段定义、逻辑规则和关联字段关系。
"""

import json
from typing import Dict, List, Any, Optional

class FieldRuleParser:
    """字段规则解析器，用于解析乳腺癌字段定义和逻辑规则"""
    
    def __init__(self, rule_path: str):
        """
        初始化解析器
        
        Args:
            rule_path: 规则文件路径
        """
        with open(rule_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
    
    def get_field_defs(self) -> Dict[str, Any]:
        """获取所有字段定义"""
        return self.rules.get('fields', {})
    
    def get_logic_rules(self) -> List[Dict[str, Any]]:
        """获取逻辑规则列表"""
        return self.rules.get('logic', [])

    def get_linked_fields(self, field: str) -> List[str]:
        """获取与指定字段关联的字段列表"""
        return self.rules.get('links', {}).get(field, [])
    
    def get_field_options(self, field: str) -> List[str]:
        """获取指定字段的选项列表"""
        return self.rules.get('fields', {}).get(field, {}).get('options', [])
    
    def get_default(self, field: str) -> Optional[Any]:
        """获取指定字段的默认值"""
        return self.rules.get('fields', {}).get(field, {}).get('default', None)
    
    def get_field_type(self, field: str) -> str:
        """获取指定字段的类型"""
        return self.rules.get('fields', {}).get(field, {}).get('type', 'string')
    
    def get_field_range(self, field: str) -> Optional[Dict[str, Any]]:
        """获取指定字段的数值范围"""
        return self.rules.get('fields', {}).get(field, {}).get('range')
    
    def validate_field_value(self, field: str, value: Any) -> bool:
        """验证字段值是否符合规则"""
        field_def = self.rules.get('fields', {}).get(field, {})
        if not field_def:
            return False
        
        field_type = field_def.get('type', 'string')
        
        if field_type == 'string':
            options = field_def.get('options', [])
            if options and value not in options:
                return False
        elif field_type == 'number':
            try:
                num_value = float(value)
                range_def = field_def.get('range')
                if range_def:
                    min_val = range_def.get('min')
                    max_val = range_def.get('max')
                    if min_val is not None and num_value < min_val:
                        return False
                    if max_val is not None and num_value > max_val:
                        return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    def get_all_fields(self) -> List[str]:
        """获取所有字段名称列表"""
        return list(self.rules.get('fields', {}).keys())
    
    def get_required_fields(self) -> List[str]:
        """获取必填字段列表"""
        required = []
        for field, defs in self.rules.get('fields', {}).items():
            if defs.get('required', False):
                required.append(field)
        return required 