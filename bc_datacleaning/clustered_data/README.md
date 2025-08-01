# 乳腺癌数据聚类结果说明

## 聚类统计

本项目将清洗后的1735+个乳腺癌病历文件按专业领域自动分类到以下15个目录：

### 主要治疗类型 (7类)

| 分类目录 | 文件数量 | 说明 |
|---------|---------|------|
| `endocrine_records/` | 187 | 内分泌治疗记录 |
| `surgery_records/` | 191 | 手术记录 |
| `chemotherapy_records/` | 49 | 化疗记录 |
| `immunotherapy/` | 128 | 免疫治疗 |
| `radiotherapy_records/` | 27 | 放疗记录 |
| `targeted_therapy/` | 47 | 靶向治疗 |
| `adjuvant_therapy/` | 5 | 辅助治疗 |

### 病理报告细分 (4类)

| 分类目录 | 文件数量 | 说明 |
|---------|---------|------|
| `pathology_reports_molecular_pathology/` | 235 | 分子病理 |
| `pathology_reports_biopsy_pathology/` | 36 | 活检病理 |
| `pathology_reports_genetic_testing/` | 27 | 基因检测 |
| `pathology_reports_postoperative_pathology/` | 18 | 术后病理 |

### 诊断评估细分 (5类)

| 分类目录 | 文件数量 | 说明 |
|---------|---------|------|
| `diagnosis_assessment_follow_up/` | 173 | 随访评估 |
| `diagnosis_assessment_initial_diagnosis/` | 20 | 初诊评估 |
| `diagnosis_assessment_neoadjuvant_treatment/` | 18 | 新辅助治疗 |
| `diagnosis_assessment_recurrence_diagnosis/` | 20 | 复发诊断 |
| `diagnosis_assessment_salvage_treatment/` | 1 | 挽救治疗 |

## 分类依据

聚类基于以下关键词匹配：

- **内分泌治疗**: 内分泌、激素、他莫昔芬、来曲唑等
- **手术记录**: 手术、切除、根治、保乳、淋巴结清扫等
- **化疗记录**: 化疗、化疗方案、紫杉醇、多西他赛等
- **免疫治疗**: 免疫、PD-1、PD-L1、免疫检查点等
- **放疗记录**: 放疗、放射治疗、放疗方案等
- **靶向治疗**: 靶向、曲妥珠单抗、帕妥珠单抗等
- **病理报告**: 根据病理类型和检测方法细分
- **诊断评估**: 根据患者所处治疗阶段分类

## 数据格式

每个目录下包含清洗后的JSON格式病历文件，文件名格式为 `cleaned_object_XXX.json`。

## 统计信息

详细的分类统计信息请查看 `clustering_stats.json` 文件。

## 总计

- **总分类数**: 15个专业分类
- **总文件数**: 约1735个病历文件
- **最大分类**: 分子病理 (235个文件)
- **最小分类**: 挽救治疗 (1个文件)

---

*聚类结果基于关键词匹配算法，每个文件可能同时属于多个分类。* 