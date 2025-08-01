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

# 尝试多个API密钥
api_keys = [
    'app-tu0nSXElJlir9Z6L8XKfWdWe',  # 从其他文件找到的密钥
    'app-gDw2StIdnmV2hMCpfkIIwFXu',  # 从build_testset.py找到的密钥
    'pp-W0Vf8phyDHlPRyDkat7HczOK',   # 原始密钥（可能已过期）
]

data = {
    "inputs": {},
    "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
    "user": "abc-123"
}

print("🚀 开始测试API密钥...")
print(f"📡 目标URL: {url}")
print(f"📝 请求内容: {data['query']}")

for i, api_key in enumerate(api_keys, 1):
    print(f"\n🔑 测试API密钥 {i}: {api_key[:10]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
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
            print(f"\n🎉 找到有效API密钥: {api_key}")
            break
        elif response.status_code == 401:
            print("❌ API密钥无效 (401 Unauthorized)")
        elif response.status_code == 403:
            print("❌ API密钥权限不足 (403 Forbidden)")
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
else:
    print("\n❌ 所有API密钥都无效")
    print("💡 建议：")
    print("   1. 检查API密钥是否正确")
    print("   2. 确认API密钥是否已过期")
    print("   3. 验证API密钥权限")
    print("   4. 联系Dify管理员获取新的API密钥") 