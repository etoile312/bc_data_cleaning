import json
import os
import time
import requests
import re

# ChatFlow API 配置
url = 'https://api.dify.ai/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-gDw2StIdnmV2hMCpfkIIwFXu',  # 替换为你的 API 密钥
    'Content-Type': 'application/json',
}

# 10 条乳腺癌相关问题
questions = [
    "我今年65岁，术后第5天，感觉胳膊有点肿胀，这是正常的吗？需要做些什么缓解？",
    "术后第10天可以洗澡吗？伤口需要注意什么？",
    "乳腺癌术后第7天可以开始抬胳膊练习了吗？有什么动作建议？",
    "术后第3天肩膀感觉僵硬，是不是不能动？还是要多动动？",
    "我60岁，刚做完保乳手术，现在该怎么做功能锻炼比较安全？",
    "术后第15天出现了腋窝处轻微疼痛，是正常恢复的一部分吗？",
    "切除淋巴结后手臂会一直肿胀吗？我该如何预防？",
    "乳腺癌术后出现轻微发热，需要看医生吗？",
    "我55岁，术后出现淋巴液渗出，用压迫敷料就行了吗？",
    "术后半个月，手术侧手指有点发麻，这是淋巴水肿的表现吗？"
]

SAVE_DIR = "qa_files"
os.makedirs(SAVE_DIR, exist_ok=True)

def clean_think_content(text: str) -> str:
    # 去掉 <think> 标签包裹的部分
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # 去掉 think 标签之外的内容，例如 Q: 和 A: 前的分析
    text = re.split(r"[Q：|Q:]", text)[-1] if "Q" in text else text
    return text.strip()

for i, question in enumerate(questions, start=1):
    data = {
        "inputs": {},
        "query": question,
        "response_mode": "blocking",
        "user": f"qa_gen_{i}"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()

        raw_answer = result.get("answer", "").strip()
        cleaned = clean_think_content(raw_answer)

        # 如果包含 A: 或 答案： 等，提取后半部分
        if "A:" in cleaned:
            answer = cleaned.split("A:")[-1].strip()
        elif "答案：" in cleaned:
            answer = cleaned.split("答案：")[-1].strip()
        else:
            answer = cleaned

        qa_pair = {
            "question": question,
            "answer": answer
        }

        file_path = os.path.join(SAVE_DIR, f"qa_{i:02d}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(qa_pair, f, ensure_ascii=False, indent=2)

        print(f"\n第 {i} 条 QA：")
        print(f"问题：{question}")
        print(f"答案：{answer}")
        print(f"✅ 已保存到：{file_path}")

        time.sleep(1)

    except Exception as e:
        print(f"❌ 第 {i} 条请求失败：{e}")
