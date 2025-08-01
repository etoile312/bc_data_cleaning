import csv
import json
from pathlib import Path

# 乳腺癌相关关键词
KEYWORDS = [
    '乳腺癌', '乳房肿瘤', '乳房癌', '乳腺肿瘤',
    '乳腺钼靶','乳腺穿刺', '乳腺导管', '乳腺切除', '乳腺复发', '乳腺转移'
]

# 读取问题
questions = {}
with open('question.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        questions[row['question_id']] = row['content']

# 读取答案
answers = {}
with open('answer.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        qid = row['question_id']
        if qid not in answers:
            answers[qid] = []
        answers[qid].append(row['content'])

# 筛选乳腺癌相关问答
output_dir = Path('breast_cancer_cmed_files')
output_dir.mkdir(exist_ok=True)

idx = 1
for qid, q_content in questions.items():
    # 检查问题或答案是否包含关键词
    related = any(kw in q_content for kw in KEYWORDS)
    ans_list = answers.get(qid, [])
    if not related:
        for ans in ans_list:
            if any(kw in ans for kw in KEYWORDS):
                related = True
                break
    if related and ans_list:
        qa = {
            'question': q_content,
            'answers': ans_list
        }
        filename = f'qa{idx:02d}_cmed.json'
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(qa, f, ensure_ascii=False, indent=2)
        idx += 1

print(f'共保存 {idx-1} 个乳腺癌相关问答对到 {output_dir}') 