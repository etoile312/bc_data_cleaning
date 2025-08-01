#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据读取脚本
从原始数据文件中读取数据并保存到data文件夹
"""

import json
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any
from scripts.data_preparation import DataPreparation


class DataReader:
    """数据读取器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化数据读取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # 初始化数据准备模块
        self.data_preparation = DataPreparation()
        
        # 创建输出目录
        self.output_dir = Path(self.config.get('data', {}).get('output_dir', 'data'))
        self.output_dir.mkdir(exist_ok=True)
    
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
        log_file = log_config.get('file', 'logs/data_reader.log')
        
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
    
    def read_and_save_data(self, max_docs: int = None):
        """
        读取数据并保存到单独文件
        
        Args:
            max_docs: 最大处理文档数量，None表示处理所有文档
        """
        self.logger.info("=== 开始数据读取和保存 ===")
        
        try:
            # 读取原始数据
            cleaned_objects = self.data_preparation.run()
            
            # 如果设置了最大文档数量限制，则只取前N个
            if max_docs and len(cleaned_objects) > max_docs:
                cleaned_objects = cleaned_objects[:max_docs]
                self.logger.info(f"限制处理文档数量为 {max_docs} 个")
            
            self.logger.info(f"共读取到 {len(cleaned_objects)} 个数据对象")
            
            # 保存每个数据对象到单独文件
            saved_count = 0
            for i, text in enumerate(cleaned_objects):
                try:
                    # 创建数据对象
                    data_object = {
                        "id": i + 1,
                        "original_text": text,
                        "cleaned_text": None,
                        "status": "pending"
                    }
                    
                    # 保存到文件
                    output_file = self.output_dir / f"cleaned_object_{i+1:03d}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data_object, f, ensure_ascii=False, indent=2)
                    
                    saved_count += 1
                    
                    if (i + 1) % 100 == 0:
                        self.logger.info(f"已保存 {i + 1} 个文件...")
                        
                except Exception as e:
                    self.logger.error(f"保存第 {i+1} 个文件时出错: {e}")
                    continue
            
            self.logger.info(f"=== 数据读取完成，共保存 {saved_count} 个文件到 {self.output_dir} ===")
            return saved_count
            
        except Exception as e:
            self.logger.error(f"数据读取失败: {e}")
            return 0
    
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
    
    def get_processed_files(self) -> List[Path]:
        """
        获取已处理的文件列表
        
        Returns:
            已处理文件路径列表
        """
        processed_files = []
        
        for file_path in self.output_dir.glob("cleaned_object_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查是否已处理
                if data.get("status") == "completed" and data.get("cleaned_text") is not None:
                    processed_files.append(file_path)
                    
            except Exception as e:
                self.logger.error(f"读取文件 {file_path} 时出错: {e}")
                continue
        
        return sorted(processed_files)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据读取脚本")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--max-docs", type=int, help="最大处理文档数量，用于测试时限制处理数量")
    parser.add_argument("--list-pending", action="store_true", help="列出待处理的文件")
    parser.add_argument("--list-processed", action="store_true", help="列出已处理的文件")
    
    args = parser.parse_args()
    
    # 创建数据读取器
    reader = DataReader(args.config)
    
    if args.list_pending:
        # 列出待处理文件
        pending_files = reader.get_pending_files()
        print(f"待处理文件数量: {len(pending_files)}")
        for file_path in pending_files[:10]:  # 只显示前10个
            print(f"  {file_path.name}")
        if len(pending_files) > 10:
            print(f"  ... 还有 {len(pending_files) - 10} 个文件")
        return
    
    if args.list_processed:
        # 列出已处理文件
        processed_files = reader.get_processed_files()
        print(f"已处理文件数量: {len(processed_files)}")
        for file_path in processed_files[:10]:  # 只显示前10个
            print(f"  {file_path.name}")
        if len(processed_files) > 10:
            print(f"  ... 还有 {len(processed_files) - 10} 个文件")
        return
    
    # 执行数据读取
    saved_count = reader.read_and_save_data(args.max_docs)
    print(f"数据读取完成，共保存 {saved_count} 个文件")


if __name__ == "__main__":
    main() 