import requests
import json

# 创建一个不使用环境代理的 session
session = requests.Session()
session.trust_env = False  # 关键一步，忽略系统代理设置

url = 'https://api.dify.ai/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe',
    'Content-Type': 'application/json',
}

data = {
    "inputs": {},
    "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
    "user": "abc-123"
}

response = session.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)
