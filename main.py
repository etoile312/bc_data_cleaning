import os
import json
import requests

# ==== config ====
LLM_PROVIDER = "doubao"  # 可选: doubao, openai, qwen, baidu 等
LLM_API_URL = "https://api.doubao.com/v1/chat/completions"  # 豆包API地址
LLM_API_KEY = "f53e45e9-7cee-4760-afe6-29ce90682f21"  # API密钥
MODEL_NAME = "doubao-lite-32k"  # 模型名称
PROMPT_DIR = "prompts"
STRUCTURED_DATA_DIR = "data/structured"
AUGMENTED_DATA_DIR = "data/augmented"
N_VARIANTS = 3  # 每字段生成几个变体

# ==== utils ====
def call_llm(prompt, model=MODEL_NAME, temperature=0.8):
    """
    通用大模型API适配器。只需修改上方配置区即可切换大模型。
    """
    url = LLM_API_URL
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 512
    }
    # 临时调试，跳过 SSL 校验
    response = requests.post(url, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    # 兼容不同大模型的返回结构
    data = response.json()
    if "choices" in data and "message" in data["choices"][0]:
        return data["choices"][0]["message"]["content"].strip()
    elif "result" in data:  # 例如部分国产大模型
        return data["result"].strip()
    else:
        raise RuntimeError(f"未知的LLM返回结构: {data}")

def load_prompt_template(field_name):
    with open(f"prompts/{field_name}.txt", "r", encoding="utf-8") as f:
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
            enhanced[field] = [content]
        else:
            enhanced[field] = enhance_field(field, content)
    return enhanced

# ==== main ====
def main():
    input_path = os.path.join(STRUCTURED_DATA_DIR, "sample_01.json")
    output_path = os.path.join(AUGMENTED_DATA_DIR, "sample_01.json")
    with open(input_path, "r", encoding="utf-8") as f:
        record = json.load(f)
    # 只增强 basic_info 字段，其它字段保持原样
    enhanced = enhance_record(record, fields=["basic_info"])
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enhanced, f, ensure_ascii=False, indent=2)
    print(f"Enhanced: sample_01.json (only basic_info)")

if __name__ == "__main__":
    main() 