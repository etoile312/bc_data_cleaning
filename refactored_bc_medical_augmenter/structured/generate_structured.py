"""
结构化数据生成主入口脚本。
整合字段解析、采样、组合等模块，生成完整的结构化病例数据。
"""

import json
import os
from typing import Dict, List, Any

from .field_parser import FieldRuleParser
from .field_sampler import FieldSampler
from .combine_segments import SegmentCombiner
from .segment_groups import SEGMENT_GROUPS

class StructuredDataGenerator:
    """结构化数据生成器"""
    
    def __init__(self, 
                 rules_path: str = 'rules/breast_cancer_rules.json',
                 segment_dir: str = 'data/segments',
                 output_dir: str = 'data'):
        """
        初始化生成器
        
        Args:
            rules_path: 规则文件路径
            segment_dir: 段落数据目录
            output_dir: 输出目录
        """
        self.rules_path = rules_path
        self.segment_dir = segment_dir
        self.output_dir = output_dir
        
        # 初始化各个模块
        self.parser = FieldRuleParser(rules_path)
        self.sampler = FieldSampler(
            self.parser.get_field_defs(),
            self.parser.get_logic_rules()
        )
        self.combiner = SegmentCombiner(segment_dir, rules_path)
    
    def generate_segment_pools(self, samples_per_group: int = 100) -> Dict[str, List[Dict[str, str]]]:
        """生成各字段组的样本池"""
        pools = {}
        
        for group_name, fields in SEGMENT_GROUPS.items():
            print(f"生成 {group_name} 字段组样本池...")
            samples = self.sampler.sample_segment(fields, samples_per_group, group_name)
            pools[group_name] = samples
            
            # 保存到文件
            output_file = os.path.join(self.segment_dir, f'{group_name}_pool.json')
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(samples, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(samples)} 个 {group_name} 样本到 {output_file}")
        
        return pools
    
    def generate_combined_cases(self, n_cases: int = 100) -> List[Dict[str, Any]]:
        """生成组合病例"""
        print(f"生成 {n_cases} 个组合病例...")
        cases = self.combiner.generate_cases(n_cases, os.path.join(self.output_dir, 'combined_cases.json'))
        return cases
    
    def validate_generated_data(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证生成的数据质量"""
        validation_results = {
            'total_cases': len(cases),
            'field_coverage': {},
            'logic_violations': [],
            'empty_fields': {}
        }
        
        # 统计字段覆盖率
        all_fields = self.parser.get_all_fields()
        field_counts = {field: 0 for field in all_fields}
        
        for case in cases:
            for field in all_fields:
                if field in case and case[field]:
                    field_counts[field] += 1
        
        validation_results['field_coverage'] = {
            field: count / len(cases) 
            for field, count in field_counts.items()
        }
        
        # 检查空字段
        for field, coverage in validation_results['field_coverage'].items():
            if coverage < 0.1:  # 覆盖率低于10%
                validation_results['empty_fields'][field] = coverage
        
        print(f"✅ 数据验证完成:")
        print(f"   - 总病例数: {validation_results['total_cases']}")
        print(f"   - 字段覆盖率: {len([f for f, c in validation_results['field_coverage'].items() if c > 0.5])}/{len(all_fields)}")
        print(f"   - 空字段数: {len(validation_results['empty_fields'])}")
        
        return validation_results
    
    def run_full_pipeline(self, 
                         samples_per_group: int = 100, 
                         n_cases: int = 100,
                         validate: bool = True) -> Dict[str, Any]:
        """运行完整的数据生成流水线"""
        print("🚀 开始结构化数据生成流水线...")
        
        # 1. 生成字段组样本池
        print("\n📊 步骤1: 生成字段组样本池")
        pools = self.generate_segment_pools(samples_per_group)
        
        # 2. 生成组合病例
        print("\n🔗 步骤2: 生成组合病例")
        cases = self.generate_combined_cases(n_cases)
        
        # 3. 数据验证
        if validate:
            print("\n✅ 步骤3: 数据验证")
            validation_results = self.validate_generated_data(cases)
        else:
            validation_results = {}
        
        print("\n🎉 结构化数据生成完成！")
        
        return {
            'pools': pools,
            'cases': cases,
            'validation': validation_results
        }

def main():
    """主函数"""
    generator = StructuredDataGenerator()
    results = generator.run_full_pipeline(
        samples_per_group=100,
        n_cases=100,
        validate=True
    )
    
    print(f"\n📈 生成统计:")
    print(f"   - 字段组样本池: {len(results['pools'])} 个")
    print(f"   - 组合病例: {len(results['cases'])} 个")
    print(f"   - 输出文件: data/combined_cases.json")

if __name__ == "__main__":
    main() 