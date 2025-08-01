import json
import requests
import time
import os
import re
from pathlib import Path

# 清理代理环境变量，避免代理连接问题
for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
    os.environ.pop(var, None)

# ChatFlow（AI问答）配置
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-W0Vf8phyDHlPRyDkat7HczOK'
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

def call_chatflow_api_with_retry(question, max_retries=3):
    """调用ChatFlow API，带重试机制"""
    data = {
        "inputs": {},
        "query": question,
        "response_mode": "blocking",
        "user": "test_user_001"
    }
    
    for attempt in range(max_retries):
        try:
            # 添加随机延迟，避免请求过于频繁
            time.sleep(2)
            
            response = requests.post(
                CHATFLOW_API_URL, 
                headers=CHATFLOW_HEADERS, 
                data=json.dumps(data), 
                timeout=60,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ⚠️ API调用失败，状态码: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ API调用异常 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    
    return None

def extract_context_and_answer(response_data):
    """从API响应中提取retrieved_context和answer"""
    try:
        # 获取answer字段
        answer_text = response_data.get('answer', '')
        
        print("原始answer_text:")
        print(answer_text)
        print("\n" + "="*50 + "\n")
        
        # 检查是否包含<think>标签，如果有则移除
        if '<think>' in answer_text and '</think>' in answer_text:
            # 移除<think>部分，只保留最终答案
            think_start = answer_text.find('<think>')
            think_end = answer_text.find('</think>') + len('</think>')
            answer_text = answer_text[think_end:].strip()
            print("移除<think>后的answer_text:")
            print(answer_text)
            print("\n" + "="*50 + "\n")
        
        # 检查是否包含"retrieved_context:"和"answer:"的格式
        if "retrieved_context:" in answer_text and "answer:" in answer_text:
            print("检测到retrieved_context和answer格式，开始解析...")
            
            # 分割retrieved_context和answer部分
            parts = answer_text.split("answer:")
            if len(parts) == 2:
                # 提取retrieved_context部分
                context_part = parts[0]
                context_start = context_part.find("retrieved_context:")
                if context_start != -1:
                    # 移除"retrieved_context:"标题，获取内容
                    context_content = context_part[context_start + len("retrieved_context:"):].strip()
                    # 移除可能的格式标记
                    context_content = re.sub(r'^[-\s]*', '', context_content)
                    context_content = re.sub(r'[-\s]*$', '', context_content)
                    # 检查是否为空或只包含[]
                    if context_content.strip() in ['', '[]', '【】', '()', '（）']:
                        retrieved_context = ''
                    else:
                        retrieved_context = context_content
                else:
                    retrieved_context = ''
                
                print("提取的retrieved_context:")
                print(repr(retrieved_context))
                print("\n" + "="*50 + "\n")
                
                # 提取answer部分
                answer_part = parts[1].strip()
                # 移除可能的格式标记和注释
                answer_part = re.sub(r'（注：.*?）', '', answer_part, flags=re.DOTALL)
                answer_part = re.sub(r'更正后的第二部分：', '', answer_part)
                answer_part = re.sub(r'^\s*[-—]\s*', '', answer_part)
                answer_part = answer_part.strip()
                
                print("提取的ai_answer:")
                print(repr(answer_part))
                print("\n" + "="*50 + "\n")
                
                return retrieved_context, answer_part
            else:
                print("分割失败，parts数量:", len(parts))
                return '', answer_text
        # 检查是否包含"第一部分：**retrieved_context**"和"第二部分：**answer**"的格式
        elif "第一部分：**retrieved_context**" in answer_text and "第二部分：**answer**" in answer_text:
            print("检测到标准格式，开始解析...")
            # 分割retrieved_context和answer部分
            parts = answer_text.split("第二部分：**answer**")
            if len(parts) == 2:
                # 提取retrieved_context部分
                context_part = parts[0]
                context_start = context_part.find("第一部分：**retrieved_context**")
                if context_start != -1:
                    # 移除标题，获取内容
                    context_content = context_part[context_start + len("第一部分：**retrieved_context**"):].strip()
                    # 移除可能的格式标记
                    context_content = re.sub(r'^[-\s]*', '', context_content)
                    context_content = re.sub(r'[-\s]*$', '', context_content)
                    # 检查是否为空或只包含[]
                    if context_content.strip() in ['', '[]', '【】', '()', '（）']:
                        retrieved_context = ''
                    else:
                        retrieved_context = context_content
                else:
                    retrieved_context = ''
                
                print("提取的retrieved_context:")
                print(repr(retrieved_context))
                print("\n" + "="*50 + "\n")
                
                # 提取answer部分
                answer_part = parts[1].strip()
                # 移除可能的格式标记和注释
                answer_part = re.sub(r'（注：.*?）', '', answer_part, flags=re.DOTALL)
                answer_part = re.sub(r'更正后的第二部分：', '', answer_part)
                answer_part = re.sub(r'^\s*[-—]\s*', '', answer_part)
                answer_part = answer_part.strip()
                
                print("提取的ai_answer:")
                print(repr(answer_part))
                print("\n" + "="*50 + "\n")
                
                return retrieved_context, answer_part
            else:
                print("分割失败，parts数量:", len(parts))
                return '', answer_text
        else:
            print("未检测到标准格式")
            return '', answer_text
                
    except Exception as e:
        print(f"提取过程中出错: {e}")
        return '', ''

def test_single_qa():
    """测试单个问答对"""
    # 读取第一个QA文件进行测试
    qa_file_path = Path('breast_cancer_cmed_files/qa01_cmed.json')
    
    if not qa_file_path.exists():
        print(f"❌ 文件不存在: {qa_file_path}")
        return
    
    # 读取QA文件
    with open(qa_file_path, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    question = qa_data['question']
    ref_answer = qa_data['answers'][0] if qa_data['answers'] else ''
    
    print(f"问题: {question}")
    print(f"参考答案: {ref_answer}")
    print("\n" + "="*50 + "\n")
    
    # 调用ChatFlow API
    print("正在调用API...")
    response = call_chatflow_api_with_retry(question)
    
    if response:
        print("API调用成功，开始提取...")
        retrieved_context, ai_answer = extract_context_and_answer(response)
        
        print("\n最终结果:")
        print(f"retrieved_context: {repr(retrieved_context)}")
        print(f"ai_answer: {repr(ai_answer)}")
        
        # 保存测试结果
        result_data = {
            "question": question,
            "retrieved_context": retrieved_context,
            "ai_answer": ai_answer,
            "ref_answer": ref_answer
        }
        
        with open('test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print("\n测试结果已保存到 test_result.json")
    else:
        print("❌ API调用失败")

if __name__ == "__main__":
    test_single_qa() 