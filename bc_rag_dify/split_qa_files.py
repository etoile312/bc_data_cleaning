import json
import os

def split_qa_to_files(input_file, output_dir):
    """
    将乳腺癌问答对分别保存为单独的文件
    
    Args:
        input_file (str): breast_cancer_qa.json
        output_dir (str): spit_qa
    """
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 读取乳腺癌问答对文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"开始处理 {len(data)} 条乳腺癌问答对...")
        
        # 遍历每个问答对
        for i, item in enumerate(data, 1):
            # 提取问题和答案
            question = item.get('input', '')
            answer = item.get('output', '')
            
            # 跳过空的问答对
            if not question or not answer:
                print(f"跳过第 {i} 条：问题或答案为空")
                continue
            
            # 格式化文件名（两位数编号）
            file_name = f"qa{i:02d}_caremagic.json"
            file_path = os.path.join(output_dir, file_name)
            
            # 创建新的问答对格式
            qa_data = {
                "Q": question,
                "A": answer
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(qa_data, f, ensure_ascii=False, indent=2)
            
            print(f"已保存: {file_name}")
        
        print(f"\n✅ 完成！共保存了 {len(data)} 个文件到 {output_dir} 目录")
        
        # 显示前几个文件的内容预览
        print(f"\n📋 文件内容预览:")
        for i in range(1, min(4, len(data) + 1)):
            preview_file = os.path.join(output_dir, f"qa{i:02d}_caremagic.json")
            if os.path.exists(preview_file):
                with open(preview_file, 'r', encoding='utf-8') as f:
                    preview_data = json.load(f)
                print(f"\n--- qa{i:02d}_caremagic.json ---")
                print(f"Q: {preview_data['Q'][:100]}...")
                print(f"A: {preview_data['A'][:100]}...")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_file}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
    except Exception as e:
        print(f"❌ 处理文件时发生错误: {e}")

def main():
    # 文件路径配置
    input_file = "breast_cancer_qa.json"  # 乳腺癌问答对文件
    output_dir = "breast_cancer_qa_files"  # 输出目录
    
    print(f"正在将 {input_file} 中的问答对分别保存为单独文件...")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        print("请先运行 filter_breast_cancer.py 生成乳腺癌问答对文件")
        return
    
    # 执行分割
    split_qa_to_files(input_file, output_dir)

if __name__ == "__main__":
    main() 