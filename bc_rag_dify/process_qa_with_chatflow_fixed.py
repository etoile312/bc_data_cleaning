import json
import requests
import time
import os
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

def call_chatflow_api(question):
    """调用ChatFlow API"""
    data = {
        "inputs": {},
        "query": question,
        "response_mode": "blocking",  # 使用blocking模式
        "user": "test_user_001"
    }
    
    try:
        print(f"  调用API处理问题: {question[:50]}...")
        start_time = time.time()
        response = requests.post(CHATFLOW_API_URL, headers=CHATFLOW_HEADERS, data=json.dumps(data), timeout=120)
        end_time = time.time()
        
        print(f"  ⏱️ API调用耗时: {end_time - start_time:.2f}秒")
        print(f"  📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✅ API调用成功！")
            return response.json()
        else:
            print(f"  ⚠️ API调用失败，状态码: {response.status_code}")
            print(f"  📄 错误响应: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API调用异常: {e}")
        return None

def extract_context_and_answer(response_data):
    """从API响应中提取retrieved_context和answer"""
    try:
        # 获取answer字段
        answer_text = response_data.get('answer', '')
        print(f"  📄 原始answer长度: {len(answer_text)}")
        
        # 尝试解析JSON格式的answer
        try:
            # 查找JSON开始和结束的位置
            start_idx = answer_text.find('{')
            end_idx = answer_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = answer_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                retrieved_context = parsed.get('retrieved_context', '')
                ai_answer = parsed.get('answer', '')
                
                print(f"  ✅ 成功提取retrieved_context和answer")
                print(f"  📝 retrieved_context长度: {len(retrieved_context)}")
                print(f"  📝 ai_answer长度: {len(ai_answer)}")
                
                return retrieved_context, ai_answer
            else:
                print(f"  ⚠️ 未找到JSON格式，使用原始answer")
                return '', answer_text
                
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON解析失败: {e}")
            print(f"  📄 使用原始answer作为ai_answer")
            return '', answer_text
            
    except Exception as e:
        print(f"  ❌ 提取数据失败: {e}")
        return '', ''

def process_first_qa_file():
    """处理第一个QA文件"""
    # 创建输出目录
    output_dir = Path('chatflow_results')
    output_dir.mkdir(exist_ok=True)
    
    # 读取第一个qa文件
    qa_file = Path('breast_cancer_cmed_files/qa01_cmed.json')
    
    if not qa_file.exists():
        print(f"❌ 文件不存在: {qa_file}")
        return
    
    print(f"📁 处理文件: {qa_file.name}")
    
    # 读取QA文件
    with open(qa_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    question = qa_data['question']
    ref_answer = qa_data['answers'][0] if qa_data['answers'] else ''
    
    print(f"📝 问题: {question[:100]}...")
    print(f"📝 参考答案: {ref_answer[:100]}...")
    
    # 调用ChatFlow API
    response = call_chatflow_api(question)
    
    if response:
        retrieved_context, ai_answer = extract_context_and_answer(response)
        
        # 创建结果数据
        result_data = {
            "question": question,
            "retrieved_context": retrieved_context,
            "ai_answer": ai_answer,
            "ref_answer": ref_answer
        }
        
        # 保存结果文件
        result_filename = "result01_cmed.json"
        result_filepath = output_dir / result_filename
        
        with open(result_filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存结果到: {result_filename}")
        print(f"📊 结果统计:")
        print(f"   - 问题长度: {len(question)}")
        print(f"   - retrieved_context长度: {len(retrieved_context)}")
        print(f"   - ai_answer长度: {len(ai_answer)}")
        print(f"   - ref_answer长度: {len(ref_answer)}")
        
    else:
        print(f"❌ 处理失败: {qa_file.name}")

if __name__ == "__main__":
    print("🚀 开始处理第一个QA文件...")
    process_first_qa_file()
    print("🏁 处理完成！") 