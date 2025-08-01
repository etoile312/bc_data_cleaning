import json
import requests
import time
import os
import re
import random
from pathlib import Path
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from bert_score import score
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm

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

# 全局锁，用于保护模型访问
model_lock = threading.Lock()

# 全局模型变量
embedding_model = None
nli_tokenizer = None
nli_model = None

def initialize_models():
    """初始化评估模型"""
    global embedding_model, nli_tokenizer, nli_model
    
    print("🔧 正在加载评估模型...")
    
    # 1. 文本嵌入模型 (用于Context Relevance) - 必需
    try:
        embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
        print("✅ 文本嵌入模型加载完成")
    except Exception as e:
        print(f"❌ 文本嵌入模型加载失败: {e}")
        exit(1)
    
    # 2. NLI模型 (用于Answer Faithfulness和Answer Relevance) - 可选
    try:
        nli_model_name = 'MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli'
        nli_tokenizer = AutoTokenizer.from_pretrained(nli_model_name)
        nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model_name)
        nli_model.eval()  # 设置为评估模式
        print("✅ NLI模型加载完成")
    except Exception as e:
        print(f"⚠️ NLI模型加载失败，将使用Embedding回退: {e}")
        nli_tokenizer = None
        nli_model = None
    
    # 3. BERTScore模型 (用于Answer Correctness)
    print("✅ BERTScore模型准备就绪")

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
            time.sleep(random.uniform(1, 3))
            
            response = requests.post(
                CHATFLOW_API_URL, 
                headers=CHATFLOW_HEADERS, 
                data=json.dumps(data), 
                timeout=60,  # 减少超时时间
                verify=False  # 禁用SSL验证
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait_time = (attempt + 1) * 5
                print(f"  ⏳ 遇到频率限制，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                continue
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
        
        # 检查是否包含<think>标签，如果有则移除
        if '<think>' in answer_text and '</think>' in answer_text:
            # 移除<think>部分，只保留最终答案
            think_start = answer_text.find('<think>')
            think_end = answer_text.find('</think>') + len('</think>')
            answer_text = answer_text[think_end:].strip()
        
        # 现在处理清理后的answer_text
        # 检查是否包含"第一部分：**retrieved_context**"和"第二部分：**answer**"的格式
        if "第一部分：**retrieved_context**" in answer_text and "第二部分：**answer**" in answer_text:
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
                
                # 提取answer部分
                answer_part = parts[1].strip()
                # 移除可能的格式标记和注释
                answer_part = re.sub(r'（注：.*?）', '', answer_part, flags=re.DOTALL)
                answer_part = re.sub(r'更正后的第二部分：', '', answer_part)
                answer_part = re.sub(r'^\s*[-—]\s*', '', answer_part)
                answer_part = answer_part.strip()
                
                return retrieved_context, answer_part
            else:
                return '', answer_text
        else:
            # 如果没有明确的格式，尝试其他解析方式
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
                    
                    return retrieved_context, ai_answer
                else:
                    return '', answer_text
                    
            except json.JSONDecodeError as e:
                return '', answer_text
                
    except Exception as e:
        return '', ''

def calculate_context_relevance(question, retrieved_context):
    """计算上下文相关性 (Context Relevance)"""
    try:
        with model_lock:
            if embedding_model is None:
                print("❌ 模型未初始化")
                return 0.0
            embeddings = embedding_model.encode([question, retrieved_context])
            similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
            return float(similarity)
    except Exception as e:
        print(f"  ❌ Context Relevance计算失败: {e}")
        return 0.0

def calculate_answer_faithfulness(retrieved_context, ai_answer):
    """计算答案忠实度 (Answer Faithfulness) - 优先使用NLI模型，失败时回退到Embedding"""
    try:
        # 首先尝试使用NLI模型
        if nli_tokenizer is not None and nli_model is not None:
            with model_lock:
                # 准备输入
                inputs = nli_tokenizer(
                    retrieved_context, 
                    ai_answer, 
                    return_tensors="pt", 
                    truncation=True, 
                    max_length=512
                )
                
                with torch.no_grad():
                    outputs = nli_model(**inputs)
                    logits = outputs.logits
                    probs = torch.softmax(logits, dim=1)
                    
                    # 获取entailment概率 (通常索引为2)
                    entailment_prob = probs[0][2].item()
                    return float(entailment_prob)
        else:
            # NLI模型不可用，使用embedding余弦相似度
            with model_lock:
                if embedding_model is None:
                    print("❌ 模型未初始化")
                    return 0.0
                embeddings = embedding_model.encode([retrieved_context, ai_answer])
                similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
                return float(similarity)
    except Exception as e:
        print(f"  ⚠️ NLI模型计算失败，使用Embedding回退: {e}")
        # 回退到embedding方法
        try:
            with model_lock:
                if embedding_model is None:
                    print("❌ 模型未初始化")
                    return 0.0
                embeddings = embedding_model.encode([retrieved_context, ai_answer])
                similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
                return float(similarity)
        except Exception as e2:
            print(f"  ❌ Answer Faithfulness计算失败: {e2}")
            return 0.0

def calculate_answer_relevance(question, ai_answer):
    """计算答案相关性 (Answer Relevance) - 优先使用NLI模型，失败时回退到Embedding"""
    try:
        # 首先尝试使用NLI模型
        if nli_tokenizer is not None and nli_model is not None:
            with model_lock:
                # 准备输入
                inputs = nli_tokenizer(
                    question, 
                    ai_answer, 
                    return_tensors="pt", 
                    truncation=True, 
                    max_length=512
                )
                
                with torch.no_grad():
                    outputs = nli_model(**inputs)
                    logits = outputs.logits
                    probs = torch.softmax(logits, dim=1)
                    
                    # 获取entailment概率 (通常索引为2)
                    entailment_prob = probs[0][2].item()
                    return float(entailment_prob)
        else:
            # NLI模型不可用，使用embedding余弦相似度
            with model_lock:
                if embedding_model is None:
                    print("❌ 模型未初始化")
                    return 0.0
                embeddings = embedding_model.encode([question, ai_answer])
                similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
                return float(similarity)
    except Exception as e:
        print(f"  ⚠️ NLI模型计算失败，使用Embedding回退: {e}")
        # 回退到embedding方法
        try:
            with model_lock:
                if embedding_model is None:
                    print("❌ 模型未初始化")
                    return 0.0
                embeddings = embedding_model.encode([question, ai_answer])
                similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
                return float(similarity)
        except Exception as e2:
            print(f"  ❌ Answer Relevance计算失败: {e2}")
            return 0.0

def calculate_answer_correctness(ai_answer, ref_answer):
    """计算答案正确性 (Answer Correctness) - 优先使用BERTScore，失败时回退到Embedding"""
    try:
        # 使用BERTScore计算语义匹配度
        P, R, F1 = score([ai_answer], [ref_answer], lang='zh', verbose=False)
        return float(F1[0])
    except Exception as e:
        print(f"  ⚠️ BERTScore计算失败，使用Embedding回退: {e}")
        # 回退到embedding方法
        try:
            with model_lock:
                if embedding_model is None:
                    print("❌ 模型未初始化")
                    return 0.0
                embeddings = embedding_model.encode([ai_answer, ref_answer])
                similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
                return float(similarity)
        except Exception as e2:
            print(f"  ❌ Answer Correctness计算失败: {e2}")
            return 0.0

def extract_keywords(text):
    """提取关键词/实体"""
    # 丰富的中英文医疗关键词
    medical_keywords = [
        # 中文关键词
        '乳头', '溢液', '乳房', '乳腺', '月经', '检查', '治疗', '医院', '医生',
        '症状', '疼痛', '胀痛', '白色', '液体', '激素', '雌激素', '催乳素',
        '增生', '导管', '细胞', '病理', '超声', '钼靶', '乳透', '肿块',
        '结节', '囊肿', '纤维瘤', '乳腺癌', '良性', '恶性', '转移',
        '手术', '化疗', '放疗', '靶向治疗', '免疫治疗', '内分泌治疗',
        '活检', '穿刺', '切片', '免疫组化', '基因检测', '分子分型',
        '分期', '分级', '预后', '复发', '生存率', '治愈率',
        '筛查', '预防', '早期发现', '定期检查', '自检', '触诊',
        '影像学', 'CT', 'MRI', 'PET-CT', '骨扫描', '淋巴结',
        '腋窝', '锁骨', '胸骨', '肋骨', '肺', '肝', '脑', '骨',
        
        # 英文关键词
        'breast', 'nipple', 'discharge', 'lump', 'mass', 'tumor', 'cancer',
        'carcinoma', 'adenocarcinoma', 'ductal', 'lobular', 'invasive',
        'in situ', 'DCIS', 'LCIS', 'IDC', 'ILC', 'HER2', 'ER', 'PR',
        'triple negative', 'hormone receptor', 'estrogen', 'progesterone',
        'prolactin', 'mammogram', 'ultrasound', 'biopsy', 'fine needle',
        'core needle', 'excisional', 'incisional', 'sentinel node',
        'axillary', 'lymph node', 'metastasis', 'metastatic', 'stage',
        'grade', 'prognosis', 'survival', 'recurrence', 'remission',
        'chemotherapy', 'radiation', 'surgery', 'mastectomy', 'lumpectomy',
        'reconstruction', 'implant', 'flap', 'radiation therapy',
        'targeted therapy', 'immunotherapy', 'hormone therapy',
        'tamoxifen', 'aromatase inhibitor', 'herceptin', 'perjeta',
        'kadcyla', 'enhertu', 'ibrance', 'verzenio', 'kisqali',
        'screening', 'prevention', 'early detection', 'risk factors',
        'family history', 'genetic', 'BRCA1', 'BRCA2', 'PALB2',
        'TP53', 'PTEN', 'ATM', 'CHEK2', 'genetic testing',
        'counseling', 'surveillance', 'prophylactic', 'mastectomy',
        'oophorectomy', 'salpingo-oophorectomy', 'hysterectomy',
        
        # 症状相关
        'pain', 'tenderness', 'swelling', 'redness', 'warmth',
        'itching', 'rash', 'dimpling', 'puckering', 'retraction',
        'inversion', 'discharge', 'bleeding', 'ulceration', 'fever',
        'fatigue', 'weight loss', 'appetite', 'nausea', 'vomiting',
        'constipation', 'diarrhea', 'cough', 'shortness of breath',
        'chest pain', 'back pain', 'bone pain', 'headache',
        'dizziness', 'confusion', 'seizure', 'paralysis',
        
        # 检查方法
        'physical exam', 'clinical breast exam', 'mammography',
        'digital mammogram', '3D mammogram', 'tomosynthesis',
        'breast MRI', 'breast ultrasound', 'elastography',
        'contrast enhanced', 'diffusion weighted', 'spectroscopy',
        'nuclear medicine', 'scintigraphy', 'bone scan',
        'liver scan', 'brain scan', 'PET scan', 'CT scan',
        'chest X-ray', 'abdominal CT', 'pelvic CT', 'brain MRI',
        
        # 治疗相关
        'surgery', 'lumpectomy', 'mastectomy', 'breast conserving',
        'modified radical', 'radical', 'simple', 'skin sparing',
        'nipple sparing', 'reconstruction', 'implant', 'tissue expander',
        'autologous', 'TRAM flap', 'DIEP flap', 'latissimus dorsi',
        'chemotherapy', 'neoadjuvant', 'adjuvant', 'palliative',
        'radiation', 'external beam', 'brachytherapy', 'intraoperative',
        'hormone therapy', 'endocrine therapy', 'targeted therapy',
        'immunotherapy', 'clinical trial', 'protocol', 'regimen',
        
        # 药物相关
        'doxorubicin', 'adriamycin', 'cyclophosphamide', 'cytoxan',
        'methotrexate', '5-fluorouracil', '5-FU', 'paclitaxel',
        'taxol', 'docetaxel', 'taxotere', 'carboplatin', 'cisplatin',
        'capecitabine', 'xeloda', 'gemcitabine', 'gemzar',
        'vinorelbine', 'navelbine', 'eribulin', 'halaven',
        'tamoxifen', 'nolvadex', 'raloxifene', 'evista',
        'anastrozole', 'arimidex', 'letrozole', 'femara',
        'exemestane', 'aromasin', 'fulvestrant', 'faslodex',
        'trastuzumab', 'herceptin', 'pertuzumab', 'perjeta',
        'ado-trastuzumab', 'kadcyla', 'fam-trastuzumab', 'enhertu',
        'palbociclib', 'ibrance', 'ribociclib', 'kisqali',
        'abemaciclib', 'verzenio', 'alpelisib', 'piqray',
        'olaparib', 'lynparza', 'talazoparib', 'talzenna'
    ]
    
    found_keywords = []
    for keyword in medical_keywords:
        if keyword.lower() in text.lower():  # 不区分大小写
            found_keywords.append(keyword)
    
    return found_keywords

def calculate_context_recall(ref_answer, retrieved_context):
    """计算上下文召回率 (Context Recall)"""
    try:
        # 如果retrieved_context为空，直接返回0
        if not retrieved_context or retrieved_context.strip() == '':
            return 0.0
        
        # 提取ref_answer中的关键词
        ref_keywords = extract_keywords(ref_answer)
        
        if not ref_keywords:
            return 0.0
        
        # 统计这些关键词在retrieved_context中出现的比例（不区分大小写）
        found_count = 0
        retrieved_context_lower = retrieved_context.lower()
        
        for keyword in ref_keywords:
            if keyword.lower() in retrieved_context_lower:
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

def process_single_qa_file(qa_file_path):
    """处理单个QA文件并计算评估指标"""
    try:
        # 读取QA文件
        with open(qa_file_path, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        question = qa_data['question']
        ref_answer = qa_data['answers'][0] if qa_data['answers'] else ''
        
        # 调用ChatFlow API（带重试）
        response = call_chatflow_api_with_retry(question)
        
        if response:
            retrieved_context, ai_answer = extract_context_and_answer(response)
            
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
            
            return {
                'file_name': qa_file_path.name,
                'success': True,
                'result_data': result_data,
                'scores': scores
            }
        else:
            return {
                'file_name': qa_file_path.name,
                'success': False,
                'error': 'API调用失败'
            }
            
    except Exception as e:
        return {
            'file_name': qa_file_path.name,
            'success': False,
            'error': str(e)
        }

def process_all_qa_files():
    """并发处理所有QA文件"""
    # 初始化模型
    initialize_models()
    
    # 创建输出目录
    output_dir = Path('chatflow_results')
    output_dir.mkdir(exist_ok=True)
    
    # 获取前20个qa文件（第1-10和100-109）
    qa_dir = Path('breast_cancer_cmed_files')
    all_files = sorted([f for f in qa_dir.glob('qa*.json')])
    
    # 选择第1-10和100-109这20个文件
    selected_files = []
    for i in range(1, 11):  # 1-10
        filename = f'qa{i:02d}_cmed.json'
        file_path = qa_dir / filename
        if file_path.exists():
            selected_files.append(file_path)
    
    for i in range(100, 110):  # 100-109
        filename = f'qa{i:03d}_cmed.json'
        file_path = qa_dir / filename
        if file_path.exists():
            selected_files.append(file_path)
    
    qa_files = selected_files
    
    print(f"🚀 开始并发处理 {len(qa_files)} 个QA文件...")
    print(f"🔧 使用5个并发线程")
    
    # 存储所有结果
    all_results = []
    all_scores = []
    
    # 使用ThreadPoolExecutor进行并发处理
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_file = {executor.submit(process_single_qa_file, qa_file): qa_file for qa_file in qa_files}
        
        # 使用tqdm显示进度
        with tqdm(total=len(qa_files), desc="处理进度") as pbar:
            for future in as_completed(future_to_file):
                result = future.result()
                all_results.append(result)
                
                if result['success']:
                    # 保存结果文件
                    result_filename = f"result{result['file_name'].replace('qa', '').replace('.json', '')}_cmed.json"
                    result_filepath = output_dir / result_filename
                    
                    with open(result_filepath, 'w', encoding='utf-8') as f:
                        json.dump(result['result_data'], f, ensure_ascii=False, indent=2)
                    
                    all_scores.append(result['scores'])
                    print(f"✅ {result['file_name']} - RAG Score: {result['result_data']['rag_score_mean']:.4f}")
                else:
                    print(f"❌ {result['file_name']} - {result['error']}")
                
                pbar.update(1)
    
    # 计算平均分
    if all_scores:
        avg_scores = {}
        for metric in ['context_relevance', 'faithfulness', 'answer_relevance', 'answer_correctness', 'context_recall']:
            values = [score[metric] for score in all_scores if score[metric] is not None]
            avg_scores[metric] = sum(values) / len(values) if values else 0.0
        
        # 计算总平均分
        total_avg = sum(avg_scores.values()) / len(avg_scores)
        
        print(f"\n📊 处理完成！共处理 {len(all_scores)} 个文件")
        print(f"📈 各项指标平均分:")
        print(f"   - Context Relevance: {avg_scores['context_relevance']:.4f}")
        print(f"   - Faithfulness: {avg_scores['faithfulness']:.4f}")
        print(f"   - Answer Relevance: {avg_scores['answer_relevance']:.4f}")
        print(f"   - Answer Correctness: {avg_scores['answer_correctness']:.4f}")
        print(f"   - Context Recall: {avg_scores['context_recall']:.4f}")
        print(f"📊 总平均分: {total_avg:.4f}")
        
        # 保存汇总结果
        summary_data = {
            "total_files_processed": len(all_scores),
            "average_scores": avg_scores,
            "total_average": total_avg,
            "successful_files": [r['file_name'] for r in all_results if r['success']],
            "failed_files": [r['file_name'] for r in all_results if not r['success']]
        }
        
        summary_filepath = output_dir / "summary_results.json"
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 汇总结果已保存到: summary_results.json")
    else:
        print("❌ 没有成功处理的文件")

if __name__ == "__main__":
    process_all_qa_files() 