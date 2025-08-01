"""
临床风格文本生成入口脚本。
批量处理结构化病例数据，生成临床风格文本。
"""

import json
import os
from typing import Dict, List, Any

from .text_generator import process_single_case

class ClinicalTextGenerator:
    """临床文本生成器"""
    
    def __init__(self, 
                 input_file: str = 'data/combined_cases.json',
                 output_dir: str = 'data/generated_cases'):
        """
        初始化生成器
        
        Args:
            input_file: 输入的结构化病例文件
            output_dir: 输出目录
        """
        self.input_file = input_file
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def load_cases(self) -> List[Dict[str, Any]]:
        """加载结构化病例数据"""
        try:
            with open(self.input_file, encoding='utf-8') as f:
                cases = json.load(f)
            print(f"✅ 成功加载 {len(cases)} 个结构化病例")
            return cases
        except FileNotFoundError:
            print(f"❌ 错误：{self.input_file} 文件不存在，请先运行结构化数据生成")
            return []
        except Exception as e:
            print(f"❌ 错误：读取文件失败 - {e}")
            return []
    
    def process_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量处理病例"""
        results = []
        
        print(f"开始处理 {len(cases)} 个病例...")
        
        for idx, case in enumerate(cases):
            print(f"处理第 {idx+1}/{len(cases)} 个病例...")
            
            # 处理单个病例
            result = process_single_case(case, idx+1)
            results.append(result)
            
            # 写入 JSON 文件
            json_file = os.path.join(self.output_dir, f"case_{idx+1:03d}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # 写入 TXT 文件
            txt_file = os.path.join(self.output_dir, f"case_{idx+1:03d}.txt")
            with open(txt_file, "w", encoding="utf-8") as ftxt:
                ftxt.write(result["text"])

            print(f"已生成: {json_file}")
        
        return results
    
    def save_combined_results(self, results: List[Dict[str, Any]]) -> None:
        """保存合并结果"""
        combined_file = os.path.join(self.output_dir, 'all_cases.json')
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存合并结果到: {combined_file}")
    
    def run(self) -> List[Dict[str, Any]]:
        """运行完整的生成流程"""
        print("🚀 开始临床风格文本生成...")
        
        # 1. 加载病例数据
        cases = self.load_cases()
        if not cases:
            return []
        
        # 2. 批量处理
        results = self.process_cases(cases)
        
        # 3. 保存合并结果
        self.save_combined_results(results)
        
        print("🎉 临床风格文本生成完成！")
        return results

def main():
    """主函数"""
    generator = ClinicalTextGenerator()
    results = generator.run()
    
    if results:
        print(f"\n📈 生成统计:")
        print(f"   - 处理病例数: {len(results)}")
        print(f"   - 输出目录: {generator.output_dir}")
        print(f"   - 文件格式: JSON + TXT")

if __name__ == "__main__":
    main() 