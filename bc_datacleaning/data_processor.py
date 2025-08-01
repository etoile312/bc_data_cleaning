#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理脚本
从data文件夹读取数据，进行清洗处理，并保存结果
"""

import json
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any

# 导入各个步骤模块
from scripts.llm_api import LLMAPI
from scripts.step1_format_fix import FormatFix
from scripts.step2_noise_removal import NoiseRemoval
from scripts.step4_terminology_standardization import TerminologyStandardization

# ===== 在这里设置要处理的文件 =====
# 设置数据文件夹路径（相对于项目根目录或绝对路径）
DATA_FOLDER = "data"  # 例如："data"、"../other_data"、"/absolute/path/to/data"

# 设置要处理的单个文件ID（设置为None表示不处理单个文件）
SINGLE_FILE_ID = 17  # 处理第17个文件

# 设置要处理的文件范围（设置为None表示不处理文件范围）
# 格式：(起始ID, 结束ID) - 包含起始和结束ID
FILE_RANGE = None  # 处理第23-25个文件

# 设置要处理的多个指定文件ID列表（设置为None表示不处理多个文件）
MULTIPLE_FILE_IDS = None  # 例如：[27, 36, 68, 100]

# ===== 设置结束 =====

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化数据处理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # 初始化LLM API
        self.llm_api = LLMAPI(config_path)
        
        # 初始化各个步骤
        self.format_fix = FormatFix(self.llm_api)
        self.noise_removal = NoiseRemoval(self.llm_api)
        self.terminology_standardization = TerminologyStandardization(self.llm_api)
        
        # 创建输出目录
        # 优先使用设置中的DATA_FOLDER，如果没有设置则使用配置文件中的路径
        if 'DATA_FOLDER' in globals():
            self.output_dir = Path(DATA_FOLDER)
        else:
            self.output_dir = Path(self.config.get('data', {}).get('output_dir', 'data'))
        
        # 确保输出目录存在
        self.output_dir.mkdir(exist_ok=True)
        print(f"使用数据文件夹: {self.output_dir.absolute()}")
    
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
        log_file = log_config.get('file', 'logs/data_processor.log')
        
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
    
    def get_pending_files(self) -> List[Path]:
        """
        获取待处理的文件列表
        
        Returns:
            待处理文件路径列表
        """
        pending_files = []
        
        for file_path in self.output_dir.glob("cleaned_object_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查是否已处理
                if data.get("status") == "pending" or data.get("cleaned_text") is None:
                    pending_files.append(file_path)
                    
            except Exception as e:
                self.logger.error(f"读取文件 {file_path} 时出错: {e}")
                continue
        
        return sorted(pending_files)
    
    def validate_data_folder(self) -> bool:
        """
        验证数据文件夹是否存在且包含数据文件
        
        Returns:
            验证是否通过
        """
        if not self.output_dir.exists():
            self.logger.error(f"数据文件夹不存在: {self.output_dir.absolute()}")
            return False
        
        # 检查文件夹中是否有数据文件
        data_files = list(self.output_dir.glob("cleaned_object_*.json"))
        if not data_files:
            self.logger.error(f"数据文件夹中没有找到数据文件: {self.output_dir.absolute()}")
            return False
        
        self.logger.info(f"数据文件夹验证通过，找到 {len(data_files)} 个数据文件")
        return True
    
    def process_single_file(self, file_path: Path) -> bool:
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理是否成功
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            original_text = data.get("original_text", "")
            if not original_text:
                self.logger.error(f"文件 {file_path.name} 中没有原始文本")
                return False
            
            self.logger.info(f"开始处理文件: {file_path.name}")
            
            # Step 1: 格式纠正与拼写修复
            step1_result = self.format_fix.batch_process([original_text])
            if not step1_result:
                self.logger.error(f"Step 1 失败，跳过文件 {file_path.name}")
                return False
            
            step1_cleaned_text = step1_result[0].get("cleaned_text", "")
            
            # Step 2: 噪声剔除与段落切分
            step2_result = self.noise_removal.batch_process([step1_cleaned_text])
            if not step2_result:
                self.logger.error(f"Step 2 失败，跳过文件 {file_path.name}")
                return False
            
            step2_cleaned_text = step2_result[0].get("cleaned_text", "")
            
            # Step 3: 术语标准化
            step3_result = self.terminology_standardization.batch_process([step2_cleaned_text])
            if not step3_result:
                self.logger.error(f"Step 3 失败，跳过文件 {file_path.name}")
                return False
            
            step3_cleaned_text = step3_result[0].get("cleaned_text", "")
            

            
            # 更新数据对象
            data["cleaned_text"] = step3_cleaned_text
            data["status"] = "completed"
            data["processing_steps"] = {
                "step1_format_fix": step1_cleaned_text,
                "step2_noise_removal": step2_cleaned_text,
                "step3_terminology_standardization": step3_cleaned_text
            }
            
            # 保存更新后的文件
            # 只保留 original_text 和 cleaned_text 字段
            output_data = {
                "original_text": data.get("original_text", ""),
                "cleaned_text": step3_cleaned_text
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"文件 {file_path.name} 处理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"处理文件 {file_path.name} 时出错: {e}")
            return False
    
    def process_all_pending_files(self, max_files: int = None):
        """
        处理所有待处理的文件
        
        Args:
            max_files: 最大处理文件数量，None表示处理所有文件
        """
        self.logger.info("=== 开始数据处理 ===")
        
        # 获取待处理文件列表
        pending_files = self.get_pending_files()
        
        if not pending_files:
            self.logger.info("没有待处理的文件")
            return
        
        self.logger.info(f"找到 {len(pending_files)} 个待处理文件")
        
        # 限制处理文件数量
        if max_files and len(pending_files) > max_files:
            pending_files = pending_files[:max_files]
            self.logger.info(f"限制处理文件数量为 {max_files} 个")
        
        # 处理文件
        success_count = 0
        for i, file_path in enumerate(pending_files):
            self.logger.info(f"=== 处理第 {i+1}/{len(pending_files)} 个文件 ===")
            
            if self.process_single_file(file_path):
                success_count += 1
            
            # 每处理10个文件输出一次进度
            if (i + 1) % 10 == 0:
                self.logger.info(f"已处理 {i + 1} 个文件，成功 {success_count} 个")
        
        self.logger.info(f"=== 数据处理完成，共处理 {len(pending_files)} 个文件，成功 {success_count} 个 ===")
    
    def process_specific_files(self, file_ids: List[int]):
        """
        处理指定的文件
        
        Args:
            file_ids: 文件ID列表
        """
        self.logger.info(f"=== 开始处理指定文件: {file_ids} ===")
        
        success_count = 0
        for file_id in file_ids:
            file_path = self.output_dir / f"cleaned_object_{file_id:03d}.json"
            
            if not file_path.exists():
                self.logger.error(f"文件不存在: {file_path}")
                continue
            
            if self.process_single_file(file_path):
                success_count += 1
        
        self.logger.info(f"=== 指定文件处理完成，成功 {success_count}/{len(file_ids)} 个 ===")
    
    def process_file_range(self, start_id: int, end_id: int):
        """
        处理指定范围的文件
        
        Args:
            start_id: 起始文件ID
            end_id: 结束文件ID（包含）
        """
        if start_id > end_id:
            self.logger.error(f"起始ID {start_id} 不能大于结束ID {end_id}")
            return
        
        file_ids = list(range(start_id, end_id + 1))
        self.logger.info(f"=== 开始处理文件范围: {start_id}-{end_id} ===")
        
        success_count = 0
        for file_id in file_ids:
            file_path = self.output_dir / f"cleaned_object_{file_id:03d}.json"
            
            if not file_path.exists():
                self.logger.error(f"文件不存在: {file_path}")
                continue
            
            if self.process_single_file(file_path):
                success_count += 1
        
        self.logger.info(f"=== 文件范围处理完成，成功 {success_count}/{len(file_ids)} 个 ===")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        获取处理统计信息
        
        Returns:
            统计信息字典
        """
        total_files = 0
        pending_files = 0
        completed_files = 0
        failed_files = 0
        
        for file_path in self.output_dir.glob("cleaned_object_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                total_files += 1
                status = data.get("status", "pending")
                
                if status == "completed":
                    completed_files += 1
                elif status == "failed":
                    failed_files += 1
                else:
                    pending_files += 1
                    
            except Exception as e:
                self.logger.error(f"读取文件 {file_path} 时出错: {e}")
                continue
        
        return {
            "total_files": total_files,
            "pending_files": pending_files,
            "completed_files": completed_files,
            "failed_files": failed_files,
            "completion_rate": completed_files / total_files if total_files > 0 else 0
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据处理脚本")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--data-folder", type=str, help="指定数据文件夹路径")
    parser.add_argument("--max-files", type=int, help="最大处理文件数量")
    parser.add_argument("--file-ids", type=int, nargs='+', help="指定要处理的文件ID列表")
    parser.add_argument("--file-range", type=str, help="指定要处理的文件范围，格式：start-end，如：100-102")
    parser.add_argument("--stats", action="store_true", help="显示处理统计信息")
    parser.add_argument("--list-pending", action="store_true", help="列出待处理的文件")
    
    args = parser.parse_args()
    
    # 如果命令行指定了数据文件夹，则覆盖设置中的路径
    if args.data_folder:
        global DATA_FOLDER
        DATA_FOLDER = args.data_folder
        print(f"使用命令行指定的数据文件夹: {DATA_FOLDER}")
    
    # 创建数据处理器
    processor = DataProcessor(args.config)
    
    # 验证数据文件夹
    if not processor.validate_data_folder():
        print("数据文件夹验证失败，请检查DATA_FOLDER设置或--data-folder参数")
        return
    
    if args.stats:
        # 显示统计信息
        stats = processor.get_processing_stats()
        print("处理统计信息:")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  待处理文件数: {stats['pending_files']}")
        print(f"  已完成文件数: {stats['completed_files']}")
        print(f"  失败文件数: {stats['failed_files']}")
        print(f"  完成率: {stats['completion_rate']:.2%}")
        return
    
    if args.list_pending:
        # 列出待处理文件
        pending_files = processor.get_pending_files()
        print(f"待处理文件数量: {len(pending_files)}")
        for file_path in pending_files[:10]:  # 只显示前10个
            print(f"  {file_path.name}")
        if len(pending_files) > 10:
            print(f"  ... 还有 {len(pending_files) - 10} 个文件")
        return
    
    # 处理在脚本前面设置的文件
    total_processed = 0
    
    # 处理单个文件
    if SINGLE_FILE_ID is not None:
        print(f"处理单个文件 ID: {SINGLE_FILE_ID}")
        processor.process_specific_files([SINGLE_FILE_ID])
        total_processed += 1
    
    # 处理文件范围
    if FILE_RANGE is not None:
        start_id, end_id = FILE_RANGE
        print(f"处理文件范围: {start_id}-{end_id}")
        processor.process_file_range(start_id, end_id)
        total_processed += 1
    
    # 处理多个指定文件
    if MULTIPLE_FILE_IDS is not None:
        print(f"处理多个文件 IDs: {MULTIPLE_FILE_IDS}")
        processor.process_specific_files(MULTIPLE_FILE_IDS)
        total_processed += 1
    
    # 如果脚本前面没有设置任何文件，则检查命令行参数
    if total_processed == 0:
        if args.file_range:
            # 处理文件范围
            try:
                start_id, end_id = map(int, args.file_range.split('-'))
                processor.process_file_range(start_id, end_id)
            except ValueError:
                print("错误：文件范围格式不正确，请使用 'start-end' 格式，如：100-102")
                return
        elif args.file_ids:
            # 处理指定文件
            processor.process_specific_files(args.file_ids)
        else:
            # 处理所有待处理文件
            processor.process_all_pending_files(args.max_files)


if __name__ == "__main__":
    main() 