#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚类配置文件
定义聚类规则和分类标准
"""

# 聚类分类规则
CLUSTERING_RULES = {
    # 大分类聚类（按标签名称聚类）
    "major_categories": [
        "endocrine_records",      # 内分泌记录
        "surgery_records",        # 手术记录
        "chemotherapy_records",   # 化疗记录
        "immunotherapy",          # 免疫治疗
        "radiotherapy_records",   # 放疗记录
        "targeted_therapy",       # 靶向治疗
        "adjuvant_therapy"        # 辅助治疗
    ],
    
    # 需要细分的大分类
    "sub_categories": {
        "pathology_reports": {    # 病理报告
            "field": "病理类型",
            "values": ["biopsy_pathology", "postoperative_pathology", "molecular_pathology", "genetic_testing"]
        },
        "diagnosis_assessment": { # 病情诊断与评估
            "field": "患者所处阶段", 
            "values": ["initial_diagnosis", "neoadjuvant_treatment", "recurrence_diagnosis", "salvage_treatment", "follow_up"]
        }
    }
}

# 中文到英文的映射
CATEGORY_MAPPING = {
    # 大分类映射
    "内分泌记录": "endocrine_records",
    "手术记录": "surgery_records", 
    "化疗记录": "chemotherapy_records",
    "免疫治疗": "immunotherapy",
    "放疗记录": "radiotherapy_records",
    "靶向治疗": "targeted_therapy",
    "辅助治疗": "adjuvant_therapy",
    
    # 病理报告细分映射
    "病理报告_活检病理": "pathology_reports_biopsy",
    "病理报告_术后病理": "pathology_reports_postoperative",
    "病理报告_分子病理": "pathology_reports_molecular",
    "病理报告_基因检测": "pathology_reports_genetic",
    
    # 病情诊断与评估细分映射
    "病情诊断与评估_初诊": "diagnosis_assessment_initial",
    "病情诊断与评估_新辅助治疗中": "diagnosis_assessment_neoadjuvant",
    "病情诊断与评估_复发确诊": "diagnosis_assessment_recurrence",
    "病情诊断与评估_解救治疗中": "diagnosis_assessment_salvage",
    "病情诊断与评估_随访跟踪记录": "diagnosis_assessment_followup"
}

# 聚类输出目录
CLUSTERING_OUTPUT_DIR = "clustered_data"

# 数据源目录
DATA_SOURCE_DIR = "data"

# 标签文件路径
LABEL_FILE_PATH = "bc_strct_label.json" 