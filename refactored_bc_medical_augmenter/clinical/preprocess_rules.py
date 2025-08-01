"""
临床风格文本生成前的字段预处理与规则转换模块。
所有与结构化字段到自然语言表达相关的规则均集中于此，便于维护和扩展。
"""

import random
from typing import Dict, Any, List, Set

def preprocess_case_fields(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    优化结构化字段表达逻辑，按新规则补充变量间约束，并生成更符合医生表达习惯的表达片段。
    返回：{'expressions': List[str], ...其余字段...}
    """
    new_case = dict(case)
    expressions = []
    suppress_fields: Set[str] = set()

    # 1. 转移/复发表达去重
    if new_case.get("转移位置") not in ["", None]:
        suppress_fields.update(["远处转移", "转移或复发"])
    if new_case.get("复发时间") not in ["", None]:
        suppress_fields.update(["复发", "转移或复发"])

    # 2. "是否"类字段事件性表达
    if new_case.get("绝经状态") == "是":
        expressions.append("已绝经")
        suppress_fields.add("绝经状态")
    elif new_case.get("绝经状态") == "否":
        expressions.append("未绝经")
        suppress_fields.add("绝经状态")

    # 3. 手术表达
    if new_case.get("是否保乳") == "是":
        expressions.append("行保乳手术")
        suppress_fields.add("是否保乳")
    elif new_case.get("是否保乳") == "否":
        expressions.append("行根治手术")
        suppress_fields.add("是否保乳")

    # 4. 复发/转移时间表达
    if new_case.get("复发时间") not in ["", None]:
        expressions.append(f"{new_case['复发时间']}复发")
        suppress_fields.add("复发时间")
    if new_case.get("转移位置") not in ["", None]:
        # 只保留部位，不要字段名
        parts = new_case["转移位置"].replace("，", ",").replace("及", ",").replace(" ", "").split(",")
        parts = [p for p in parts if p]
        if parts:
            expressions.append("、".join(parts) + "转移")
        suppress_fields.add("转移位置")

    # 5. 肿块大小合并表达
    pre = new_case.get("肿块大小CM(术前)")
    post = new_case.get("肿块大小CM(术后)")
    if pre and post:
        expressions.append(f"术前肿块大小{pre}cm，术后{post}cm")
        suppress_fields.update(["肿块大小CM(术前)", "肿块大小CM(术后)"])
    elif pre:
        expressions.append(f"肿块大小{pre}cm")
        suppress_fields.add("肿块大小CM(术前)")
    elif post:
        expressions.append(f"肿块大小{post}cm")
        suppress_fields.add("肿块大小CM(术后)")

    # 6. MP评分表达
    mp_val = new_case.get("MP评分")
    if mp_val not in ["", None, "无"]:
        mp_expr_options = [
            f"MP评分为{mp_val}分",
            f"MP评分为{mp_val}",
            f"MP{mp_val}分"
        ]
        expressions.append(random.choice(mp_expr_options))
        suppress_fields.add("MP评分")

    # 7. 根治手术时间表达
    surgery_time = new_case.get("根治手术时间")
    if surgery_time not in ["", None]:
        expressions.append(f"{surgery_time}行根治手术")
        suppress_fields.add("根治手术时间")

    # 8. 病理分级表达
    grade = new_case.get("组织学分级")
    if grade not in ["", None]:
        expressions.append(f"{grade}")
        suppress_fields.add("组织学分级")

    # 9. 免疫组化表达
    er_val = new_case.get("ER%")
    pr_val = new_case.get("PR%")
    her2_val = new_case.get("Her-2免疫组化")
    fish_val = new_case.get("FISH")
    ki67_val = new_case.get("Ki-67%")
    
    if any([er_val, pr_val, her2_val, fish_val, ki67_val]):
        immuno_expressions = []
        if er_val not in ["", None]:
            immuno_expressions.append(f"ER({er_val}%)")
            suppress_fields.add("ER%")
        if pr_val not in ["", None]:
            immuno_expressions.append(f"PR({pr_val}%)")
            suppress_fields.add("PR%")
        if her2_val not in ["", None]:
            immuno_expressions.append(f"HER-2({her2_val})")
            suppress_fields.add("Her-2免疫组化")
        if fish_val not in ["", None]:
            immuno_expressions.append(f"FISH({fish_val})")
            suppress_fields.add("FISH")
        if ki67_val not in ["", None]:
            immuno_expressions.append(f"Ki-67({ki67_val}%)")
            suppress_fields.add("Ki-67%")
        
        if immuno_expressions:
            expressions.append("免疫组化：" + "，".join(immuno_expressions))

    # 10. 淋巴结表达
    lymph_positive = new_case.get("腋窝淋巴结是否有阳性")
    lymph_count_pre = new_case.get("腋窝淋巴结阳性个数(术前)")
    lymph_count_post = new_case.get("腋窝淋巴结阳性个数(术后)")
    
    if lymph_positive == "是":
        if lymph_count_pre not in ["", None]:
            expressions.append(f"腋窝淋巴结转移({lymph_count_pre}个)")
            suppress_fields.add("腋窝淋巴结阳性个数(术前)")
        elif lymph_count_post not in ["", None]:
            expressions.append(f"腋窝淋巴结转移({lymph_count_post}个)")
            suppress_fields.add("腋窝淋巴结阳性个数(术后)")
        else:
            expressions.append("腋窝淋巴结转移")
        suppress_fields.add("腋窝淋巴结是否有阳性")

    # 11. 切缘表达
    margin_positive = new_case.get("切缘阳性")
    margin_thin = new_case.get("切缘<1mm")
    
    if margin_positive == "是":
        expressions.append("切缘阳性")
        suppress_fields.add("切缘阳性")
    elif margin_positive == "否":
        expressions.append("切缘阴性")
        suppress_fields.add("切缘阳性")
    
    if margin_thin == "是":
        expressions.append("切缘<1mm")
        suppress_fields.add("切缘<1mm")

    # 12. 分期表达
    ctnm = new_case.get("cTNM")
    ptnm = new_case.get("pTNM")
    yptnm = new_case.get("ypTNM")
    
    if ctnm not in ["", None]:
        expressions.append(f"临床分期{ctnm}")
        suppress_fields.add("cTNM")
    if ptnm not in ["", None]:
        expressions.append(f"病理分期{ptnm}")
        suppress_fields.add("pTNM")
    if yptnm not in ["", None]:
        expressions.append(f"新辅助治疗后分期{yptnm}")
        suppress_fields.add("ypTNM")

    # 13. 治疗反应表达
    pcr = new_case.get("pCR")
    ypt0n0 = new_case.get("ypT0N0")
    
    if pcr == "是":
        expressions.append("pCR")
        suppress_fields.add("pCR")
    if ypt0n0 == "是":
        expressions.append("ypT0N0")
        suppress_fields.add("ypT0N0")

    # 14. 药品信息表达
    drug_info = new_case.get("药品信息")
    if drug_info and isinstance(drug_info, list) and len(drug_info) > 0:
        if isinstance(drug_info[0], str):
            # 方案名称
            expressions.append(f"治疗方案：{', '.join(drug_info)}")
        elif isinstance(drug_info[0], dict):
            # 药品明细
            drug_names = [drug.get("药品名称", "") for drug in drug_info if drug.get("药品名称")]
            if drug_names:
                expressions.append(f"使用药物：{', '.join(drug_names)}")
        suppress_fields.add("药品信息")

    # 15. 其他字段按需扩展
    # ...

    # 16. 只保留未被 suppress 的字段
    for field in list(new_case.keys()):
        if field in suppress_fields:
            del new_case[field]

    # 17. 生成最终表达片段
    new_case['expressions'] = expressions
    return new_case

def random_name() -> str:
    """生成随机姓名"""
    surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    return random.choice(surnames) + "**" 