import json
import os
import time
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# ChatFlow API 配置
url = 'https://api.dify.ai/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-gDw2StIdnmV2hMCpfkIIwFXu',  # 替换为你的 API 密钥
    'Content-Type': 'application/json',
}

# 50 条乳腺癌相关问题
questions = [
    "我今年62岁，术后第7天，乳房有些胀痛，是否正常？",
    "乳腺癌术后第10天能做有氧运动吗？有哪些适合的运动项目？",
    "术后第5天伤口有渗液，应该怎么办？",
    "术后肩部活动受限，是否需要做物理治疗？",
    "我刚做完乳腺癌手术，什么时候可以开始锻炼胸部肌肉？",
    "术后出现胸部明显肿胀，是否需要就医？",
    "术后第14天，乳房周围有压痛，是否需要担心？",
    "我59岁，乳腺癌术后能不能去游泳？有何注意事项？",
    "术后是否可以进行按摩？会影响恢复吗？",
    "乳腺癌术后，如何避免淋巴水肿？",
    "我刚做了乳腺癌手术，什么时候可以开车？",
    "术后伤口肿胀是正常的吗？如何加速恢复？",
    "乳腺癌手术后，是否需要定期复查，多久复查一次？",
    "乳腺癌术后有什么饮食建议？需要避免哪些食物？",
    "术后出现轻微发热，有时会持续几天，这正常吗？",
    "乳腺癌术后疼痛需要服药缓解吗？哪些药物安全？",
    "我正在接受乳腺癌手术后治疗，是否能继续工作？",
    "术后如何预防乳腺癌复发？有哪些生活习惯需要调整？",
    "术后是否可以使用护肤品？需要特别注意什么成分？",
    "乳腺癌术后胸部出现硬块，是否需要担心？",
    "术后恢复期可以进行哪些类型的运动来保持体形？",
    "我45岁，乳腺癌术后是否可以进行瑜伽练习？",
    "术后10天出现了手臂的轻微麻木感，应该怎么办？",
    "乳腺癌术后多久能恢复正常的性生活？",
    "术后需要控制体重吗？怎样保持健康体重？",
    "乳腺癌术后，伤口愈合得很慢，是否需要就医？",
    "术后是否可以旅行？有什么需要注意的事项吗？",
    "乳腺癌术后需要做乳腺检查，多久一次比较合适？",
    "术后手臂肿胀是常见的吗？如何缓解？",
    "乳腺癌术后胸部硬块是复发的迹象吗？",
    "乳腺癌术后需要避免哪些运动或活动？",
    "术后伤口愈合不好，可能是什么原因？如何促进愈合？",
    "乳腺癌术后，如何应对术后情绪低落？",
    "乳腺癌术后，什么时候可以恢复正常饮食？",
    "我65岁，乳腺癌术后多久能开始恢复正常作息？",
    "乳腺癌术后出现焦虑情绪，如何调节心态？",
    "乳腺癌术后有哪些理疗或康复建议？",
    "乳腺癌术后，哪些身体症状应该及时就医？",
    "术后第30天，胸部疼痛是否正常？",
    "乳腺癌术后，伤口瘢痕增生怎么处理？",
    "乳腺癌术后出现发热，是否与治疗相关？",
    "术后何时可以开始进行身体检查？需要哪些项目？",
    "乳腺癌术后如何避免淋巴水肿的发生？",
    "乳腺癌术后是否可以晒太阳？有何风险？",
    "乳腺癌术后，是否有必要接受心理疏导？",
    "术后需要避免哪些食物以免影响恢复？",
    "乳腺癌术后可以做重体力劳动吗？需要注意什么？",
    "乳腺癌术后什么时候可以开始进行抗阻训练？",
    "乳腺癌术后体重增加，应该如何调整饮食和运动？",
    "术后如何通过饮食改善身体的免疫力？",
    "乳腺癌术后出现了淋巴水肿，如何治疗？",
    "术后能不能继续跑步？有哪些运动禁忌？",
    "乳腺癌术后如何评估是否需要化疗或放疗？",
    "乳腺癌术后，是否有复发的迹象？如何监测？",
    "术后需要关注哪些指标，如何做健康监测？",
    "乳腺癌术后，恢复过程中是否要避免感冒？"
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
