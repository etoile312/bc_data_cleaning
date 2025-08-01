#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据聚类器
根据标签字段对数据进行聚类
"""

import json
import shutil
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path
from .label_parser import LabelParser
from .clustering_config import CATEGORY_MAPPING


class DataClusterer:
    """数据聚类器类"""
    
    def __init__(self, label_parser: LabelParser):
        """
        初始化数据聚类器
        
        Args:
            label_parser: 标签解析器实例
        """
        self.label_parser = label_parser
        self.clusters = {}
    
    def cluster_data(self, data_dir: str, output_dir: str):
        """
        对数据进行聚类
        
        Args:
            data_dir: 数据目录
            output_dir: 输出目录
        """
        print("开始数据聚类...")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 获取所有数据文件
        data_files = list(Path(data_dir).glob("cleaned_object_*.json"))
        print(f"找到 {len(data_files)} 个数据文件")
        
        # 初始化聚类结果
        self._init_clusters()
        
        # 处理每个数据文件
        for file_path in data_files:
            self._process_single_file(file_path)
        
        # 保存聚类结果并复制文件
        self._save_clusters_and_copy_files(output_path, data_dir)
        
        # 打印聚类统计
        self._print_clustering_stats()
    
    def _init_clusters(self):
        """初始化聚类结果"""
        self.clusters = {}
        
        # 初始化大分类聚类
        major_categories = [
            "endocrine_records", "surgery_records", "chemotherapy_records", "immunotherapy", 
            "radiotherapy_records", "targeted_therapy", "adjuvant_therapy"
        ]
        
        for category in major_categories:
            self.clusters[category] = []
        
        # 初始化细分分类聚类
        # 病理报告细分
        pathology_types = ["biopsy_pathology", "postoperative_pathology", "molecular_pathology", "genetic_testing"]
        for p_type in pathology_types:
            self.clusters[f"pathology_reports_{p_type}"] = []
        
        # 病情诊断与评估细分
        diagnosis_stages = ["initial_diagnosis", "neoadjuvant_treatment", "recurrence_diagnosis", "salvage_treatment", "follow_up"]
        for stage in diagnosis_stages:
            self.clusters[f"diagnosis_assessment_{stage}"] = []
    
    def _process_single_file(self, file_path: Path):
        """
        处理单个数据文件
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            original_text = data.get("original_text", "")
            cleaned_text = data.get("cleaned_text", "")
            
            # 合并原始文本和清洗后文本进行匹配
            combined_text = f"{original_text} {cleaned_text}"
            
            # 对每个分类进行匹配
            self._match_categories(file_path.name, combined_text)
            
        except Exception as e:
            print(f"处理文件 {file_path.name} 时出错: {e}")
    
    def _match_categories(self, file_name: str, text: str):
        """
        匹配文本中的分类
        
        Args:
            file_name: 文件名
            text: 文本内容
        """
        # 匹配大分类
        major_categories = [
            "endocrine_records", "surgery_records", "chemotherapy_records", "immunotherapy", 
            "radiotherapy_records", "targeted_therapy", "adjuvant_therapy"
        ]
        
        for category in major_categories:
            if self._text_contains_category(text, category):
                self.clusters[category].append(file_name)
        
        # 匹配病理报告细分
        pathology_types = ["biopsy_pathology", "postoperative_pathology", "molecular_pathology", "genetic_testing"]
        for p_type in pathology_types:
            if self._text_contains_pathology_type(text, p_type):
                self.clusters[f"pathology_reports_{p_type}"].append(file_name)
        
        # 匹配病情诊断与评估细分
        diagnosis_stages = ["initial_diagnosis", "neoadjuvant_treatment", "recurrence_diagnosis", "salvage_treatment", "follow_up"]
        for stage in diagnosis_stages:
            if self._text_contains_diagnosis_stage(text, stage):
                self.clusters[f"diagnosis_assessment_{stage}"].append(file_name)
    
    def _text_contains_category(self, text: str, category: str) -> bool:
        """
        检查文本是否包含指定分类的关键词
        
        Args:
            text: 文本内容
            category: 分类名称
            
        Returns:
            是否包含该分类
        """
        # 定义每个分类的关键词
        category_keywords = {
            "endocrine_records": ["内分泌", "激素", "他莫昔芬", "来曲唑", "阿那曲唑", "依西美坦", "氟维司群"],
            "surgery_records": ["手术", "切除", "根治", "保乳", "淋巴结清扫", "前哨淋巴结", "乳房重建"],
            "chemotherapy_records": ["化疗", "化疗方案", "化疗药物", "紫杉醇", "多西他赛", "环磷酰胺", "阿霉素"],
            "immunotherapy": ["免疫", "PD-1", "PD-L1", "免疫检查点", "免疫治疗"],
            "radiotherapy_records": ["放疗", "放射治疗", "放疗方案", "放疗部位", "放疗剂量"],
            "targeted_therapy": ["靶向", "曲妥珠单抗", "帕妥珠单抗", "拉帕替尼", "奈拉替尼"],
            "adjuvant_therapy": ["辅助治疗", "骨保护", "双膦酸盐", "地诺单抗"]
        }
        
        keywords = category_keywords.get(category, [category])
        return any(keyword in text for keyword in keywords)
    
    def _text_contains_pathology_type(self, text: str, pathology_type: str) -> bool:
        """
        检查文本是否包含指定病理类型
        
        Args:
            text: 文本内容
            pathology_type: 病理类型
            
        Returns:
            是否包含该病理类型
        """
        pathology_keywords = {
            "biopsy_pathology": ["活检", "穿刺", "切取"],
            "postoperative_pathology": ["术后病理", "手术病理", "切除病理"],
            "molecular_pathology": ["分子病理", "ER", "PR", "HER2", "Ki67", "FISH"],
            "genetic_testing": ["基因检测", "BRCA", "21基因", "CTC", "PD-L1"]
        }
        
        keywords = pathology_keywords.get(pathology_type, [pathology_type])
        return any(keyword in text for keyword in keywords)
    
    def _text_contains_diagnosis_stage(self, text: str, stage: str) -> bool:
        """
        检查文本是否包含指定诊断阶段
        
        Args:
            text: 文本内容
            stage: 诊断阶段
            
        Returns:
            是否包含该诊断阶段
        """
        stage_keywords = {
            "initial_diagnosis": ["初诊", "首次诊断", "初次就诊"],
            "neoadjuvant_treatment": ["新辅助", "术前治疗"],
            "recurrence_diagnosis": ["复发", "复发确诊"],
            "salvage_treatment": ["解救治疗", "姑息治疗"],
            "follow_up": ["随访", "跟踪", "复查"]
        }
        
        keywords = stage_keywords.get(stage, [stage])
        return any(keyword in text for keyword in keywords)
    
    def _save_clusters_and_copy_files(self, output_path: Path, data_dir: str):
        """
        保存聚类结果并复制文件到对应目录
        
        Args:
            output_path: 输出路径
            data_dir: 数据源目录
        """
        # 保存聚类结果到JSON文件
        clusters_file = output_path / "clustering_results.json"
        with open(clusters_file, 'w', encoding='utf-8') as f:
            json.dump(self.clusters, f, ensure_ascii=False, indent=2)
        
        # 为每个聚类创建单独的目录和文件列表
        for cluster_name, file_list in self.clusters.items():
            if file_list:  # 只处理非空聚类
                cluster_dir = output_path / cluster_name
                cluster_dir.mkdir(exist_ok=True)
                
                # 保存文件列表
                file_list_path = cluster_dir / "file_list.txt"
                with open(file_list_path, 'w', encoding='utf-8') as f:
                    for file_name in file_list:
                        f.write(f"{file_name}\n")
                
                # 保存聚类信息
                cluster_info = {
                    "cluster_name": cluster_name,
                    "file_count": len(file_list),
                    "files": file_list
                }
                
                info_file = cluster_dir / "cluster_info.json"
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(cluster_info, f, ensure_ascii=False, indent=2)
                
                # 复制数据文件到聚类目录
                print(f"复制 {len(file_list)} 个文件到 {cluster_name} 目录...")
                for file_name in file_list:
                    source_file = Path(data_dir) / file_name
                    target_file = cluster_dir / file_name
                    if source_file.exists():
                        shutil.copy2(source_file, target_file)
                    else:
                        print(f"警告: 源文件不存在: {source_file}")
        
        print(f"聚类结果已保存到: {output_path}")
    
    def _print_clustering_stats(self):
        """打印聚类统计信息"""
        print("\n=== 聚类统计 ===")
        
        total_files = set()
        for cluster_name, file_list in self.clusters.items():
            if file_list:
                print(f"{cluster_name}: {len(file_list)} 个文件")
                total_files.update(file_list)
        
        print(f"\n总共有 {len(total_files)} 个文件被聚类")
        
        # 统计未分类文件
        data_files = list(Path("data").glob("cleaned_object_*.json"))
        all_files = {f.name for f in data_files}
        unclassified = all_files - total_files
        
        if unclassified:
            print(f"未分类文件: {len(unclassified)} 个")
            print("未分类文件列表:")
            for file_name in sorted(unclassified):
                print(f"  - {file_name}") 