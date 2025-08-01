"""
结构化数据生成的字段分组模块。
定义各种医学字段的分组，便于按逻辑生成相关字段。
"""

SEGMENT_GROUPS = {
    "basic_info": ["年龄", "绝经状态", "PS"],
    "stage_and_metastasis": ["IV期", "M1分期", "远处转移", "转移位置", "转移或复发", "复发"],
    "surgery": ["是否保乳", "已行根治手术", "可再次手术", "切缘<1mm", "切缘阳性", "是否腋窝清扫", "腋窝淋巴结是否有阳性", "腋窝淋巴结阳性个数(术前)", "腋窝淋巴结阳性个数(术后)", "根治手术时间"],
    "pathology": ["组织学分级", "ER%", "PR%", "Her-2免疫组化", "FISH", "Ki-67%"],
    "tumor_size": [
        "肿块大小CM(术前)", "肿块大小CM(术后)",
        "术前肿块大小CM(CT)", "术前肿块大小CM(MRI)", "术前肿块大小CM(B超)", "术前肿块大小CM(查体)",
        "术后肿块大小CM(CT)", "术后肿块大小CM(MRI)", "术后肿块大小CM(B超)", "术后肿块大小CM(查体)"
    ],
    "treatment": ["药品信息", "免疫禁忌", "有新辅助治疗", "新辅助治疗使用免疫", "新辅助治疗使用双靶"],
    "response": ["pCR", "ypT0N0", "MP评分"],
    "prognosis": ["DFS（月）", "复发时间"],
    "risk": ["基因高风险"],
    "staging": ["cTNM", "pTNM", "ypTNM"]
}

def validate_fields():
    """检查字段是否都在 rules 中定义"""
    from .field_parser import FieldRuleParser
    parser = FieldRuleParser('rules/breast_cancer_rules.json')
    fields = parser.get_field_defs()
    
    missing_fields = []
    for group, fs in SEGMENT_GROUPS.items():
        for f in fs:
            if f not in fields:
                missing_fields.append(f)
                print(f"[警告] 字段 {f} 未在 rules/breast_cancer_rules.json 中定义！")
    
    if missing_fields:
        print(f"总共发现 {len(missing_fields)} 个未定义字段")
    else:
        print("所有字段都已正确定义")
    
    return missing_fields

if __name__ == "__main__":
    validate_fields() 