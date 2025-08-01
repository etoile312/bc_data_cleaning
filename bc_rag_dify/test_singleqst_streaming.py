import os
# 清理代理环境变量，避免代理连接问题
for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
    os.environ.pop(var, None)

import requests
import json
import time

url = 'https://api.dify.ai/v1/chat-messages'
headers = {
    'Authorization': 'Bearer app-W0Vf8phyDHlPRyDkat7HczOK',
    'Content-Type': 'application/json',
}

data = {
    "inputs": {},
    "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
    "response_mode": "streaming",  # 使用streaming模式
    "user": "abc-123"
}

print("🚀 开始发送请求...")
print(f"📡 目标URL: {url}")
print(f"📝 请求内容: {data['query']}")
print(f"🔧 响应模式: {data['response_mode']}")

try:
    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120, stream=True)
    end_time = time.time()
    
    print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 请求成功！")
        print("📄 流式响应内容:")
        
        # 处理流式响应
        for line in response.iter_lines():
            if line:
                try:
                    # 解析SSE格式的数据
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                        if data_str.strip() == '[DONE]':
                            print("🏁 流式响应结束")
                            break
                        elif data_str.strip():
                            try:
                                json_data = json.loads(data_str)
                                print(f"📦 数据块: {json.dumps(json_data, ensure_ascii=False)}")
                            except json.JSONDecodeError:
                                print(f"📝 原始数据: {data_str}")
                except Exception as e:
                    print(f"⚠️ 解析流数据时出错: {e}")
    else:
        print(f"⚠️ 请求失败，状态码: {response.status_code}")
        print(f"📄 错误响应: {response.text}")
        
except requests.exceptions.ProxyError as e:
    print(f"❌ 代理错误: {e}")
    print("💡 建议：检查代理设置或网络配置")
    
except requests.exceptions.Timeout:
    print("❌ 请求超时 (120秒)")
    print("💡 建议：检查网络连接或增加超时时间")
    
except requests.exceptions.ConnectionError as e:
    print(f"❌ 连接错误: {e}")
    print("💡 建议：检查网络连接")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")
    print(f"💡 错误类型: {type(e).__name__}") 