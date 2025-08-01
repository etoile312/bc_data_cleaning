import os
import json
import requests

# ==== config ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-9GZhvKlhFxAnh0ZfObB8DYAP'
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}
PROMPT_DIR = os.path.join(BASE_DIR, "prompts")
STRUCTURED_DATA_DIR = os.path.join(BASE_DIR, "data/structured")
AUGMENTED_DATA_DIR = os.path.join(BASE_DIR, "data/augmented")
N_VARIANTS = 2  # 每字段生成几个变体

# ==== utils ====
def call_llm(prompt, temperature=0.8):
    url_local_model = "http://192.168.19.211:8000/v1/model/single_report"
    response = requests.post(url_local_model, json={"report": prompt})
    if response.status_code == 200:
        res = response.json()
        return res.get("llm_ret")
    else:
        raise RuntimeError(f"本地模型API请求失败: {response.status_code}, {response.text}")

def load_prompt_template(field_name):
    with open(os.path.join(PROMPT_DIR, f"{field_name}.txt"), "r", encoding="utf-8") as f:
        return f.read()

# ==== enhancer ====
def enhance_field(field_name, field_content, n_variants=N_VARIANTS):
    prompt_template = load_prompt_template(field_name)
    variants = []
    for i in range(n_variants):
        prompt = prompt_template.format(content=field_content)
        variant = call_llm(prompt)
        variants.append(variant)
    return variants

def enhance_record(structured_record, fields=None):
    enhanced = {}
    for field, content in structured_record.items():
        if fields and field not in fields:
            continue  # 跳过未增强字段
        enhanced[field] = enhance_field(field, content)
    return enhanced

# ==== main ====
def main():
    for fname in os.listdir(STRUCTURED_DATA_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(STRUCTURED_DATA_DIR, fname), "r", encoding="utf-8") as f:
            record = json.load(f)
        # 只增强指定字段
        enhanced = enhance_record(record, fields=["diagnosis"])
        # 只保存本次增强的字段结果文件
        for field, variants in enhanced.items():
            out_path = os.path.join(AUGMENTED_DATA_DIR, f"{field}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(variants, f, ensure_ascii=False, indent=2)
            print(f"Enhanced: {field} -> {out_path}")

if __name__ == "__main__":
    main() 