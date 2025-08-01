import os
import json
import requests

# 路径配置
TESTSET_DIR = 'qa_files'  # 替换为你的 JSON 测试集目录路径

# ChatFlow 模型配置（用于生成 AI 答复）
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe'  # 替换为你的 ChatFlow API Key
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

# 评分 Agent 模型配置（用于打分）
SCORE_CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
SCORE_CHATFLOW_API_KEY = 'Bearer app-W0Vf8phyDHlPRyDkat7HczOK'
SCORE_CHATFLOW_HEADERS = {
    'Authorization': SCORE_CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

# 遍历测试集文件夹中的所有 JSON 文件
files = sorted(os.listdir(TESTSET_DIR))
total_score = 0
count = 0

for file in files:
    if file.endswith('.json'):
        path = os.path.join(TESTSET_DIR, file)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        question = data['question']
        reference = data['answer']

        # 1. 向 ChatFlow 提交问题，生成 AI 答案
        chat_payload = {
            "inputs": {},
            "query": question,
            "user": "test-user"
        }
        chat_response = requests.post(CHATFLOW_API_URL, headers=CHATFLOW_HEADERS, json=chat_payload)

        if chat_response.status_code == 200:
            chat_result = chat_response.json()
            ai_answer = chat_result.get("answer", "").strip()
        else:
            ai_answer = ""
            print(f"❌ ChatFlow 请求失败: {file}, 状态码: {chat_response.status_code}")

        # 2. 使用评分 Agent 评估 AI 答案和参考答案的质量
        score_query = (
            f"请评估以下两个医学问答在内容、准确性、表达等方面的相似程度，并给出评分。\n\n"
            f"【AI回答】：{ai_answer}\n"
            f"【参考答案】：{reference}\n\n"
            f"请根据提示词中提到的评分维度给出0到1之间的得分，保留两位小数，仅输出得分，不需要解释。"
        )

        score_payload = {
            "inputs": {},
            "query": score_query,
            "response_mode": "blocking",
            "user": "scoring-agent"
        }

        score_response = requests.post(SCORE_CHATFLOW_API_URL, headers=SCORE_CHATFLOW_HEADERS, json=score_payload)

        if score_response.status_code == 200:
            score_result = score_response.json()
            score_text = score_result.get("answer", "").strip()
            try:
                score = float(score_text)
            except ValueError:
                print(f"⚠️ 评分格式错误: {score_text}")
                score = 0.0
        else:
            score = 0.0
            print(f"❌ Score ChatFlow 请求失败: 状态码: {score_response.status_code}")  
        # 打印每个问答的评分结果
        print(f"Q: {question}")
        print(f"AI答复: {ai_answer}")
        print(f"参考答案: {reference}")
        print(f"得分: {score:.2f}")
        print("-" * 60)

        total_score += score
        count += 1

# 3. 打印平均得分
average_score = total_score / count if count > 0 else 0
print(f"\n📊 总共测试 {count} 条，平均得分: {average_score:.2f}")
