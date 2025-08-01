import json
import requests
import time
import os
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 清理代理环境变量
proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]

# 设置不使用代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ChatFlow（AI问答）配置
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe'
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

def create_session_without_proxy():
    """创建一个不使用代理的session"""
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

def call_chatflow_api(question, max_retries=3):
    """调用ChatFlow API，带重试机制"""
    data = {
        "inputs": {},
        "query": question,
        "user": "test_user_001"
    }
    
    session = create_session_without_proxy()
    
    for attempt in range(max_retries):
        try:
            print(f"  尝试第 {attempt + 1} 次调用API...")
            
            response = session.post(
                CHATFLOW_API_URL, 
                headers=CHATFLOW_HEADERS, 
                json=data,  # 使用json参数
                timeout=120
            )
            
            if response.status_code == 200:
                print(f"  ✅ API调用成功")
                return response.json()
            else:
                print(f"  ⚠️ API调用失败，状态码: {response.status_code}")
                print(f"  错误响应: {response.text}")
                
        except requests.exceptions.ProxyError as e:
            print(f"  ❌ 代理错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                continue
                
        except requests.exceptions.Timeout:
            print(f"  ❌ 请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
                
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ 连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
                
        except Exception as e:
            print(f"  ❌ 其他错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
    
    print(f"  ❌ 所有重试都失败了")
    return None

def extract_context_and_answer(response_data):
    """从API响应中提取retrieved_context和answer"""
    try:
        # 检查response_data的结构
        if not response_data:
            print("  ⚠️ 响应数据为空")
            return '', ''
            
        # 打印响应结构以便调试
        print(f"  📄 响应数据结构: {list(response_data.keys()) if isinstance(response_data, dict) else '非字典类型'}")
        
        # 尝试不同的响应格式
        if isinstance(response_data, dict):
            # 格式1: 直接包含answer字段
            if 'answer' in response_data:
                answer_content = response_data['answer']
                print(f"  📝 找到answer字段: {type(answer_content)}")
                
                # 如果answer是字符串，尝试解析JSON
                if isinstance(answer_content, str):
                    try:
                        parsed = json.loads(answer_content)
                        retrieved_context = parsed.get('retrieved_context', '')
                        ai_answer = parsed.get('answer', '')
                        return retrieved_context, ai_answer
                    except json.JSONDecodeError:
                        # 如果不是JSON，直接使用字符串作为answer
                        return '', answer_content
                else:
                    # 如果answer不是字符串，直接使用
                    return '', str(answer_content)
            
            # 格式2: 直接包含retrieved_context和answer
            elif 'retrieved_context' in response_data and 'answer' in response_data:
                return response_data['retrieved_context'], response_data['answer']
            
            # 格式3: 其他可能的字段
            else:
                print(f"  ⚠️ 未找到预期的字段，使用整个响应作为answer")
                return '', json.dumps(response_data, ensure_ascii=False)
        
        else:
            print(f"  ⚠️ 响应数据不是字典类型: {type(response_data)}")
            return '', str(response_data)
            
    except Exception as e:
        print(f"  ❌ 提取数据失败: {e}")
        return '', ''

def test_first_three_files():
    """测试前3个文件"""
    # 创建输出目录
    output_dir = Path('chatflow_results')
    output_dir.mkdir(exist_ok=True)
    
    # 读取qa文件
    qa_dir = Path('breast_cancer_cmed_files')
    qa_files = sorted(qa_dir.glob('qa*.json'))[:3]  # 只处理前3个文件
    
    print(f"测试前 {len(qa_files)} 个QA文件")
    
    success_count = 0
    fail_count = 0
    
    for i, qa_file in enumerate(qa_files, 1):
        print(f"\n处理文件 {i}/{len(qa_files)}: {qa_file.name}")
        
        try:
            # 读取QA文件
            with open(qa_file, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            
            question = qa_data['question']
            ref_answer = qa_data['answers'][0] if qa_data['answers'] else ''
            
            # 调用ChatFlow API
            print(f"  调用API处理问题: {question[:50]}...")
            response = call_chatflow_api(question)
            
            if response:
                retrieved_context, ai_answer = extract_context_and_answer(response)
                
                # 创建结果数据
                result_data = {
                    "question": question,
                    "retrieved_context": retrieved_context,
                    "ai_answer": ai_answer,
                    "ref_answer": ref_answer,
                    "api_response": response  # 保存完整响应用于调试
                }
                
                # 保存结果文件
                result_filename = f"test_result{i:02d}_cmed.json"
                result_filepath = output_dir / result_filename
                
                with open(result_filepath, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ 已保存结果到: {result_filename}")
                success_count += 1
            else:
                print(f"  ❌ 处理失败: {qa_file.name}")
                fail_count += 1
                
        except Exception as e:
            print(f"  ❌ 处理文件时出错: {e}")
            fail_count += 1
        
        # 添加延迟避免API限制
        time.sleep(2)
    
    print(f"\n测试完成！")
    print(f"✅ 成功: {success_count} 个文件")
    print(f"❌ 失败: {fail_count} 个文件")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ChatFlow API 测试工具 (修复版)")
    print("=" * 60)
    test_first_three_files()
    print("=" * 60) 