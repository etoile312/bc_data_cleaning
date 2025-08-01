import json
import requests
import time
import os
import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from bert_score import score
import numpy as np

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

# 初始化模型
print("🔧 正在加载评估模型...")
try:
    # 1. 文本嵌入模型 (用于Context Relevance)
    embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
    print("✅ 文本嵌入模型加载完成")
    
    # 2. NLI模型 (用于Answer Faithfulness和Answer Relevance)
    nli_model_name = 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli'
    nli_tokenizer = AutoTokenizer.from_pretrained(nli_model_name)
    nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model_name)
    nli_model.eval()  # 设置为评估模式
    print("✅ NLI模型加载完成")
    
    # 3. BERTScore模型 (用于Answer Correctness)
    print("✅ BERTScore模型准备就绪")
    
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    exit(1)

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

def calculate_context_relevance(question, retrieved_context):
    """计算上下文相关性 (Context Relevance)"""
    try:
        # 使用Sentence-Transformers计算余弦相似度
        embeddings = embedding_model.encode([question, retrieved_context])
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        return float(similarity)
    except Exception as e:
        print(f"  ❌ Context Relevance计算失败: {e}")
        return 0.0

def calculate_answer_faithfulness(retrieved_context, ai_answer):
    """用embedding余弦相似度近似答案忠实度 (Answer Faithfulness)"""
    try:
        embeddings = embedding_model.encode([retrieved_context, ai_answer])
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        return float(similarity)
    except Exception as e:
        print(f"  ❌ Answer Faithfulness计算失败: {e}")
        return 0.0

def calculate_answer_relevance(question, ai_answer):
    """用embedding余弦相似度近似答案相关性 (Answer Relevance)"""
    try:
        embeddings = embedding_model.encode([question, ai_answer])
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        return float(similarity)
    except Exception as e:
        print(f"  ❌ Answer Relevance计算失败: {e}")
        return 0.0

def calculate_answer_correctness(ai_answer, ref_answer):
    """计算答案正确性 (Answer Correctness)"""
    try:
        # 使用BERTScore计算语义匹配度
        P, R, F1 = score([ai_answer], [ref_answer], lang='zh', verbose=False)
        return float(F1[0])
    except Exception as e:
        print(f"  ❌ Answer Correctness计算失败: {e}")
        return 0.0

def extract_keywords(text):
    """提取关键词/实体"""
    # 简单的关键词提取：医疗相关词汇
    medical_keywords = [
        '乳头', '溢液', '乳房', '乳腺', '月经', '检查', '治疗', '医院', '医生',
        '症状', '疼痛', '胀痛', '白色', '液体', '激素', '雌激素', '催乳素',
        '增生', '导管', '细胞', '病理', '超声', '钼靶', '乳透'
    ]
    
    found_keywords = []
    for keyword in medical_keywords:
        if keyword in text:
            found_keywords.append(keyword)
    
    return found_keywords

def calculate_context_recall(ref_answer, retrieved_context):
    """计算上下文召回率 (Context Recall)"""
    try:
        # 提取ref_answer中的关键词
        ref_keywords = extract_keywords(ref_answer)
        
        if not ref_keywords:
            return 0.0
        
        # 统计这些关键词在retrieved_context中出现的比例
        found_count = 0
        for keyword in ref_keywords:
            if keyword in retrieved_context:
                found_count += 1
        
        recall = found_count / len(ref_keywords)
        return recall
    except Exception as e:
        print(f"  ❌ Context Recall计算失败: {e}")
        return 0.0

def calculate_rag_score_mean(scores):
    """计算RAG评分均值"""
    valid_scores = [score for score in scores.values() if score is not None]
    if valid_scores:
        return sum(valid_scores) / len(valid_scores)
    return 0.0

def process_first_qa_file():
    """处理第一个QA文件并计算评估指标"""
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
        
        print("\n📊 开始计算评估指标...")
        
        # 计算各项评估指标
        context_relevance = calculate_context_relevance(question, retrieved_context)
        faithfulness = calculate_answer_faithfulness(retrieved_context, ai_answer)
        answer_relevance = calculate_answer_relevance(question, ai_answer)
        answer_correctness = calculate_answer_correctness(ai_answer, ref_answer)
        context_recall = calculate_context_recall(ref_answer, retrieved_context)
        
        # 计算RAG评分均值
        scores = {
            'context_relevance': context_relevance,
            'faithfulness': faithfulness,
            'answer_relevance': answer_relevance,
            'answer_correctness': answer_correctness,
            'context_recall': context_recall
        }
        rag_score_mean = calculate_rag_score_mean(scores)
        
        # 创建结果数据
        result_data = {
            "question": question,
            "retrieved_context": retrieved_context,
            "ai_answer": ai_answer,
            "ref_answer": ref_answer,
            "context_relevance": context_relevance,
            "faithfulness": faithfulness,
            "answer_relevance": answer_relevance,
            "answer_correctness": answer_correctness,
            "context_recall": context_recall,
            "rag_score_mean": rag_score_mean
        }
        
        # 保存结果文件
        result_filename = "result01_cmed.json"
        result_filepath = output_dir / result_filename
        
        with open(result_filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存结果到: {result_filename}")
        print(f"📊 评估指标结果:")
        print(f"   - Context Relevance: {context_relevance:.4f}")
        print(f"   - Faithfulness: {faithfulness:.4f}")
        print(f"   - Answer Relevance: {answer_relevance:.4f}")
        print(f"   - Answer Correctness: {answer_correctness:.4f}")
        print(f"   - Context Recall: {context_recall:.4f}")
        print(f"   - RAG Score Mean: {rag_score_mean:.4f}")
        
    else:
        print(f"❌ 处理失败: {qa_file.name}")

if __name__ == "__main__":
    print("🚀 开始处理第一个QA文件并计算评估指标...")
    process_first_qa_file()
    print("🏁 处理完成！") 