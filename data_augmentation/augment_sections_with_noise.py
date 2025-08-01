# -*- coding: utf-8 -*-
import re
import random
import json
from datetime import datetime, timedelta
from copy import deepcopy

# 读取模板库
with open("data_augmentation/augmentation_templates.json", "r", encoding="utf-8") as f:
    TEMPLATES = json.load(f)

# 简单同义词库
SYNONYMS = {
    "发现": ["检测到", "查见", "观察到"],
    "肿块": ["肿物", "结节"],
    "提示": ["显示", "见到", "发现"],
    "穿刺": ["活检", "取样"],
    "分期": ["分级", "阶段"],
    "腋下": ["腋窝", "腋部"],
    "淋巴结": ["淋巴组织", "淋巴结构"],
    "异常": ["异常", "异常表现", "异常情况"]
}

# 工具函数：区间采样

def sample_from_range(val_range, is_int=False, is_date=False):
    if is_date:
        fmt = "%Y-%m-%d"
        start = datetime.strptime(val_range[0], fmt)
        end = datetime.strptime(val_range[1], fmt)
        delta = (end - start).days
        rand_days = random.randint(0, delta)
        return (start + timedelta(days=rand_days)).strftime(fmt)
    elif is_int:
        a, b = int(val_range[0]), int(val_range[1])
        return str(random.randint(a, b))
    else:
        a, b = float(val_range[0]), float(val_range[1])
        return str(round(random.uniform(a, b), 1))

# 嵌套模板递归填充

def fill_template(section, template):
    variables = re.findall(r"{(.*?)}", template)
    values = {}
    for var in variables:
        if var + "_range" in section:
            val_range = section[var + "_range"]
            if "date" in var or "birth" in var:
                values[var] = sample_from_range(val_range, is_date=True)
            elif any(x in var for x in ["age", "num", "total", "size"]):
                if "age" in var or "num" in var or "total" in var or "moly_size" in var:
                    values[var] = sample_from_range(val_range, is_int=True)
                else:
                    values[var] = sample_from_range(val_range)
            else:
                values[var] = sample_from_range(val_range)
        elif var in section and isinstance(section[var], list):
            candidate = random.choice(section[var])
            if "{" in candidate and "}" in candidate:
                values[var] = fill_template(section, candidate)
            else:
                values[var] = candidate
        else:
            values[var] = ""
    return template.format(**values)

# 多样化增强方法

def synonym_replace(text, synonyms):
    for k, v in synonyms.items():
        if k in text and random.random() < 0.5:
            text = text.replace(k, random.choice(v))
    return text

def add_noise(text):
    # 数字微扰
    def perturb_num(m):
        num = float(m.group(0))
        return str(round(num + random.uniform(-0.2, 0.2), 1))
    text = re.sub(r'\d+\.\d+', perturb_num, text)
    # 随机插入词
    if random.random() < 0.2:
        text = text.replace('。', random.choice(['。目前，', '。大约', '。']))
    return text

def simple_reorder(text):
    # 简单语序变换：如“左乳外上象限见肿块”→“肿块见于左乳外上象限”
    m = re.match(r'(\S+)(见|发现|查见|检测到)(\S+)', text)
    if m and random.random() < 0.5:
        return f"{m.group(3)}{m.group(2)}于{m.group(1)}"
    return text

# 主增强函数

def generate_section(section_name, n=20):
    section = TEMPLATES[section_name]
    results = []
    for _ in range(n):
        template = random.choice(section["templates"])
        values = {}
        if section_name == "基本信息":
            if "birth_range" in section:
                birth_for_age = sample_from_range(section["birth_range"], is_date=True)
                values["birth"] = birth_for_age
            elif "births" in section:
                birth_for_age = random.choice(section["births"])
                values["birth"] = birth_for_age
            else:
                birth_for_age = "1970-01-01"
                values["birth"] = birth_for_age
            birth_year = int(birth_for_age[:4])
            values["age"] = str(2024 - birth_year)
            if "genders" in section:
                values["gender"] = random.choice(section["genders"])
            else:
                values["gender"] = "女"
            for var in re.findall(r"{(.*?)}", template):
                if var not in values:
                    if var in section and isinstance(section[var], list):
                        values[var] = random.choice(section[var])
                    else:
                        values[var] = ""
            text = template.format(**values)
        else:
            text = fill_template(section, template)
        # 多样化增强
        text = synonym_replace(text, SYNONYMS)
        text = add_noise(text)
        text = simple_reorder(text)
        results.append(text)
    return results

def augment_all_sections(n=20):
    results = {}
    for section_name in TEMPLATES.keys():
        results[section_name] = generate_section(section_name, n=n)
    return results

if __name__ == "__main__":
    results = augment_all_sections(n=20)
    with open("data_augmentation/augmented_data/augmented_sections_with_noise.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("所有部分多样化增强结果已保存到 data_augmentation/augmented_data/augmented_sections_with_noise.json") 