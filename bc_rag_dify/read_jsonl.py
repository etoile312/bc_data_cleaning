import json
import os

# 设置要读取的文件路径
file_path = '/Users/ssmac/Downloads/data_clean/questions/Mainland/chinese_qbank.jsonl'

def read_jsonl(file_path):
    """
    读取JSONL文件，返回所有JSON对象的列表
    
    Args:
        file_path (str): JSONL文件路径
        
    Returns:
        list: 包含所有JSON对象的列表
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        json_obj = json.loads(line)
                        data.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"第{line_num}行JSON解析错误: {e}")
                        print(f"问题行内容: {line}")
                        continue
        print(f"成功读取 {len(data)} 条记录")
        return data
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        return []
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return []

def read_jsonl_generator(file_path):
    """
    使用生成器方式读取JSONL文件，适用于大文件
    
    Args:
        file_path (str): JSONL文件路径
        
    Yields:
        dict: 每个JSON对象
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # 跳过空行
                    try:
                        json_obj = json.loads(line)
                        yield json_obj
                    except json.JSONDecodeError as e:
                        print(f"第{line_num}行JSON解析错误: {e}")
                        print(f"问题行内容: {line}")
                        continue
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

def write_jsonl(data, file_path):
    """
    将数据写入JSONL文件
    
    Args:
        data (list): 要写入的数据列表
        file_path (str): 输出文件路径
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                json_line = json.dumps(item, ensure_ascii=False)
                f.write(json_line + '\n')
        print(f"成功写入 {len(data)} 条记录到 {file_path}")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")

def main():
    # 使用全局定义的file_path
    print(f"正在读取文件: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 方法1: 一次性读取所有数据
    print("=== 方法1: 一次性读取 ===")
    data = read_jsonl(file_path)
    if data:
        print(f"第一条记录: {data[0]}")
        print(f"总记录数: {len(data)}")
    
    # 方法2: 使用生成器逐行读取（适用于大文件）
    print("\n=== 方法2: 生成器方式读取 ===")
    count = 0
    for item in read_jsonl_generator(file_path):
        count += 1
        if count <= 3:  # 只显示前3条
            print(f"第{count}条: {item}")
        elif count == 4:
            print("...")
    print(f"总记录数: {count}")

if __name__ == "__main__":
    main()
