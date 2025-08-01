# -*- coding: utf-8 -*-
import re
import random
import json
from datetime import datetime, timedelta
from copy import deepcopy

# 工具函数：区间采样

def sample_from_range(val_range, is_int=False, is_date=False):
    # 类型转换
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

# 读取模板库
with open("data_augmentation/augmentation_templates.json", "r", encoding="utf-8") as f:
    TEMPLATES = json.load(f)

# 通用增强函数

def fill_template(section, template):
    variables = re.findall(r"{(.*?)}", template)
    values = {}
    for var in variables:
        # 递归处理嵌套模板
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
            # 如果是模板字符串，递归填充
            if "{" in candidate and "}" in candidate:
                values[var] = fill_template(section, candidate)
            else:
                values[var] = candidate
        else:
            values[var] = ""
    return template.format(**values)

def generate_section(section_name, n=20):
    section = TEMPLATES[section_name]
    results = []
    for _ in range(n):
        template = random.choice(section["templates"])
        # 特殊处理：基本信息的年龄依赖出生日期和性别
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
            # 只填充模板中出现的变量
            for var in re.findall(r"{(.*?)}", template):
                if var not in values:
                    if var in section and isinstance(section[var], list):
                        values[var] = random.choice(section[var])
                    else:
                        values[var] = ""
            results.append(template.format(**values))
        else:
            results.append(fill_template(section, template))
    return results

# 主函数：对所有部分增强

def augment_all_sections(n=20):
    results = {}
    for section_name in TEMPLATES.keys():
        results[section_name] = generate_section(section_name, n=n)
    return results

if __name__ == "__main__":
    results = augment_all_sections(n=20)
    with open("data_augmentation/augmented_data/augmented_sections.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("所有部分增强结果已保存到 data_augmentation/augmented_data/augmented_sections.json") 