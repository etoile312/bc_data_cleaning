import requests
import socket
import time

def test_basic_connectivity():
    """测试基本网络连通性"""
    print("🌐 开始网络连通性测试...")
    
    # 测试DNS解析
    try:
        socket.gethostbyname("www.google.com")
        print("✅ DNS解析正常")
    except socket.gaierror:
        print("❌ DNS解析失败")
        return False
    
    # 测试HTTP连接
    try:
        response = requests.get("http://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ HTTP连接正常")
        else:
            print(f"⚠️ HTTP连接异常，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP连接失败: {e}")
        return False
    
    return True

def test_dify_api():
    """测试Dify API连接"""
    print("\n🤖 测试Dify API连接...")
    
    url = 'https://api.dify.ai/v1/chat-messages'
    api_key = 'app-tu0nSXElJlir9Z6L8XKfWdWe'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    data = {
        "inputs": {},
        "query": "测试连接",
        "user": "test-user"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ Dify API连接成功 (响应时间: {end_time - start_time:.2f}秒)")
            return True
        else:
            print(f"⚠️ Dify API连接异常，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Dify API连接超时")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Dify API连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ Dify API其他错误: {e}")
        return False

def test_speed():
    """测试网络速度"""
    print("\n⚡ 测试网络速度...")
    
    try:
        start_time = time.time()
        response = requests.get("https://httpbin.org/bytes/1024", timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            duration = end_time - start_time
            speed = 1024 / duration  # bytes per second
            print(f"✅ 网络速度测试完成")
            print(f"   下载1KB用时: {duration:.2f}秒")
            print(f"   速度: {speed:.0f} bytes/s")
            return True
        else:
            print(f"⚠️ 速度测试失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 速度测试失败: {e}")
        return False

if __name__ == "__main__":
    import json
    
    print("=" * 50)
    print("网络连通性测试工具")
    print("=" * 50)
    
    # 基本连通性测试
    basic_ok = test_basic_connectivity()
    
    # 速度测试
    speed_ok = test_speed()
    
    # Dify API测试
    dify_ok = test_dify_api()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"基本连通性: {'✅ 正常' if basic_ok else '❌ 异常'}")
    print(f"网络速度: {'✅ 正常' if speed_ok else '❌ 异常'}")
    print(f"Dify API: {'✅ 正常' if dify_ok else '❌ 异常'}")
    
    if basic_ok and speed_ok and dify_ok:
        print("\n🎉 所有测试通过！网络连接正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查网络设置。")
    print("=" * 50) 