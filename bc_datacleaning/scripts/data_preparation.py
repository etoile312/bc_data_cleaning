#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据准备模块
负责从原始数据文件中提取和预处理清洗对象
"""

import json
import re
import pandas as pd
from pathlib import Path
from typing import List


class DataPreparation:
    """数据准备类"""
    
    def __init__(self, data_file: str = "hx_data.xls"):
        """
        初始化数据准备器
        
        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_target_data(self) -> List[str]:
        """
        提取乳腺癌相关的第10列（prefixed_content）内容
        
        Returns:
            提取的文本列表
        """
        # 构建完整的数据文件路径
        project_root = Path(__file__).parent.parent
        data_file_path = project_root / self.data_file
        
        print(f"正在读取文件: {data_file_path}")
        
        if not data_file_path.exists():
            print(f"错误: 数据文件不存在: {data_file_path}")
            return []
        
        try:
            # 使用 xlrd 读取 .xls 文件
            print("使用xlrd引擎读取xls文件")
            df = pd.read_excel(data_file_path, header=0, engine='xlrd')
            
            print(f"成功读取数据，共 {len(df)} 行")
            print(f"列名: {list(df.columns)}")
            
            # 检查列数
            if len(df.columns) < 10:
                print(f"错误: 数据只有 {len(df.columns)} 列，无法提取第10列")
                return []
            
            # 只保留乳腺癌相关数据
            if "csv_cancer_type_name" in df.columns:
                target_data = df[df["csv_cancer_type_name"].str.contains("乳腺癌", na=False)]
                print(f"找到 {len(target_data)} 行乳腺癌相关数据")
            else:
                print("未找到 csv_cancer_type_name 列，使用全部数据")
                target_data = df
            
            # 提取第10列（索引9，prefixed_content）
            j_column_data = target_data.iloc[:, 9].dropna().tolist()
            print(f"提取到 {len(j_column_data)} 条有效第10列数据")
            
            # 调试：显示第一个内容示例
            if j_column_data:
                first_content = str(j_column_data[0])[:200] + "..." if len(str(j_column_data[0])) > 200 else str(j_column_data[0])
                print(f"第一个内容示例: {first_content}")
            
            return j_column_data
            
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return []
    
    def extract_words_result_content(self, text: str) -> str:
        """
        从文本中提取实际内容
        
        Args:
            text: 原始文本
            
        Returns:
            提取的内容
        """
        try:
            # 检查是否是JSON格式
            if isinstance(text, str) and text.startswith("{") and "'words_result':" in text:
                # 使用正则表达式提取 words_result 的值
                pattern = r"'words_result':\s*'([^']*)'"
                match = re.search(pattern, text, re.DOTALL)
                
                if match:
                    return match.group(1).strip()
                else:
                    # 尝试其他格式
                    pattern2 = r"'words_result':\s*\"([^\"]*)\""
                    match2 = re.search(pattern2, text, re.DOTALL)
                    if match2:
                        return match2.group(1).strip()
                    else:
                        print(f"未找到目标内容模式: {text[:100]}...")
                        return text
            else:
                # 如果不是JSON格式，直接返回文本内容
                return text
                
        except Exception as e:
            print(f"提取内容时出错: {e}")
            return text
    
    def process_raw_data(self) -> List[str]:
        """
        处理原始数据，提取清洗对象
        
        Returns:
            清洗对象列表
        """
        raw_data = self.extract_target_data()
        cleaned_objects = []
        
        print("开始提取清洗对象...")
        
        for i, text in enumerate(raw_data):
            if pd.isna(text) or not isinstance(text, str):
                continue
                
            extracted_content = self.extract_words_result_content(text)
            if extracted_content:
                cleaned_objects.append(extracted_content)
                
            if (i + 1) % 100 == 0:
                print(f"已处理 {i + 1} 条数据")
        
        print(f"成功提取 {len(cleaned_objects)} 个清洗对象")
        return cleaned_objects
    
    def save_cleaned_objects(self, cleaned_objects: List[str], base_filename: str = "cleaned_object"):
        """
        保存清洗对象到单独的JSON文件
        
        Args:
            cleaned_objects: 清洗对象列表
            base_filename: 基础文件名
        """
        try:
            for i, obj in enumerate(cleaned_objects):
                # 为每条数据创建单独的JSON文件
                filename = f"{base_filename}_{i+1:03d}.json"
                output_file = self.output_dir / filename
                
                # 初始时只设置原始文本，清洗文本为空
                data_structure = {
                    "original_text": obj,
                    "cleaned_text": None  # 初始为空，经过大模型清洗后才有内容
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data_structure, f, ensure_ascii=False, indent=2)
            
            print(f"已保存 {len(cleaned_objects)} 个清洗对象到单独文件")
            
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def run(self):
        """运行数据准备流程"""
        print("=== 开始数据准备流程 ===")
        
        # 提取清洗对象
        cleaned_objects = self.process_raw_data()
        
        # 保存结果
        self.save_cleaned_objects(cleaned_objects)
        
        print("=== 数据准备完成 ===")
        return cleaned_objects


if __name__ == "__main__":
    # 运行数据准备
    preparer = DataPreparation()
    cleaned_objects = preparer.run() 