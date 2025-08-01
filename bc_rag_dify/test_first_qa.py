import json
import requests

# ChatFlow（AI问答）配置
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe'
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

def test_first_qa():
    """测试第一个QA文件"""
    # 读取第一个QA文件
    with open('breast_cancer_cmed_files/qa01_cmed.json', 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    question = qa_data['question']
    print(f"问题: {question}")
    
    # 调用API
    data = {
        "inputs": {},
        "query": question,
        "user": "test_user_001"
    }
    response = requests.post(CHATFLOW_API_URL, headers=CHATFLOW_HEADERS, data=json.dumps(data))
    
    print(f"API响应状态码: {response.status_code}")
    print(f"API响应内容:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_first_qa() 