import os
import requests
import json
import time
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_proxy_env():
    """清理代理环境变量"""
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(var, None)
    print("✅ 代理环境变量已清理")

def test_basic_connectivity():
    """测试基本网络连接"""
    print("\n🔍 测试基本网络连接...")
    try:
        response = requests.get("https://httpbin.org/get", timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ 基本网络连接正常")
            return True
        else:
            print(f"⚠️ 基本连接测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 基本连接测试失败: {e}")
        return False

def test_dns_resolution():
    """测试DNS解析"""
    print("\n🔍 测试DNS解析...")
    try:
        import socket
        socket.gethostbyname("api.dify.ai")
        print("✅ DNS解析正常")
        return True
    except Exception as e:
        print(f"❌ DNS解析失败: {e}")
        return False

def test_api_endpoint():
    """测试API端点可访问性"""
    print("\n🔍 测试API端点...")
    try:
        response = requests.get("https://api.dify.ai", timeout=10, verify=False)
        print(f"✅ API端点可访问，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def create_robust_session():
    """创建健壮的session"""
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 确保不使用代理
    session.proxies = {
        'http': '',
        'https': ''
    }
    
    return session

def test_api_with_different_methods():
    """使用不同方法测试API"""
    print("\n🤖 测试Dify API...")
    
    url = 'https://api.dify.ai/v1/chat-messages'
    headers = {
        'Authorization': 'Bearer pp-W0Vf8phyDHlPRyDkat7HczOK',
        'Content-Type': 'application/json',
    }
    
    data = {
        "inputs": {},
        "query": "你好，我目前67岁，术后20天，今天的乳腺癌康复训练建议是什么？",
        "user": "abc-123"
    }
    
    # 方法1: 使用session
    print("\n📡 方法1: 使用session")
    try:
        session = create_robust_session()
        start_time = time.time()
        response = session.post(url, headers=headers, json=data, timeout=120, verify=False)
        end_time = time.time()
        
        print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 方法1成功！")
            return True
        else:
            print(f"⚠️ 方法1失败: {response.text}")
    except Exception as e:
        print(f"❌ 方法1错误: {e}")
    
    # 方法2: 直接使用requests
    print("\n📡 方法2: 直接使用requests")
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=120, verify=False)
        end_time = time.time()
        
        print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 方法2成功！")
            return True
        else:
            print(f"⚠️ 方法2失败: {response.text}")
    except Exception as e:
        print(f"❌ 方法2错误: {e}")
    
    # 方法3: 使用data参数
    print("\n📡 方法3: 使用data参数")
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120, verify=False)
        end_time = time.time()
        
        print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 方法3成功！")
            return True
        else:
            print(f"⚠️ 方法3失败: {response.text}")
    except Exception as e:
        print(f"❌ 方法3错误: {e}")
    
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Dify API 问题诊断工具")
    print("=" * 60)
    
    # 清理代理环境
    clean_proxy_env()
    
    # 测试基本连接
    if not test_basic_connectivity():
        print("❌ 基本网络连接失败，请检查网络设置")
        return
    
    # 测试DNS解析
    if not test_dns_resolution():
        print("❌ DNS解析失败，请检查网络设置")
        return
    
    # 测试API端点
    if not test_api_endpoint():
        print("❌ API端点不可访问")
        return
    
    # 测试API调用
    if test_api_with_different_methods():
        print("\n✅ API测试成功！")
    else:
        print("\n❌ 所有API测试方法都失败了")
        print("💡 可能的原因:")
        print("   1. API密钥无效或过期")
        print("   2. 网络连接问题")
        print("   3. API服务暂时不可用")
        print("   4. 请求格式不正确")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 