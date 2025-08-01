#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗主控脚本
协调整个数据清洗流程
"""

import json
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any

# 导入各个步骤模块
from scripts.data_preparation import DataPreparation
from scripts.llm_api import LLMAPI
from scripts.step1_noise_removal import NoiseRemoval
from scripts.step2_format_fix import FormatFix

from scripts.step4_terminology_standardization import TerminologyStandardization
from scripts.step5_spelling_correction import SpellingCorrection



class DataCleaningPipeline:
    """数据清洗流水线"""
    
    def __init__(self, config_path: str = "config/config.yaml", max_docs: int = None):
        """
        初始化数据清洗流水线
        
        Args:
            config_path: 配置文件路径
            max_docs: 最大处理文档数量，None表示处理所有文档
        """
        self.config = self._load_config(config_path)
        self.max_docs = 10
        self.setup_logging()
        
        # 初始化LLM API
        self.llm_api = LLMAPI(config_path)
        
        # 初始化各个步骤
        self.data_preparation = DataPreparation()
        self.noise_removal = NoiseRemoval(self.llm_api)
        self.format_fix = FormatFix(self.llm_api)

        self.terminology_standardization = TerminologyStandardization(self.llm_api)
        self.spelling_correction = SpellingCorrection(self.llm_api)

        
        # 创建输出目录
        self.output_dir = Path(self.config.get('data', {}).get('output_dir', 'data'))
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建临时目录
        self.temp_dir = Path(self.config.get('data', {}).get('temp_dir', 'temp'))
        self.temp_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = log_config.get('file', 'logs/cleaning.log')
        
        # 创建日志目录
        Path(log_file).parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_data_preparation(self) -> List[str]:
        """运行数据准备步骤"""
        self.logger.info("=== 开始数据准备步骤 ===")
        
        try:
            cleaned_objects = self.data_preparation.run()
            
            # 如果设置了最大文档数量限制，则只取前N个
            if self.max_docs and len(cleaned_objects) > self.max_docs:
                cleaned_objects = cleaned_objects[:self.max_docs]
                self.logger.info(f"限制处理文档数量为 {self.max_docs} 个")
            
            self.logger.info(f"数据准备完成，共提取 {len(cleaned_objects)} 个清洗对象")
            return cleaned_objects
        except Exception as e:
            self.logger.error(f"数据准备步骤失败: {e}")
            return []
    
    def run_step1_noise_removal(self, texts: List[str]) -> List[Dict[str, Any]]:
        """运行Step 1 - 噪声剔除与段落切分"""
        self.logger.info("=== 开始Step 1 - 噪声剔除与段落切分 ===")
        
        if not self.config.get('pipeline', {}).get('steps', {}).get('step1_noise_removal', True):
            self.logger.info("Step 1 已禁用，跳过")
            return []
        
        try:
            results = self.noise_removal.batch_process(texts)
            # self.noise_removal.save_results(results)  # 禁止中间结果保存
            self.logger.info(f"Step 1 完成，处理了 {len(results)} 条文本")
            return results
        except Exception as e:
            self.logger.error(f"Step 1 失败: {e}")
            return []
    
    def run_step2_format_fix(self, texts: List[str]) -> List[Dict[str, Any]]:
        """运行Step 2 - 格式纠正"""
        self.logger.info("=== 开始Step 2 - 格式纠正 ===")
        
        if not self.config.get('pipeline', {}).get('steps', {}).get('step2_format_fix', True):
            self.logger.info("Step 2 已禁用，跳过")
            return []
        
        try:
            results = self.format_fix.batch_process(texts)
            # self.format_fix.save_results(results)  # 禁止中间结果保存
            self.logger.info(f"Step 2 完成，处理了 {len(results)} 条文本")
            return results
        except Exception as e:
            self.logger.error(f"Step 2 失败: {e}")
            return []
    

    
    def run_step4_terminology_standardization(self, texts: List[str]) -> List[Dict[str, Any]]:
        """运行Step 4 - 术语标准化"""
        self.logger.info("=== 开始Step 4 - 术语标准化 ===")
        
        if not self.config.get('pipeline', {}).get('steps', {}).get('step4_terminology_standardization', True):
            self.logger.info("Step 4 已禁用，跳过")
            return []
        
        try:
            results = self.terminology_standardization.batch_process(texts)
            # self.terminology_standardization.save_results(results)  # 禁止中间结果保存
            self.logger.info(f"Step 4 完成，处理了 {len(results)} 条文本")
            return results
        except Exception as e:
            self.logger.error(f"Step 4 失败: {e}")
            return []
    
    def run_step5_spelling_correction(self, texts: List[str]) -> List[Dict[str, Any]]:
        """运行Step 5 - 拼写与字符识别错误修复"""
        self.logger.info("=== 开始Step 5 - 拼写与字符识别错误修复 ===")
        
        if not self.config.get('pipeline', {}).get('steps', {}).get('step5_spelling_correction', True):
            self.logger.info("Step 5 已禁用，跳过")
            return []
        
        try:
            results = self.spelling_correction.batch_process(texts)
            # self.spelling_correction.save_results(results)  # 禁止中间结果保存
            self.logger.info(f"Step 5 完成，处理了 {len(results)} 条文本")
            return results
        except Exception as e:
            self.logger.error(f"Step 5 失败: {e}")
            return []
    

    
    def run_pipeline(self):
        """运行完整的数据清洗流水线 - 按文件依次处理"""
        self.logger.info("=== 开始数据清洗流水线 ===")
        try:
            # Step 0: 数据准备
            cleaned_objects = self.run_data_preparation()
            if not cleaned_objects:
                self.logger.error("数据准备失败，无法继续")
                return
            
            # 按文件依次处理
            all_final_results = []
            
            for i, original_text in enumerate(cleaned_objects):
                self.logger.info(f"=== 处理第 {i+1}/{len(cleaned_objects)} 个文件 ===")
                
                # Step 1: 噪声剔除与段落切分
                step1_result = self.run_step1_noise_removal([original_text])
                if not step1_result:
                    self.logger.error(f"Step 1 失败，跳过文件 {i+1}")
                    continue
                
                step1_cleaned_text = step1_result[0].get("cleaned_text", "")
                
                # Step 2: 格式纠正
                step2_result = self.run_step2_format_fix([step1_cleaned_text])
                if not step2_result:
                    self.logger.error(f"Step 2 失败，跳过文件 {i+1}")
                    continue
                
                step2_cleaned_text = step2_result[0].get("cleaned_text", "")
                
                # Step 4: 术语标准化
                step4_result = self.run_step4_terminology_standardization([step2_cleaned_text])
                if not step4_result:
                    self.logger.error(f"Step 4 失败，跳过文件 {i+1}")
                    continue
                
                step4_cleaned_text = step4_result[0].get("cleaned_text", "")
                
                # Step 5: 拼写与字符识别错误修复
                step5_result = self.run_step5_spelling_correction([step4_cleaned_text])
                if not step5_result:
                    self.logger.error(f"Step 5 失败，跳过文件 {i+1}")
                    continue
                
                step5_cleaned_text = step5_result[0].get("cleaned_text", "")
                
                # 保存单个文件的最终结果
                final_result = {
                    "original_text": original_text,
                    "cleaned_text": step5_cleaned_text
                }
                
                # 保存到对应的文件
                output_file = self.output_dir / f"cleaned_object_{i+1:03d}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(final_result, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"文件 {i+1} 处理完成，保存到: {output_file}")
                all_final_results.append(final_result)
            
            self.logger.info(f"=== 数据清洗流水线完成，共处理 {len(all_final_results)} 个文件 ===")
            
        except Exception as e:
            self.logger.error(f"数据清洗流水线失败: {e}")
    

    
    def run_single_step(self, step_name: str, input_data: Any = None):
        """运行单个步骤"""
        self.logger.info(f"=== 运行单个步骤: {step_name} ===")
        
        if step_name == "data_preparation":
            return self.run_data_preparation()
        
        elif step_name == "step1_noise_removal":
            if input_data is None:
                # 从文件加载数据
                data_file = self.output_dir / "cleaned_objects.json"
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        input_data = json.load(f)
                else:
                    self.logger.error("未找到输入数据文件")
                    return []
            
            return self.run_step1_noise_removal(input_data)
        
        elif step_name == "step2_format_fix":
            if input_data is None:
                # 从Step 1结果中提取清洗后的文本
                step1_file = self.output_dir / "step1_results.json"
                if step1_file.exists():
                    with open(step1_file, 'r', encoding='utf-8') as f:
                        step1_results = json.load(f)
                    input_data = [result.get("cleaned_text", "") for result in step1_results]
                else:
                    self.logger.error("未找到Step 1结果文件")
                    return []
            
            return self.run_step2_format_fix(input_data)
        

        
        elif step_name == "step4_terminology_standardization":
            if input_data is None:
                # 从Step 2结果中提取清洗后的文本
                step2_file = self.output_dir / "step2_results.json"
                if step2_file.exists():
                    with open(step2_file, 'r', encoding='utf-8') as f:
                        step2_results = json.load(f)
                    input_data = [result.get("cleaned_text", "") for result in step2_results]
                else:
                    self.logger.error("未找到Step 2结果文件")
                    return []
            
            return self.run_step4_terminology_standardization(input_data)
        
        elif step_name == "step5_spelling_correction":
            if input_data is None:
                # 从Step 4结果中提取清洗后的文本
                step4_file = self.output_dir / "step4_results.json"
                if step4_file.exists():
                    with open(step4_file, 'r', encoding='utf-8') as f:
                        step4_results = json.load(f)
                    input_data = [result.get("cleaned_text", "") for result in step4_results]
                else:
                    self.logger.error("未找到Step 4结果文件")
                    return []
            
            return self.run_step5_spelling_correction(input_data)
        

        
        else:
            self.logger.error(f"未知的步骤名称: {step_name}")
            return []


def main():
    """主函数"""
    import argparse
    import sys
    
    # 检查是否在Jupyter环境中运行
    if 'ipykernel' in sys.modules:
        print("检测到Jupyter环境，使用默认参数运行...")
        # 在Jupyter环境中直接运行完整流水线，可以设置max_docs=1来测试
        pipeline = DataCleaningPipeline(max_docs=1)  # 设置为1条进行测试
        pipeline.run_pipeline()
        return
    
    parser = argparse.ArgumentParser(description="数据清洗流水线")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--step", help="运行单个步骤")
    parser.add_argument("--input", help="单个步骤的输入数据文件")
    parser.add_argument("--list-steps", action="store_true", help="列出所有可用步骤")
    parser.add_argument("--max-docs", type=int, help="最大处理文档数量，用于测试时限制处理数量")
    
    args = parser.parse_args()
    
    # 列出所有可用步骤
    if args.list_steps:
        steps = [
            "data_preparation",
            "step1_noise_removal", 
            "step2_format_fix",
            "step4_terminology_standardization",
            "step5_spelling_correction"
        ]
        print("可用的步骤:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
        return
    
    # 创建流水线
    pipeline = DataCleaningPipeline(args.config, max_docs=args.max_docs)
    
    if args.step:
        # 运行单个步骤
        input_data = None
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        
        pipeline.run_single_step(args.step, input_data)
    else:
        # 运行完整流水线
        pipeline.run_pipeline()


if __name__ == "__main__":
    main() 