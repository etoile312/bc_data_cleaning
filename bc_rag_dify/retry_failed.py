import os
import json
from test2 import process_file  # 复用你的处理函数

SCORE_DIR = 'qa_scores'
TESTSET_DIR = 'qa_files'

def is_all_zero(scores):
    return all(v == 0.0 for v in scores.values())

def main():
    files = sorted(os.listdir(SCORE_DIR))
    failed_files = []
    for file in files:
        if not file.endswith('_score.json'):
            continue
        with open(os.path.join(SCORE_DIR, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data.get('ai_answer') or is_all_zero(data.get('scores', {})):
            # 找到原始问答文件名
            qa_file = file.replace('_score.json', '.json')
            if os.path.exists(os.path.join(TESTSET_DIR, qa_file)):
                failed_files.append(qa_file)
    print(f'需重试的文件: {failed_files}')
    # 重新处理
    for qa_file in failed_files:
        process_file(qa_file)

if __name__ == '__main__':
    main()
