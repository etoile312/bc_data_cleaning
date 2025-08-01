import json
import os
import time

import requests

url = 'https://api.dify.ai/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-gDw2StIdnmV2hMCpfkIIwFXu',
    'Content-Type': 'application/json',
}


SAVE_DIR = "qa_files"  # 保存文件的目录
NUM_QA = 20

# 3. 创建保存目录
os.makedirs(SAVE_DIR, exist_ok=True)

# 4. 循环生成问答对
for i in range(11, NUM_QA + 1):
    prompt = "请从你掌握的乳腺癌康复知识中，生成一个专业的问题及其标准答案，格式为：\n问题：...\n答案：..."
    
    data = {
        "inputs": {},  # 若你的 ChatFlow 不要求 inputs，可为空
        "query": prompt,
        "response_mode": "blocking",  # 阻塞模式返回完整内容
        "user": f"qa_gen_{i}"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()

        answer_text = result.get("answer", "")

        # 提取问题和答案
        if "问题：" in answer_text and "答案：" in answer_text:
            question = answer_text.split("问题：")[1].split("答案：")[0].strip()
            answer = answer_text.split("答案：")[1].strip()

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


            print(f"✅ 已生成并保存：{file_path}")
        else:
            print(f"⚠️ 第{i}条回复格式错误：{answer_text}")

        time.sleep(1)  # 控制请求频率，避免 Dify 拒绝服务

    except Exception as e:
        print(f"❌ 第{i}条请求出错：{e}")
