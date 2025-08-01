import json
import requests
import time
from pathlib import Path

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
        "user": "test_user_001"
    }
    
    try:
        response = requests.post(CHATFLOW_API_URL, headers=CHATFLOW_HEADERS, data=json.dumps(data))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        return None

def extract_context_and_answer(response_data):
    """从API响应中提取retrieved_context和answer"""
    try:
        # 先对response['answer']做json.loads()
        answer_json = response_data.get('answer', '{}')
        parsed = json.loads(answer_json)
        retrieved_context = parsed.get('retrieved_context', '')
        ai_answer = parsed.get('answer', '')
        return retrieved_context, ai_answer
    except Exception as e:
        print(f"提取数据失败: {e}")
        return '', ''

def process_qa_files():
    """处理QA文件"""
    # 创建输出目录
    output_dir = Path('chatflow_results')
    output_dir.mkdir(exist_ok=True)
    
    # 读取qa文件
    qa_dir = Path('breast_cancer_cmed_files')
    qa_files = sorted(qa_dir.glob('qa*.json'))
    
    print(f"找到 {len(qa_files)} 个QA文件")
    
    for i, qa_file in enumerate(qa_files, 1):
        print(f"处理文件 {i}: {qa_file.name}")
        
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
                "ref_answer": ref_answer
            }
            
            # 保存结果文件
            result_filename = f"result{i:02d}_amed.json"
            result_filepath = output_dir / result_filename
            
            with open(result_filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print(f"  已保存结果到: {result_filename}")
        else:
            print(f"  处理失败: {qa_file.name}")
        
        # 添加延迟避免API限制
        time.sleep(1)
    
    print(f"\n处理完成，结果保存在 {output_dir} 目录")

if __name__ == "__main__":
    process_qa_files() 