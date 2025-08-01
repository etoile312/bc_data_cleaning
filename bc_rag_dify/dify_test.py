import requests
import json

# Dify API 端点
url = 'https://api.dify.ai/v1/chat-messages'

# 替换为你自己的 API Key（不要泄露）
api_key = 'app-tu0nSXElJlir9Z6L8XKfWdWe'

# 请求头
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

# 请求体
data = {
    "inputs": {},
    "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
    "user": "abc-123"
}

# 发送请求并处理异常
try:
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data),
        timeout=120  # 设置超时时间为 60 秒
    )

    # 检查状态码
    if response.status_code == 200:
        print("✅ 请求成功！响应内容如下：")
        print(response.json())
    else:
        print(f"⚠️ 请求失败，状态码: {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("❌ 请求超时，请检查网络是否通畅，或尝试增加 timeout 时间。")

except requests.exceptions.ProxyError as e:
    print(f"❌ 代理错误（ProxyError），可能是本地设置问题：{e}")

except requests.exceptions.ConnectionError as e:
    print(f"❌ 无法连接服务器（ConnectionError）：{e}")

except Exception as e:
    print(f"❌ 其他错误：{e}")
