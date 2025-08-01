"""
带噪声文本生成入口脚本。
批量处理临床风格文本，注入各种类型的噪声。
"""

import json
import os
import random  # 顶部统一导入
from typing import Dict, List, Any

from .noise_injector import NoiseInjector

class NoisyTextGenerator:
    """带噪声文本生成器"""
    
    def __init__(self, 
                 input_file: str = 'data/generated_cases/all_cases.json',
                 output_dir: str = 'data/generated_cases'):
        """
        初始化生成器
        
        Args:
            input_file: 输入的临床风格文本文件
            output_dir: 输出目录
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.injector = NoiseInjector()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def load_cases(self) -> List[Dict[str, Any]]:
        """加载临床风格文本数据"""
        try:
            with open(self.input_file, encoding='utf-8') as f:
                cases = json.load(f)
            print(f"✅ 成功加载 {len(cases)} 个临床风格文本")
            return cases
        except FileNotFoundError:
            print(f"❌ 错误：{self.input_file} 文件不存在，请先运行临床风格文本生成")
            return []
        except Exception as e:
            print(f"❌ 错误：读取文件失败 - {e}")
            return []
    
    def process_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量处理病例，注入噪声"""
        results = []
        print(f"开始处理 {len(cases)} 个病例...")
        for idx, case in enumerate(cases):
            print(f"处理第 {idx+1}/{len(cases)} 个病例...")
            text = case.get('text', '')
            if not text:
                print(f"警告：第 {idx+1} 个病例没有文本内容")
                results.append(case)  # 保证输出数量一致
                continue
            noisy_text = self.injector.inject_noise(text, case.get('structured', {}))
            case['noisy_text'] = noisy_text
            results.append(case)
            # 写入 JSON 文件
            json_file = os.path.join(self.output_dir, f"case_{idx+1:03d}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(case, f, ensure_ascii=False, indent=2)
            # 写入带噪声的 TXT 文件
            txt_file = os.path.join(self.output_dir, f"case_{idx+1:03d}_noisy.txt")
            with open(txt_file, "w", encoding="utf-8") as ftxt:
                ftxt.write(case.get('noisy_text', ''))
            print(f"已生成: {json_file}")
        return results
    
    def save_combined_results(self, results: List[Dict[str, Any]]) -> None:
        """保存合并结果"""
        combined_file = os.path.join(self.output_dir, 'all_cases_with_noise.json')
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存合并结果到: {combined_file}")
    
    def generate_noise_samples(self, num_samples: int = 10) -> List[Dict[str, Any]]:
        """生成噪声样本用于测试"""
        print(f"生成 {num_samples} 个噪声样本...")
        sample_texts = [
            "患者王**，女，56岁，已绝经。2025年6月10日行左乳癌改良根治术，术后病理：浸润性导管癌（1.8cm），Ⅱ级，腋窝淋巴结转移（4/18），脉管侵犯（+），切缘阴性。",
            "张某，女，48岁，左乳癌术后3年，胸壁复发1年。既往史：胸壁复发时行THP方案治疗6周期达CR，停药8个月后再次出现肺转移。",
            "女，45岁，未绝经。左乳癌术后6年。2018年行左乳癌保乳术（pT1cN0M0, ⅠA期），ER(80%+)/PR(30%+)/HER-2(-)。"
        ]
        results = []
        for i in range(num_samples):
            text = random.choice(sample_texts)
            noisy_text = self.injector.inject_noise(text)
            result = {
                "original_text": text,
                "noisy_text": noisy_text,
                "sample_id": i + 1
            }
            results.append(result)
            sample_file = os.path.join(self.output_dir, f"noise_sample_{i+1:03d}.json")
            with open(sample_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        return results
    
    def run(self, generate_samples: bool = False) -> List[Dict[str, Any]]:
        """运行完整的噪声注入流程"""
        print("🚀 开始带噪声文本生成...")
        if generate_samples:
            return self.generate_noise_samples()
        cases = self.load_cases()
        if not cases:
            return []
        results = self.process_cases(cases)
        self.save_combined_results(results)
        print("🎉 带噪声文本生成完成！")
        return results

def main():
    """主函数"""
    generator = NoisyTextGenerator()
    results = generator.run()
    if results:
        print(f"\n📈 生成统计:")
        print(f"   - 处理病例数: {len(results)}")
        print(f"   - 输出目录: {generator.output_dir}")
        print(f"   - 文件格式: JSON + TXT (带噪声)")
        print(f"\n🧪 生成噪声样本...")
        samples = generator.generate_noise_samples(5)
        print(f"   - 噪声样本数: {len(samples)}")

if __name__ == "__main__":
    main() 