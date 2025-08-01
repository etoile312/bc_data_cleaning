import requests
import json

# 验证数据集
validation_data = [
    {
        "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
        "ground_truth": "建议进行温和的肩部活动，避免剧烈运动，可参考术后康复第3阶段训练方案。"
    },
    {
        "query": "乳腺癌术后第一个月能不能举重物？",
        "ground_truth": "不建议提举重物，应以恢复为主，避免伤口裂开和淋巴水肿。"
    }
]

# Dify API 配置
url = 'https://api.dify.ai/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe',
    'Content-Type': 'application/json',
}

# 简单打分函数（可以替换为 BLEU/ROUGE/自定义规则）
def score_response(response_text, ground_truth):
    matched_keywords = [kw for kw in ground_truth.split("，") if kw.strip() in response_text]
    return len(matched_keywords) / max(len(ground_truth.split("，")), 1)

# 统计总分
total_score = 0

for item in validation_data:
    data = {
        "inputs": {},  # 如果你没有定义任何 inputs 变量，可以留空，或删掉这行   
        "query": item["query"],
        "user": "abc-123"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()

    # 获取模型回复
    ai_reply = result.get("answer", "")
    print(f"\nQ: {item['query']}\nAI答复: {ai_reply}\n参考答案: {item['ground_truth']}")

    # 简单打分
    score = score_response(ai_reply, item["ground_truth"])
    print(f"得分: {score:.2f}")
    total_score += score

# 平均得分
average_score = total_score / len(validation_data)
print(f"\n📊 平均得分: {average_score:.2f}")
