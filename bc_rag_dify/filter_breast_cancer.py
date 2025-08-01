import json
import re

def filter_breast_cancer_qa(input_file, output_file):
    """
    从JSON文件中筛选出乳腺癌相关的问答对
    
    Args:
        input_file (str): /Users/ssmac/Downloads/HealthCareMagic-100k.json
        output_file (str): /Users/ssmac/Downloads/HealthCareMagic-bc.json
    """
    
    # 乳腺癌相关的关键词（中英文）
    breast_cancer_keywords = [
        # 英文关键词
        'breast cancer', 'breast tumor', 'breast lump', 'breast mass',
        'mammary', 'mastectomy', 'breast surgery', 'breast pain',
        'nipple discharge', 'breast swelling', 'breast tenderness',
        'breast biopsy', 'breast examination', 'breast self-exam',
        'mammogram', 'breast ultrasound', 'breast MRI',
        'ductal carcinoma', 'lobular carcinoma', 'invasive ductal',
        'HER2', 'estrogen receptor', 'progesterone receptor',
        'breast reconstruction', 'breast implant',
        
        # 中文关键词
        '乳腺癌', '乳房癌', '乳腺肿瘤', '乳房肿块', '乳腺结节',
        '乳房疼痛', '乳头溢液', '乳房肿胀', '乳房压痛',
        '乳腺检查', '乳房自检', '乳腺活检', '乳房手术',
        '乳腺切除术', '乳房重建', '乳腺增生', '乳腺炎',
        '导管癌', '小叶癌', '浸润性导管癌', '乳腺纤维瘤',
        '乳腺囊肿', '乳腺钙化', '乳腺密度', '乳腺导管',
        '乳房下垂', '乳房不对称', '乳房皮肤改变',
        '腋窝淋巴结', '锁骨下淋巴结', '乳腺淋巴',
        '乳腺钼靶', '乳腺B超', '乳腺核磁',
        '雌激素受体', '孕激素受体', 'HER2阳性',
        '化疗', '放疗', '内分泌治疗', '靶向治疗'
    ]
    
    # 编译正则表达式，不区分大小写
    pattern = re.compile('|'.join(breast_cancer_keywords), re.IGNORECASE)
    
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"总共有 {len(data)} 条问答对")
        
        # 筛选乳腺癌相关的问答对
        breast_cancer_qa = []
        
        for i, item in enumerate(data):
            # 检查input和output字段是否包含乳腺癌相关关键词
            input_text = item.get('input', '')
            output_text = item.get('output', '')
            instruction_text = item.get('instruction', '')
            
            # 合并所有文本进行搜索
            combined_text = f"{instruction_text} {input_text} {output_text}"
            
            if pattern.search(combined_text):
                # 找到匹配的问答对，添加匹配信息
                matches = pattern.findall(combined_text.lower())
                unique_matches = list(set(matches))
                
                # 添加匹配的关键词信息
                item_with_matches = item.copy()
                item_with_matches['matched_keywords'] = unique_matches
                item_with_matches['original_index'] = i
                
                breast_cancer_qa.append(item_with_matches)
                
                print(f"找到匹配 #{len(breast_cancer_qa)}: {unique_matches}")
                print(f"问题: {input_text[:100]}...")
                print("-" * 50)
        
        # 保存筛选结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(breast_cancer_qa, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 筛选完成！")
        print(f"找到 {len(breast_cancer_qa)} 条乳腺癌相关的问答对")
        print(f"结果已保存到: {output_file}")
        
        # 显示统计信息
        if breast_cancer_qa:
            print(f"\n📊 匹配关键词统计:")
            keyword_count = {}
            for item in breast_cancer_qa:
                for keyword in item['matched_keywords']:
                    keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            
            # 按出现次数排序
            sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
            for keyword, count in sorted_keywords[:10]:  # 显示前10个
                print(f"  {keyword}: {count} 次")
        
        return breast_cancer_qa
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 处理文件时发生错误: {e}")
        return []

def main():
    # 文件路径配置
    input_file = '/Users/ssmac/Downloads/HealthCareMagic-100k.json'
    output_file = 'breast_cancer_qa.json'
    
    print(f"正在从 {input_file} 中筛选乳腺癌相关问答对...")
    
    # 执行筛选
    results = filter_breast_cancer_qa(input_file, output_file)
    
    if results:
        print(f"\n🎯 筛选结果预览:")
        for i, item in enumerate(results[:3]):  # 显示前3条
            print(f"\n--- 第 {i+1} 条 ---")
            print(f"匹配关键词: {item['matched_keywords']}")
            print(f"问题: {item['input'][:200]}...")
            print(f"回答: {item['output'][:200]}...")

if __name__ == "__main__":
    main() 