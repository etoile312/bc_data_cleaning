import json
import requests
from pathlib import Path
from text2vec import SentenceModel, cos_sim
from bert_score import score as bert_score
import jieba
from transformers.pipelines import pipeline




# 加载中文句向量模型
model = SentenceModel('shibing624/text2vec-base-chinese')

# 加载NLI模型
nli = pipeline("text-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

def semantic_similarity(a, b):
    if not a or not b:
        return 0.0
    emb_a = model.encode([a])[0]
    emb_b = model.encode([b])[0]
    sim = cos_sim(emb_a, emb_b)
    return float(sim)

def bertscore_similarity(a, b, lang='zh'):
    P, R, F1 = bert_score([a], [b], lang=lang, rescale_with_baseline=True)
    return float(F1[0])

def nli_entailment_prob(premise, hypothesis):
    result = nli(f"{premise} </s> {hypothesis}")
    for r in result:
        if r['label'].lower() == 'entailment':
            return r['score']
    return 0.0

def keyword_recall(ref, context):
    ref_words = set(jieba.lcut(ref))
    context_words = set(jieba.lcut(context))
    if not ref_words:
        return 0.0
    return len(ref_words & context_words) / len(ref_words)

# ChatFlow（AI问答）配置
CHATFLOW_API_URL = 'https://api.dify.ai/v1/chat-messages'
CHATFLOW_API_KEY = 'Bearer app-tu0nSXElJlir9Z6L8XKfWdWe'
CHATFLOW_HEADERS = {
    'Authorization': CHATFLOW_API_KEY,
    'Content-Type': 'application/json',
}

def call_chatflow_api(question):
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
    try:
        answer_json = response_data.get('answer', '{}')
        parsed = json.loads(answer_json)
        retrieved_context = parsed.get('retrieved_context', '')
        ai_answer = parsed.get('answer', '')
        return retrieved_context, ai_answer
    except Exception as e:
        print(f"提取数据失败: {e}")
        return '', ''

def process_first_qa():
    output_dir = Path('chatflow_results')
    output_dir.mkdir(exist_ok=True)
    qa_file = Path('breast_cancer_cmed_files/qa01_cmed.json')
    print(f"处理文件: {qa_file.name}")
    with open(qa_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    question = qa_data['question']
    ref_answer = qa_data['answers'][0] if qa_data['answers'] else ''
    print(f"问题: {question}")
    print(f"参考答案: {ref_answer}")
    # 调用ChatFlow API
    print("调用API...")
    response = call_chatflow_api(question)
    if response:
        retrieved_context, ai_answer = extract_context_and_answer(response)
        print(f"检索上下文: {retrieved_context}")
        print(f"AI答案: {ai_answer}")
        # 计算五个RAG指标
        context_relevance = semantic_similarity(question, retrieved_context)
        faithfulness = bertscore_similarity(retrieved_context, ai_answer)
        answer_relevance = nli_entailment_prob(question, ai_answer)
        answer_correctness = bertscore_similarity(ai_answer, ref_answer)
        context_recall = keyword_recall(ref_answer, retrieved_context)
        rag_score_mean = round((context_relevance + faithfulness + answer_relevance + answer_correctness + context_recall) / 5, 4)
        # 创建结果数据
        result_data = {
            "question": question,
            "retrieved_context": retrieved_context,
            "ai_answer": ai_answer,
            "ref_answer": ref_answer,
            "context_relevance": round(context_relevance, 4),
            "faithfulness": round(faithfulness, 4),
            "answer_relevance": round(answer_relevance, 4),
            "answer_correctness": round(answer_correctness, 4),
            "context_recall": round(context_recall, 4),
            "rag_score_mean": rag_score_mean
        }
        # 保存结果文件
        result_filename = "result01_cmed.json"
        result_filepath = output_dir / result_filename
        with open(result_filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        print(f"已保存结果到: {result_filename}")
        print(f"五个指标及均分: {result_data}")
    else:
        print("处理失败")

if __name__ == "__main__":
    process_first_qa() 