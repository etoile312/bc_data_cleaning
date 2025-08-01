import json
import os
from pathlib import Path

def extract_breast_cancer_qa():
    """
    从breast_cancer_qa.json文件中提取乳腺癌相关的问答对
    根据matched_keywords字段筛选，包含以下关键词的内容：
    - breast cancer
    - breast pain
    - breast tenderness
    - breast ultrasound
    - mammogram
    - mastectomy
    - nipple discharge
    - breast implant
    - mammary
    - ductal carcinoma
    - invasive ductal
    - her2
    """
    
    # 乳腺癌相关关键词
    breast_cancer_keywords = [
        "breast cancer",
        "breast pain", 
        "breast tenderness",
        "breast ultrasound",
        "mammogram",
        "mastectomy",
        "nipple discharge",
        "breast implant",
        "mammary",
        "ductal carcinoma",
        "invasive ductal",
        "her2"
    ]
    
    # 创建输出目录
    output_dir = Path("breast_cancer_qa_files")
    output_dir.mkdir(exist_ok=True)
    
    # 读取原始数据
    with open("breast_cancer_qa.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 筛选乳腺癌相关的问答对
    breast_cancer_qa = []
    for item in data:
        if "matched_keywords" in item:
            # 检查是否包含乳腺癌相关关键词
            for keyword in item["matched_keywords"]:
                if any(bc_keyword in keyword.lower() for bc_keyword in breast_cancer_keywords):
                    breast_cancer_qa.append(item)
                    break
    
    print(f"找到 {len(breast_cancer_qa)} 个乳腺癌相关的问答对")
    
    # 为每个问答对创建单独的JSON文件
    for i, qa in enumerate(breast_cancer_qa, 1):
        # 生成文件名，格式为 qa01_caremagic.json, qa02_caremagic.json 等
        filename = f"qa{i:02d}_caremagic.json"
        filepath = output_dir / filename
        
        # 保存单个问答对
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(qa, f, ensure_ascii=False, indent=2)
        
        print(f"已保存: {filename}")
    
    print(f"\n所有文件已保存到 {output_dir} 目录")
    
    # 显示一些统计信息
    keyword_counts = {}
    for qa in breast_cancer_qa:
        for keyword in qa.get("matched_keywords", []):
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    print("\n关键词统计:")
    for keyword, count in sorted(keyword_counts.items()):
        print(f"  {keyword}: {count}")

if __name__ == "__main__":
    extract_breast_cancer_qa() 