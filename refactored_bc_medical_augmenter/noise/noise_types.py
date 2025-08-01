"""
噪声类型定义与生成模块。
每种噪声类型一个函数，便于统一管理和扩展。
"""

import random
import re
import string
from typing import Dict, Any, Optional, Tuple

from core.llm_api import call_llm

def extract_main_info(case_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    提取病例中的姓名和年龄信息，如果没有则自动生成（女性姓名，年龄25-80）
    """
    # 常见中文女性姓和名
    surnames = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    female_names = ["丽", "敏", "华", "芳", "娟", "秀", "英", "红", "梅", "燕", "霞", "萍", "玲", "静", "洁", "娜", "莉", "艳", "玲", "倩", "雪", "玉", "丹", "婷", "慧", "璐", "佳", "璇", "悦", "菲", "璐"]
    
    name = case_data.get("name", "") or case_data.get("姓名", "")
    age = case_data.get("age", "") or case_data.get("年龄", "")
    
    # 兼容数字型年龄
    if isinstance(age, int):
        age = str(age)
    elif isinstance(age, str):
        age = ''.join(filter(str.isdigit, age))
    
    # 如果没有姓名，自动生成
    if not name:
        name = random.choice(surnames) + random.choice(female_names)
    
    # 如果没有年龄，自动生成
    if not age:
        age = str(random.randint(25, 80))
    
    return name, age

def generate_administrative_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成行政信息噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段医院行政信息的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 全部为"信息名称：具体信息"格式，如"姓名：{name}\\n年龄：{age}岁\\n性别：女"。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 医院名称、科室、病房、医生等信息请直接虚构真实名称，不允许用*、某等遮掩符号。
4. 信息顺序自然，长度控制在50-100字。
5. 参考上下文（如果有）：{context}
请生成一段符合要求的行政信息噪声文本："""
    
    return call_llm(prompt)

def generate_hospital_info_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成医院信息噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段医院楼层、病房、编号等信息的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含病房号、楼层、床位号、住院号等信息。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 信息顺序自然，长度控制在30-80字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的医院信息噪声文本："""
    
    return call_llm(prompt)

def generate_examination_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成检查类无关记录噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段检查类无关记录的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含心电图、血压、体温、血常规等与乳腺癌无关的检查记录。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 检查结果要真实合理，长度控制在50-200字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的检查记录噪声文本："""
    
    return call_llm(prompt)

def generate_electronic_trace_noise(context: str = "") -> str:
    """生成电子记录痕迹噪声"""
    prompt = f"""请生成一段电子记录痕迹的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含时间戳、操作员ID、系统信息、打印时间等电子痕迹。
2. 格式如"打印时间：2024-01-15 14:30:25\\n操作员：张三\\n系统版本：v2.1.3"。
3. 信息真实合理，长度控制在50-100字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的电子记录痕迹噪声文本："""
    
    return call_llm(prompt)

def generate_address_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成地址/家庭信息噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段地址、家庭信息的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含患者地址、联系电话、紧急联系人等信息。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 地址信息要真实合理，长度控制在50-100字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的地址信息噪声文本："""
    
    return call_llm(prompt)

def generate_duplicate_noise(context: str = "") -> str:
    """生成多次复制残留噪声"""
    prompt = f"""请生成一段多次复制残留的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含重复的字段名、重复的内容片段、格式混乱等。
2. 模拟复制粘贴导致的重复和错乱。
3. 长度控制在50-100字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的重复残留噪声文本："""
    
    return call_llm(prompt)

def generate_covid_test_noise(context: str = "") -> str:
    """生成核酸检测记录噪声"""
    prompt = f"""请生成一段核酸检测记录的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含核酸检测结果、检测时间、检测机构等信息。
2. 格式如"核酸检测：阴性\\n检测时间：2024-01-10\\n检测机构：XX医院"。
3. 信息真实合理，长度控制在30-80字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的核酸检测记录噪声文本："""
    
    return call_llm(prompt)

def generate_table_header_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成表头噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段表格表头的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含表格的表头信息，如"姓名 年龄 性别 科室 病房号"。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 表头格式要真实合理，长度控制在30-80字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的表头噪声文本："""
    
    return call_llm(prompt)

def generate_table_row_merge_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成表格行拼接噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段表格行拼接的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含表格行的数据，如"{name} {age} 女 肿瘤科 301"。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 数据格式要真实合理，长度控制在30-80字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的表格行噪声文本："""
    
    return call_llm(prompt)

def generate_detailed_lab_result_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成详细检验结果噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段详细检验结果的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含血常规、生化等详细检验结果。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 检验结果要真实合理，长度控制在50-200字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的详细检验结果噪声文本："""
    
    return call_llm(prompt)

def generate_serial_merge_noise(context: str = "", main_info: Optional[Tuple[str, str]] = None) -> str:
    """生成串行噪声"""
    name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
    age = main_info[1] if main_info and main_info[1] else str(random.randint(25, 80))
    
    prompt = f"""请生成一段串行信息的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含序列号、流水号、编号等信息。
2. 所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁。
3. 信息格式要真实合理，长度控制在30-80字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的串行信息噪声文本："""
    
    return call_llm(prompt)

def generate_doctor_advice_noise(context: str = "") -> str:
    """生成医生建议/嘱托噪声"""
    prompt = f"""请生成一段医生建议或嘱托的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. 包含医生的建议、嘱托、注意事项等。
2. 格式如"医生建议：定期复查\\n注意事项：避免剧烈运动"。
3. 内容要真实合理，长度控制在50-100字。
4. 参考上下文（如果有）：{context}
请生成一段符合要求的医生建议噪声文本："""
    
    return call_llm(prompt)

def generate_remove_space_noise(text: str) -> str:
    """生成删除空格噪声"""
    # 随机删除一些空格
    words = text.split()
    if len(words) <= 1:
        return text
    
    # 随机选择一些位置删除空格
    num_to_remove = max(1, len(words) // 20)  # 删除约5%的空格
    positions = random.sample(range(len(words) - 1), min(num_to_remove, len(words) - 1))
    
    result = []
    for i, word in enumerate(words):
        result.append(word)
        if i not in positions and i < len(words) - 1:
            result.append(" ")
    
    return "".join(result)

def generate_computer_menu_noise(context: str = "") -> str:
    """生成电脑菜单噪声"""
    prompt = f"""请生成一段模拟电脑屏幕菜单的OCR识别噪声文本，内容包括如'文件 编辑 查看 工具 帮助'等菜单项，可以包含快捷键、菜单分隔符、英文单词、乱码符号等，长度30-80字左右，内容风格贴近Windows或医院信息系统菜单，可出现如'File Edit View Tools Help 设置 退出 Alt+F4 Ctrl+S'等，允许部分错别字、拼写错误、符号混杂。
参考上下文（如果有）：{context}
请生成一段电脑菜单噪声文本："""
    
    return call_llm(prompt)

# 噪声类型映射
NOISE_TYPE_MAP = {
    'administrative': generate_administrative_noise,
    'hospital_info': generate_hospital_info_noise,
    'examination': generate_examination_noise,
    'electronic_trace': generate_electronic_trace_noise,
    'address': generate_address_noise,
    'duplicate': generate_duplicate_noise,
    'covid_test': generate_covid_test_noise,
    'table_header': generate_table_header_noise,
    'table_row_merge': generate_table_row_merge_noise,
    'detailed_lab_result': generate_detailed_lab_result_noise,
    'serial_merge': generate_serial_merge_noise,
    'doctor_advice': generate_doctor_advice_noise,
    'remove_space': generate_remove_space_noise,
    'computer_menu': generate_computer_menu_noise
} 