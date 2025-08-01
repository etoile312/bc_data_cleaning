import os
import json
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# 路径配置
TESTSET_DIR = 'qa_files'  # 输入问答对目录
SAVE_DIR = 'qa_scores'    # 输出评分文件目录
os.makedirs(SAVE_DIR, exist_ok=True)

# ChatFlow（AI问答）配置
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe'
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

# Score ChatFlow 配置
SCORE_CHATFLOW_API_KEY = 'Bearer app-W0Vf8phyDHlPRyDkat7HczOK'
SCORE_CHATFLOW_HEADERS = {
    'Authorization': SCORE_CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

# 提示词模板
PROMPT_TEMPLATE = (
    "你是一个医学问答评分专家。现在有两个回答：\n\n"
    "- 回答1（AI生成）：{ai_answer}\n"
    "- 回答2（参考答案）：{ref_answer}\n\n"
    "请你从以下维度评估“回答1”与“回答2”之间的语义一致性和专业质量：\n\n"
    "1. 医学准确性（权重 30%）\n"
    "2. 回答完整性（权重 25%）\n"
    "3. 专业性与逻辑性（权重 15%）\n"
    "4. 表达清晰度与通俗性（权重 15%）\n"
    "5. 与参考答案的相关性（权重 15%）\n\n"
    "请输出每一部分的得分（0~1），并且综合以上维度打出一个最终得分（0~1），仅输出保留两位小数的数字即可，例如：\n"
    "医学准确性: 0.90\n"
    "回答完整性: 0.80\n"
    "专业性与逻辑性: 0.85\n"
    "表达清晰度与通俗性: 0.95\n"
    "与参考答案的相关性: 0.75\n"
    "最终得分: 0.84\n"
    "不要输出其他内容。"
)

SCORE_KEYS = [
    "医学准确性",
    "回答完整性",
    "专业性与逻辑性",
    "表达清晰度与通俗性",
    "与参考答案的相关性",
    "最终得分"
]

def process_file(file):
    if not file.endswith('.json'):
        return None
    try:
        with open(os.path.join(TESTSET_DIR, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        question = data['question']
        ref_answer = data['answer']

        # 第一步：生成 AI 回答
        chat_payload = {
            "inputs": {},
            "query": question,
            "user": "test-user"
        }
        chat_resp = requests.post(CHATFLOW_API_URL, headers=CHATFLOW_HEADERS, json=chat_payload)
        ai_answer = chat_resp.json().get("answer", "").strip() if chat_resp.status_code == 200 else ""

        # 第二步：评分
        prompt = PROMPT_TEMPLATE.format(ai_answer=ai_answer, ref_answer=ref_answer)
        score_payload = {
            "inputs": {},
            "query": prompt,
            "response_mode": "blocking",
            "user": "scoring-agent"
        }
        score_resp = requests.post(CHATFLOW_API_URL, headers=SCORE_CHATFLOW_HEADERS, json=score_payload)

        if score_resp.status_code != 200:
            print(f"❌ Score ChatFlow 请求失败: {file}, 状态码: {score_resp.status_code}")
            return None

        answer_text = score_resp.json().get("answer", "")
        score_dict = {}
        for key in SCORE_KEYS:
            match = re.search(fr"{key}[:：]?\s*([0-1]\.\d+)", answer_text)
            if match:
                score = float(match.group(1))
            else:
                print(f"⚠️ 缺失得分：{key} in {file}")
                score = 0.0
            score_dict[key] = round(score, 2)

        # 保存每个评分结果到单独文件
        score_data = {
            "question": question,
            "ai_answer": ai_answer,
            "ref_answer": ref_answer,
            "scores": score_dict
        }
        save_path = os.path.join(SAVE_DIR, file.replace('.json', '_score.json'))
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(score_data, f, ensure_ascii=False, indent=2)

        # 控制台打印
        print(f"📌 {file}")
        print(f"Q: {question}")
        for k, v in score_dict.items():
            print(f"{k}: {v:.2f}")
        print("-" * 60)

        return score_dict
    except Exception as e:
        print(f"❌ 处理文件 {file} 时出错: {e}")
        return None

def main():
    files = sorted(os.listdir(TESTSET_DIR))
    # ====== 分批处理参数，手动修改 ======
    start_idx = 1   # 包含
    end_idx = 2    # 不包含（如0-10表示处理前10条）
    # ===================================
    batch_files = files[start_idx:end_idx]
    sum_scores = {k: 0.0 for k in SCORE_KEYS}
    count = 0
    results = []
    # 线程数可根据实际情况调整
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in batch_files if file.endswith('.json')}
        for future in as_completed(future_to_file):
            score_dict = future.result()
            if score_dict:
                for k in SCORE_KEYS:
                    sum_scores[k] += score_dict[k]
                count += 1
                results.append(score_dict)
    # 输出平均得分
    if count > 0:
        print("\n📊 平均得分")
        for k in SCORE_KEYS:
            avg = sum_scores[k] / count
            print(f"{k}: {avg:.2f}")
    else:
        print("⚠️ 未处理任何问答。")

if __name__ == "__main__":
    main()
