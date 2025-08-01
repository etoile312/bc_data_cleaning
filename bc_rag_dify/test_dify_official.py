import os
# 清理代理环境变量，避免代理连接问题
for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
    os.environ.pop(var, None)

import requests
import json
import time
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://api.dify.ai/v1/chat-messages'

# 测试不同的密钥格式
test_keys = [
    # API Keys (客户端)
    'app-W0Vf8phyDHlPRyDkat7HczOK',
    'app-tu0nSXElJlir9Z6L8XKfWdWe',
    'app-gDw2StIdnmV2hMCpfkIIwFXu',
    # Secret Keys (服务端) - 如果你有的话
    # 'sk-xxxxxxxxxxxxxxxxxxxxxxxx',
]

data = {
    "inputs": {},
    "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
    "response_mode": "blocking",  # 使用blocking模式而不是streaming
    "user": "abc-123"
}

print("🚀 按照Dify官方文档格式测试...")
print(f"📡 目标URL: {url}")
print(f"📝 请求内容: {data['query']}")

for i, key in enumerate(test_keys, 1):
    print(f"\n🔑 测试密钥 {i}: {key[:10]}...")
    
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120, verify=False)
        end_time = time.time()
        
        print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 请求成功！")
            result = response.json()
            print("📄 响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"\n🎉 找到有效密钥: {key}")
            break
        elif response.status_code == 401:
            print("❌ 密钥无效 (401 Unauthorized)")
            print(f"📄 错误详情: {response.text}")
        elif response.status_code == 403:
            print("❌ 密钥权限不足 (403 Forbidden)")
            print(f"📄 错误详情: {response.text}")
        else:
            print(f"⚠️ 其他错误，状态码: {response.status_code}")
            print(f"📄 错误响应: {response.text}")
            
    except requests.exceptions.ProxyError as e:
        print(f"❌ 代理错误: {e}")
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时 (120秒)")
        
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL证书错误: {e}")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        print(f"💡 错误类型: {type(e).__name__}")

print("\n" + "="*60)
print("💡 如果所有密钥都失败，请检查：")
print("   1. 确认使用的是正确的密钥类型（API Key vs Secret Key）")
print("   2. 检查Dify应用配置是否正确")
print("   3. 确认API端点URL是否正确")
print("   4. 检查网络连接和代理设置")
print("="*60) 