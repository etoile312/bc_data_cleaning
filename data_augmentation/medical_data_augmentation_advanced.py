# -*- coding: utf-8 -*-
import re
import random
import json
from copy import deepcopy

# 1. 结构化提取

def extract_sections(text):
    sections = {
        "基本信息": "",
        "既往史": "",
        "个人史": "",
        "婚育史": "",
        "月经史": "",
        "家族史": "",
        "病史": "",
        "辅助检查": "",
        "确诊时间": "",
        "手术": "",
        "术后病理": "",
        "分期": "",
        "基因检测": "",
        "化疗": ""
    }
    patterns = {
        "基本信息": r"基本信息[:：]?(.*?)(?=既往史|个人史|婚育史|月经史|家族史|病史|$)",
        "既往史": r"既往史[:：]?(.*?)(?=个人史|婚育史|月经史|家族史|病史|$)",
        "个人史": r"个人史[:：]?(.*?)(?=婚育史|月经史|家族史|病史|$)",
        "婚育史": r"婚育史[:：]?(.*?)(?=月经史|家族史|病史|$)",
        "月经史": r"月经史[:：]?(.*?)(?=家族史|病史|$)",
        "家族史": r"家族史[:：]?(.*?)(?=病史|$)",
        "病史": r"病史[:：]?(.*?)(?=辅助检查|确诊时间|手术|$)",
        "辅助检查": r"辅助检查[:：]?(.*?)(?=确诊时间|手术|$)",
        "确诊时间": r"确诊时间[:：]?(.*?)(?=手术|$)",
        "手术": r"手术[:：]?(.*?)(?=术后病理|分期|基因检测|化疗|$)",
        "术后病理": r"术后病理[:：]?(.*?)(?=分期|基因检测|化疗|$)",
        "分期": r"(术后分期|分期)[:：]?(.*?)(?=基因检测|化疗|$)",
        "基因检测": r"(BRCA1/2遗传易感基因|基因检测)[:：]?(.*?)(?=化疗|$)",
        "化疗": r"化疗[:：]?(.*)$"
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.S)
        if m:
            # 分期、基因检测正则多一组
            if key in ["分期", "基因检测"] and len(m.groups()) > 1:
                sections[key] = m.group(2).strip()
            else:
                sections[key] = m.group(1).strip()
    return sections

# 2. 数据增强示例

def augment_basic_info(info):
    # 姓名脱敏、年龄扰动
    name_pat = r"([\u4e00-\u9fa5]{1,3})\*{0,2}"
    age_pat = r"(\d{2,3})岁"
    surnames = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
    info = re.sub(name_pat, random.choice(surnames) + "**", info)
    def age_replace(m):
        age = int(m.group(1))
        new_age = max(1, age + random.choice([-2, -1, 0, 1, 2]))
        return f"{new_age}岁"
    info = re.sub(age_pat, age_replace, info)
    return info

def augment_family_history(fam):
    diseases = ["胃癌", "肺癌", "肝癌", "乳腺癌"]
    fam = re.sub(r"胃癌", random.choice(diseases), fam)
    fam = fam.replace("体健", random.choice(["健康", "无异常", "良好"]))
    return fam

def augment_exam(exam):
    def float_perturb(match):
        val = float(match.group(1))
        perturbed = round(val + random.uniform(-0.5, 0.5), 1)
        return f"{perturbed}{match.group(2)}"
    exam = re.sub(r"(\d+\.\d+)(cm)", float_perturb, exam)
    return exam

def augment_menstrual_history(hist):
    # 月经规律性扰动
    options = ["规律", "不规律", "周期正常", "偶有提前", "偶有延后"]
    hist = re.sub(r"月经规律", random.choice(options), hist)
    return hist

def augment_marriage_history(hist):
    # 婚育史年龄扰动
    age_pat = r"(\d{2,3})\s*岁结婚"
    def age_replace(m):
        age = int(m.group(1))
        new_age = max(15, age + random.choice([-2, -1, 0, 1, 2]))
        return f"{new_age}岁结婚"
    hist = re.sub(age_pat, age_replace, hist)
    return hist

def augment_record(text, n=5):
    sections = extract_sections(text)
    augmented_records = []
    for _ in range(n):
        aug = deepcopy(sections)
        aug["基本信息"] = augment_basic_info(aug["基本信息"])
        aug["家族史"] = augment_family_history(aug["家族史"])
        aug["辅助检查"] = augment_exam(aug["辅助检查"])
        aug["月经史"] = augment_menstrual_history(aug["月经史"])
        aug["婚育史"] = augment_marriage_history(aug["婚育史"])
        # 其他部分可继续扩展
        augmented_records.append(aug)
    return augmented_records

if __name__ == "__main__":
    # 示例病历文本
    text = """基本信息：朱**，女， 1973-07-01出生（现年51岁）。\n既往史：无殊\n个人史：无殊\n婚育史： 25  岁结婚，育有1子，体健。\n月经史：平素月经规律，47岁已绝经。\n家族史：父母已故，父亲卒于年迈，母亲及大哥因“胃癌”去世。余兄弟姐妹体健。\n病史：2020-10触及左乳肿物\n辅助检查：乳腺B超：左乳外上象限腺体边缘低回声结节BI-RADS 4a类（2.7×2.2cm）。左侧腋下一淋巴肿大（2.3×1.7cm）。\n钼靶：左乳腋尾区占位，BI-RADS 4b考虑（长径约33mm ），右侧腋下见肿大淋巴结影(短径21mm)。\n胸部CT：左乳腋尾区结节，左侧腋下淋巴结肿大。\n确诊时间：2020.10.10\n手术：左乳及腋窝淋巴结穿刺活检术：左乳浸润性导管癌，腋窝淋巴结穿刺阳性\n免疫组化： ER（-）、PR（-）、C-erbB-2（1+），Ki-67（+, 约80%）。\n术后分期： cT2N1M0 ⅡB期（三阴性）\n治疗：手术。手术时间：2020.10.20 手术方式：左乳癌改良根治术+腋窝淋巴结清扫\n术后病理：1.（左乳）浸润性导管癌伴局灶神经内分泌分化，Ⅲ级。单灶3*2.5cm，累犯神经及脉管；（乳头及基底切缘）阴性；\n2. 腋淋巴结转移:   3 / 22\n免疫组化： ER（-）、PR（-）、C-erbB-2（1+），Ki-67（+, 约80%）。\n术后分期： pT2N1M0 ⅡB期（三阴性）\nBRCA1/2遗传易感基因（NGS）： 未发现与疾病表型相关的致病突变。\n辅助化疗1:2020-11-15辅助化疗：EC  q3w（体表面积：1.62㎡） 吡柔比星 80mg +环磷酰胺 800mg q3W  24小时后：聚乙二醇化重组人粒细胞刺激因子6mg 一级预防。中度（2级）肝功能损害（ALT 183U/L↑，AST 102U/L↑） 4度骨髓抑制（NE 0.01*10^9/L↓，PLT 55*10^9/L↓）及粒缺性发热\n辅助化疗2:2020.12-2021.5：AC-T 吡柔比星 80mg +环磷酰胺 800mg q3W 白蛋白紫杉醇 200mg d1 d8  q3w  轻度（1级）肝功能损害（ALT 50U/L↑，AST 55U/L↑） 2度骨髓抑制（NE 1.30*10^9/L↓ ）。\n"""
    augmented = augment_record(text, n=5)
    with open("data_augmentation/data_augmentation/augmented_medical_records_advanced.json", "w", encoding="utf-8") as f:
        json.dump(augmented, f, ensure_ascii=False, indent=2)
    print("已生成增强病历并保存为 data_augmentation/data_augmentation/augmented_medical_records_advanced.json") 