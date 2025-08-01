from field_parser import FieldRuleParser
from field_sampler import FieldSampler
from segment_groups import SEGMENT_GROUPS
import json
import os
import pandas as pd

RULE_PATH = 'rules/breast_cancer_rules.json'
DRUG_EXCEL_PATH = 'rules/drug_data.xlsx' # Excel文件路径
OUT_DIR = 'data/segments'
N = 100  # 每个段落组采样数量

def load_drug_data(path):
    """从Excel加载药物数据"""
    try:
        df = pd.read_excel(path, usecols=[1, 2]) # 只读取B,C两列
        df.columns = ['方案名称', '关联药物名称']
        df.dropna(inplace=True)
        print(f"✅ 成功从 {path} 加载 {len(df)} 条药物方案。")
        return df
    except FileNotFoundError:
        print(f"🚨 [警告] 未找到药物Excel文件: {path}。'药品信息'字段将使用默认值。")
    except Exception as e:
        print(f"🚨 [错误] 加载药物Excel文件失败: {e}")
    return None

if __name__ == '__main__':
    print("脚本已启动")
    parser = FieldRuleParser(RULE_PATH)
    field_defs = parser.get_field_defs()
    logic_rules = parser.get_logic_rules() # 获取逻辑规则
    drug_data = load_drug_data(DRUG_EXCEL_PATH) # 加载药物数据

    # 将逻辑规则和药物数据传入采样器
    sampler = FieldSampler(field_defs, logic_rules, drug_data)
    os.makedirs(OUT_DIR, exist_ok=True)

    for group_name, fields in SEGMENT_GROUPS.items():
        seg_samples = sampler.sample_segment(fields, n=N, group_name=group_name)
        out_path = os.path.join(OUT_DIR, f"{group_name}_pool.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(seg_samples, f, ensure_ascii=False, indent=2)
        print(f"已生成段落组池: {group_name}_pool.json, 数量: {len(seg_samples)}")

