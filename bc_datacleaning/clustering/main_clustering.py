#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主聚类脚本
整合所有聚类功能，执行数据聚类任务
"""

import sys
from pathlib import Path

# 添加父目录到路径，以便导入模块
sys.path.append(str(Path(__file__).parent.parent))

from clustering.label_parser import LabelParser
from clustering.data_clusterer import DataClusterer
from clustering.clustering_config import CLUSTERING_OUTPUT_DIR, DATA_SOURCE_DIR, LABEL_FILE_PATH


def main():
    """主函数"""
    print("=== 乳腺癌数据聚类系统 ===")
    
    # 检查文件是否存在
    label_file = Path(LABEL_FILE_PATH)
    data_dir = Path(DATA_SOURCE_DIR)
    
    if not label_file.exists():
        print(f"错误: 标签文件不存在: {label_file}")
        return
    
    if not data_dir.exists():
        print(f"错误: 数据目录不存在: {data_dir}")
        return
    
    # 初始化标签解析器
    print("1. 初始化标签解析器...")
    label_parser = LabelParser(LABEL_FILE_PATH)
    label_parser.print_category_info()
    
    # 初始化数据聚类器
    print("\n2. 初始化数据聚类器...")
    clusterer = DataClusterer(label_parser)
    
    # 执行聚类
    print("\n3. 开始数据聚类...")
    clusterer.cluster_data(DATA_SOURCE_DIR, CLUSTERING_OUTPUT_DIR)
    
    print("\n=== 聚类完成 ===")
    print(f"聚类结果保存在: {CLUSTERING_OUTPUT_DIR}")


if __name__ == "__main__":
    main() 