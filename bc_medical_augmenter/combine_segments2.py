import json
import random
import os

SEGMENT_DIR = 'data/segments'
OUT_FILE = 'data/combined_cases.json'
N = 100  # 生成样本数

# 全部段落组配置（固定与可选）
SEGMENT_GROUPS = {
    "basic_info": ["年龄", "绝经状态", "PS"],
    "stage_and_metastasis": ["IV期", "M1分期", "远处转移", "转移位置", "转移或复发", "复发"],
    "surgery": ["是否保乳", "已行根治手术", "可再次手术", "切缘<1mm", "切缘阳性", "是否腋窝清扫", "腋窝淋巴结是否有阳性", "腋窝淋巴结阳性个数(术前)", "腋窝淋巴结阳性个数(术后)", "根治手术时间"],
    "pathology": ["组织学分级", "ER%", "PR%", "Her-2免疫组化", "FISH", "Ki-67%"],
    "tumor_size": [
        "肿块大小CM(术前)", "肿块大小CM(术后)",
        "肿块大小CM(CT)", "肿块大小CM(MRI)", "肿块大小CM(B超)", "肿块大小CM(查体)"
    ],
    "treatment": ["药品信息", "免疫禁忌", "有新辅助治疗", "新辅助治疗使用免疫", "新辅助治疗使用双靶"],
    "response": ["pCR", "ypT0N0", "MP评分"],
    "prognosis": ["DFS（月）", "复发时间"],
    "risk": ["基因高风险"],
    "staging": ["cTNM", "pTNM", "ypTNM"]
}

REQUIRED_SEGMENTS = ["basic_info", "stage_and_metastasis", "surgery", "tumor_size", "prognosis"]
OPTIONAL_SEGMENTS = [k for k in SEGMENT_GROUPS if k not in REQUIRED_SEGMENTS]

# 读取所有段落池
segment_pools = {}
for group in SEGMENT_GROUPS:
    fname = f'{group}_pool.json'
    path = os.path.join(SEGMENT_DIR, fname)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            segment_pools[group] = json.load(f)
    else:
        print(f"[警告] 未找到段落池: {fname}")

# 读取字段全集和默认值
with open('rules/breast_cancer_rules.json', encoding='utf-8') as f:
    rules = json.load(f)
    all_fields = list(rules['fields'].keys())
    field_defaults = {k: v.get('default', '') for k, v in rules['fields'].items()}

def logic_check_and_fix(sample):
    # 段落间规则修正
    # 1. 年龄、绝经状态一致性
    age = sample.get('年龄', '')
    if age:
        for k in sample:
            if k == '年龄':
                continue
            if isinstance(sample[k], dict) and '年龄' in sample[k]:
                sample[k]['年龄'] = age
    # 2. 根治手术时间一致性
    surgery_time = sample.get('根治手术时间', '')
    if surgery_time:
        for k in sample:
            if k == '根治手术时间':
                continue
            if isinstance(sample[k], dict) and '根治手术时间' in sample[k]:
                sample[k]['根治手术时间'] = surgery_time
    # 3. 复发时间、转移位置一致性
    recur_time = sample.get('复发时间', '')
    transfer_loc = sample.get('转移位置', '')
    if recur_time:
        for k in sample:
            if k == '复发时间':
                continue
            if isinstance(sample[k], dict) and '复发时间' in sample[k]:
                sample[k]['复发时间'] = recur_time
    if transfer_loc:
        for k in sample:
            if k == '转移位置':
                continue
            if isinstance(sample[k], dict) and '转移位置' in sample[k]:
                sample[k]['转移位置'] = transfer_loc
    # 4. 药品信息一致性
    drug_info = sample.get('药品信息', [])
    if drug_info:
        for k in sample:
            if k == '药品信息':
                continue
            if isinstance(sample[k], dict) and '药品信息' in sample[k]:
                sample[k]['药品信息'] = drug_info
    # 5. TNM分期与肿块/淋巴/转移等字段一致性
    # ...可补充更复杂的全局推断...
    return sample

def combine_one_case():
    sample = {}
    selected_fields = set()

    # 随机选择组合模式
    mode = random.choice(['standard', 'random_groups'])

    if mode == 'standard':
        # 模式A: 固定+可选
        # 固定必选段
        for group in REQUIRED_SEGMENTS:
            pool = segment_pools.get(group, [])
            if pool:
                entry = random.choice(pool)
                sample.update(entry)
        
        # 随机选 1~5 个可选段
        num_optional = random.randint(1, len(OPTIONAL_SEGMENTS))
        optional_groups_to_add = random.sample(OPTIONAL_SEGMENTS, k=num_optional)
        for group in optional_groups_to_add:
            pool = segment_pools.get(group, [])
            if pool:
                sample.update(random.choice(pool))
    
    else: # mode == 'random_groups'
        # 模式B: 从所有组中随机选1-10个
        all_groups = list(SEGMENT_GROUPS.keys())
        num_to_select = random.randint(1, 4)
        groups_to_combine = random.sample(all_groups, k=num_to_select)
        
        for group in groups_to_combine:
            pool = segment_pools.get(group, [])
            if pool:
                sample.update(random.choice(pool))

    # ---- 统一的后续处理 ----
    
    # 特殊处理 tumor_size 组，确保只有一个影像学大小
    ts_fields = ["肿块大小CM(CT)", "肿块大小CM(MRI)", "肿块大小CM(B超)", "肿块大小CM(查体)"]
    present_ts_fields = [f for f in ts_fields if f in sample]
    if len(present_ts_fields) > 1:
        field_to_keep = random.choice(present_ts_fields)
        for f in present_ts_fields:
            if f != field_to_keep:
                del sample[f]

    # 最后应用逻辑修正
    return logic_check_and_fix(sample)


# 批量生成
cases = [combine_one_case() for _ in range(N)]
with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成 {N} 条符合逻辑的病历样本: {OUT_FILE}")
