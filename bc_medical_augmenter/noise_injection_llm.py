#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
import requests
import re
import string
from typing import List, Dict, Any, Optional
from config import LOCAL_LLM_API

def ask_model(query):
    url_local_model = "http://192.168.19.211:8000/v1/model/single_report"
    response = requests.post(url_local_model, json={"report": query})
    if response.status_code == 200:
        res = response.json()
        return res.get("llm_ret")

def extract_main_info(case_data):
    """
    提取病例中的姓名和年龄信息，如果没有则自动生成（女性姓名，年龄25-80）
    """
    import random
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

class LLMNoiseInjector:
    def __init__(self):
        # 噪声类型定义
        self.noise_types = [
            "administrative",      # 行政信息冗余
            "hospital_info",       # 医院/楼层/编号
            "examination",         # 检查类无关记录
            "electronic_trace",    # 电子记录痕迹
            "address",            # 地址/家庭信息
            "duplicate",          # 多次复制残留
            "covid_test",         # 核酸检测记录
            "table_header",       # 表头噪声
            "table_row_merge",    # 表格行拼接噪声
            "detailed_lab_result",# 详细检验结果噪声
            "serial_merge",       # 串行噪声
            "doctor_advice",      # 医生建议/嘱托
            "remove_space",       # 删除空格噪声
            "computer_menu"       # 电脑菜单噪声
        ]
        
        # OCR错误字符映射
        self.ocr_errors = {
            "0": ["O", "o", "D"],
            "1": ["l", "I", "i"],
            "2": ["Z", "z"],
            "3": ["8", "B"],
            "4": ["A", "a"],
            "5": ["S", "s"],
            "6": ["G", "g"],
            "7": ["T", "t"],
            "8": ["B", "b"],
            "9": ["g", "q"],
            "O": ["0", "o"],
            "l": ["1", "I"],
            "I": ["1", "l"],
            "S": ["5", "s"],
            "Z": ["2", "z"],
            "G": ["6", "g"],
            "B": ["8", "b"],
            "T": ["7", "t"]
        }

    def call_llm(self, prompt: str) -> str:
        """调用大模型生成噪声内容"""
        try:
            text = ask_model(prompt)
            if text:
                text = text.replace("**", "")
                return text
            else:
                return ""
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""

    def extract_existing_info(self, text: str) -> Dict[str, str]:
        """从文本中提取已有的信息，避免冲突"""
        existing_info = {}
        
        # 提取姓名
        name_match = re.search(r'([王李张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗][\u4e00-\u9fa5]*)\*\*', text)
        if name_match:
            surname = name_match.group(1)
            # 生成完整的姓名
            full_name = surname + random.choice(['丽', '敏', '华', '芳', '娟', '秀', '英', '红', '梅', '燕', '霞', '萍', '玲', '静', '洁', '娜', '莉', '萍', '艳', '玲'])
            existing_info['patient_name'] = full_name
        
        # 提取年龄
        age_match = re.search(r'(\d+)岁', text)
        if age_match:
            existing_info['age'] = age_match.group(1)
        
        # 提取其他信息
        if '已绝经' in text:
            existing_info['menopause'] = '已绝经'
        elif '未绝经' in text:
            existing_info['menopause'] = '未绝经'
        
        return existing_info

    def complete_or_generate_name(self, text: str) -> str:
        """补全或生成姓名"""
        # 检查是否有"**"或"某"或"*"等占位符
        if re.search(r'[王李张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗][*某]+', text):
            # 用大模型补全为真实姓名（不再用**）
            prompt = f"请将下列文本中的姓名占位符（如'王**'、'李某'）补全为真实的中文女性姓名，不能用*或某等占位符，其他内容不变：\n{text}"
            result = self.call_llm(prompt)
            return result if result else text
        else:
            # 没有姓名占位符，直接返回原文
            return text

    def enforce_main_info(self, text: str, name: str, age: str) -> str:
        """强制统一主要信息"""
        # 替换所有姓名、性别、年龄为主病例信息，性别一律为女
        text = re.sub(r'姓名[：: ]*[\u4e00-\u9fa5]{1,4}', f'姓名：{name}', text)
        text = re.sub(r'性别[：: ]*男', '性别：女', text)
        text = re.sub(r'性别[：: ]*女', '性别：女', text)
        text = re.sub(r'男', '女', text)
        text = re.sub(r'年龄[：: ]*\d{1,3}', f'年龄：{age}', text)
        # 兜底：如有"患者姓名：xxx"也替换
        text = re.sub(r'患者姓名[：: ]*[\u4e00-\u9fa5]{1,4}', f'患者姓名：{name}', text)
        # 医院名称中的**替换为真实名称
        text = re.sub(r'(医院名称[：: ]*)\*+', r'\1某某医院', text)
        text = re.sub(r'(医院[：: ]*)\*+', r'\1某某医院', text)
        text = re.sub(r'(科室[：: ]*)\*+', r'\1某某科室', text)
        text = re.sub(r'(病房[：: ]*)\*+', r'\1某某病房', text)
        text = re.sub(r'(医生[：: ]*)\*+', r'\1张伟', text)
        # 兜底：所有"**医院"直接替换为"某某医院"
        text = re.sub(r'\*+医院', '某某医院', text)
        text = re.sub(r'\*+科室', '某某科室', text)
        text = re.sub(r'\*+病房', '某某病房', text)
        text = re.sub(r'\*+医生', '张伟', text)
        return text

    def generate_administrative_noise(self, context: str = "", existing_info: Dict[str, str] = None, main_info=None) -> str:
        """生成行政信息冗余噪声"""
        name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
        age = main_info[1] if main_info and main_info[1] else (existing_info.get('age', str(random.randint(25, 80))) if existing_info else str(random.randint(25, 80)))
        prompt = f"""请生成一段医院行政信息的噪声文本，模拟真实病历中常见的OCR识别结果。要求：
1. **全部为"信息名称：具体信息"格式**，如"姓名：张三\n年龄：45岁\n性别：女"，不要出现"现住址为""联系电话是""患者应如何如何"等叙述性语言。
2. **所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁，不允许出现其他姓名、性别、年龄。**
3. **医院名称、科室、病房、医生等信息请直接虚构真实名称，不允许用*、某等遮掩符号。**
4. **信息顺序**：年龄、姓名、性别的出现顺序自然
5. **临床风格**：使用医院记录的专业术语和格式
6. **长度控制**：控制在50-100字之间
7. **真实性**：内容要像真实医院OCR识别结果
8. **性别统一**：性别统一为女性
9. **换行**：不同信息用\n分隔，段落可用\n\n分隔
10. **适当标点**：仅限冒号、逗号、句号等常见标点
11. **医生信息**：可以包含医生姓名，但不包含护士信息
姓名：{name}\n年龄：{age}岁\n性别：女\n参考上下文（如果有）：{context}\n请生成一段符合要求的行政信息噪声文本："""
        return self.call_llm(prompt)

    def generate_hospital_info_noise(self, context: str = "", main_info=None) -> str:
        """生成医院信息噪声"""
        prompt = (
            "请生成一段医院/科室/楼层/编号的噪声信息，全部为'信息名称：具体信息'格式，医院名称、科室、病房、医生等信息请直接虚构真实名称，不允许用*、某等遮掩符号。"
            "如'医院名称：杭州市第一人民医院\\n科室：肿瘤科\\n病房：3楼4区\\n医生：张伟'，不要出现'医院名称：**'或'医院名称：某医院'等遮掩。"
            "内容可包含医院名称、科室名称、楼层、病房号、医生办公室、检查科室、检查室、技师、门诊号、挂号时间、候诊区等，长度50-100字。不同信息用\\n分隔。"
        )
        return self.call_llm(prompt)

    def generate_examination_noise(self, context: str = "", main_info=None) -> str:
        """生成检查类无关记录噪声"""
        name = main_info[0] if main_info and main_info[0] else ""
        age = main_info[1] if main_info and main_info[1] else ""
        prompt = f"""请生成一段检查类无关记录的噪声信息，模拟真实病历中的常规检查记录。要求：
1. **常规检查**：包含血常规、尿常规、肝功能、肾功能、电解质、血糖、血脂等
2. **检查结果**：可以是正常、轻度异常、中度异常、重度异常等
3. **临床风格**：使用医院记录的专业术语和格式
4. **长度控制**：控制在50-200字之间
5. **真实性**：内容要像真实医院检查记录
6. **与乳腺癌无关**：这些检查与乳腺癌治疗无关，是常规检查项目
7. **姓名**：请严格使用：{name}
8. **年龄**：请严格使用：{age}
9. **不换行**：文本中不要有换行符，所有内容在一行内
10. **保留标点**：检查结果信息保留必要的标点符号
参考上下文（如果有）：{context}
请生成一段符合要求的检查记录噪声文本："""
        return self.call_llm(prompt)

    def generate_electronic_trace_noise(self, context: str = "") -> str:
        """生成电子记录痕迹噪声"""
        prompt = f"""请生成一段电子记录痕迹的噪声信息，模拟真实医院电子系统中的记录痕迹。要求：

1. **系统生成信息**：包含系统生成时间、记录时间等
2. **记录人签名**：包含记录医生、审核医生签名信息
3. **电子签名**：包含电子签名、签名时间等
4. **系统信息**：包含系统版本、操作员、工作站信息
5. **临床风格**：使用医院电子记录的专业术语和格式
6. **长度控制**：控制在50-100字之间
7. **真实性**：内容要像真实医院电子记录
8. **随机名称**：记录医生、审核医生、操作员等都要随机生成真实姓名，不要用XX代替
9. **不换行**：文本中不要有换行符，所有内容在一行内
10. **适当标点**：电子记录信息可以使用适当的标点符号
11. **医生信息**：只包含医生姓名，不包含护士信息

参考上下文（如果有）：{context}

请生成一段符合要求的电子记录痕迹噪声文本："""
        
        return self.call_llm(prompt)

    def generate_address_noise(self, context: str = "", main_info=None) -> str:
        """生成地址信息噪声"""
        name = main_info[0] if main_info and main_info[0] else ""
        age = main_info[1] if main_info and main_info[1] else ""
        prompt = f"""请生成一段地址/家庭信息的噪声信息，模拟真实病历OCR识别结果。要求：
1. **全部为"信息名称：具体信息"格式**，如"住址：浙江省杭州市西湖区文三路123号\n联系电话：13812345678\n身份证号：330105198012123456"，不要出现"现住址为""联系电话是"等叙述性语言。
2. **所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁，不允许出现其他姓名、性别、年龄。**
3. **信息顺序**：顺序自然
4. **长度控制**：控制在50-100字之间
5. **真实性**：内容要像真实医院OCR识别结果
6. **换行**：不同信息用\n分隔，段落可用\n\n分隔
7. **适当标点**：仅限冒号、逗号、句号等常见标点
8. **姓名**：请严格使用：{name}
9. **年龄**：请严格使用：{age}
参考上下文（如果有）：{context}\n请生成一段符合要求的地址信息噪声文本："""
        return self.call_llm(prompt)

    def generate_duplicate_noise(self, context: str = "") -> str:
        """生成多次复制残留噪声"""
        prompt = f"""请生成一段复制残留的噪声信息，模拟真实病历中因复制粘贴导致的少量重复内容。要求：

1. **少量重复**：同一信息在文本中最多重复1-2次
2. **复制痕迹**：体现轻微的复制粘贴痕迹
3. **临床风格**：使用医院记录的专业术语和格式
4. **长度控制**：控制在50-100字之间
5. **真实性**：内容要像真实医院记录中的轻微复制残留
6. **不换行**：文本中不要有换行符，所有内容在一行内
7. **保留标点**：诊断信息保留必要的标点符号

参考上下文（如果有）：{context}

请生成一段符合要求的复制残留噪声文本："""
        
        return self.call_llm(prompt)

    def generate_covid_test_noise(self, context: str = "") -> str:
        """生成核酸检测记录噪声"""
        prompt = f"""请生成一段核酸检测记录的噪声信息，模拟真实病历中的核酸检测记录。要求：

1. **核酸检测**：包含新型冠状病毒核酸检测、抗体检测、抗原检测等
2. **检测结果**：包含阴性、阳性等结果
3. **检测时间**：包含检测时间、报告时间等
4. **临床风格**：使用医院记录的专业术语和格式
5. **长度控制**：控制在50-100字之间
6. **真实性**：内容要像真实医院核酸检测记录
7. **不换行**：文本中不要有换行符，所有内容在一行内
8. **保留标点**：检测结果信息保留必要的标点符号

参考上下文（如果有）：{context}

请生成一段符合要求的核酸检测记录噪声文本："""
        
        return self.call_llm(prompt)

    def generate_table_header_noise(self, context="", main_info=None):
        """生成表头噪声"""
        name = main_info[0] if main_info and main_info[0] else "请自动生成真实女性姓名"
        age = main_info[1] if main_info and main_info[1] else ""
        prompt = (
            f"请生成一段医院报告表头的OCR识别文本，全部为'信息名称：具体信息'格式，如'报告编号：12345\\n姓名：张三\\n性别：女\\n年龄：45岁'，不要出现叙述性语言，姓名请严格使用：{name}，年龄请严格使用：{age}，"
            f"所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁，不允许出现其他姓名、性别、年龄。"
            "模拟真实病历报告表头OCR识别结果，内容可有部分字段缺失或顺序混乱，长度30-80字。"
            "不同信息用\\n分隔，段落可用\\n\\n分隔。"
        )
        return self.call_llm(prompt)

    def generate_table_row_merge_noise(self, context="", main_info=None):
        """生成表格行拼接噪声"""
        name = main_info[0] if main_info and main_info[0] else ""
        age = main_info[1] if main_info and main_info[1] else ""
        prompt = (
            f"请生成一段模拟表格两列内容被OCR识别后拼接在一起的文本，姓名请严格使用：{name}，年龄请严格使用：{age}，"
            f"所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁，不允许出现其他姓名、性别、年龄。"
            "如'白细胞:5.2 红细胞:4.3 血红蛋白:120 血小板:200'，要求内容为常见血常规或生化检查项目，长度50-120字。不同项目用\\n分隔，段落可用\\n\\n分隔。"
        )
        return self.call_llm(prompt)

    def generate_detailed_lab_result_noise(self, context="", main_info=None):
        """生成详细检验结果噪声"""
        name = main_info[0] if main_info and main_info[0] else ""
        age = main_info[1] if main_info and main_info[1] else ""
        prompt = (
            f"请生成一段血常规或肺CT等详细检验结果的OCR识别文本，姓名请严格使用：{name}，年龄请严格使用：{age}，"
            f"所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁，不允许出现其他姓名、性别、年龄。"
            "列出10项常见指标及其数值、单位、参考范围，全部为'项目名称：数值 单位 参考范围'格式，不要出现叙述性语言，"
            "模拟OCR错误（单位丢失、标点混乱、拼接、换行错位），不同项目用\\n分隔，段落可用\\n\\n分隔，总长度100-300字。"
        )
        return self.call_llm(prompt)

    def generate_serial_merge_noise(self, context="", main_info=None):
        """生成串行噪声"""
        name = main_info[0] if main_info and main_info[0] else ""
        age = main_info[1] if main_info and main_info[1] else ""
        prompt = (
            f"请生成一段模拟多份报告内容被OCR识别后串行拼接在一起的文本，姓名请严格使用：{name}，年龄请严格使用：{age}，"
            f"所有报告、所有字段中的姓名、性别、年龄都必须与主病例一致，姓名：{name}，性别：女，年龄：{age}岁，不允许出现其他姓名、性别、年龄。"
            "如'报告编号：12345\\n姓名：李华\\n性别：女\\n年龄：45岁\\n血常规\\n白细胞:5.2 红细胞:4.3 血红蛋白:120 血小板:200\\n报告编号：67890\\n姓名：王芳\\n性别：女\\n年龄：52岁\\n生化检查\\n谷丙转氨酶:20 谷草转氨酶:18'，"
            "要求内容为多份不同检查报告的内容直接拼接，部分字段缺失或顺序混乱，长度80-200字。不同项目用\\n分隔，段落可用\\n\\n分隔。"
        )
        return self.call_llm(prompt)

    def generate_doctor_advice_noise(self, context=""):
        """生成医生建议噪声"""
        prompt = (
            "请生成一段医生对患者的建议或嘱托，前面加'医生建议：'或'诊断建议：'，内容包括用药、复查、生活方式、注意事项等，"
            "要求风格贴近真实病历，简明扼要，长度30-80字，全部内容只用换行（\\n）分隔，不要出现空行，不要用\\n\\n。可包含常见叮嘱如定期复查、按时服药、注意休息、饮食清淡、避免劳累等。"
        )
        return self.call_llm(prompt)

    def generate_remove_space_noise(self, text: str) -> str:
        """删除空格噪声：随机删除部分空格"""
        import random
        chars = list(text)
        for i in range(len(chars)):
            if chars[i] == ' ' and random.random() < 0.5:
                chars[i] = ''
        return ''.join(chars)

    def generate_computer_menu_noise(self, context: str = "") -> str:
        """生成电脑菜单噪声，模拟OCR识别电脑屏幕菜单内容"""
        prompt = (
            "请生成一段模拟电脑屏幕菜单的OCR识别噪声文本，内容包括如‘文件 编辑 查看 工具 帮助’等菜单项，"
            "可以包含快捷键、菜单分隔符、英文单词、乱码符号等，长度30-80字，内容风格贴近Windows或医院信息系统菜单，"
            "可出现如‘File Edit View Tools Help 设置 退出 Alt+F4 Ctrl+S’等，允许部分错别字、拼写错误、符号混杂。"
            f"参考上下文（如果有）：{context}\n请生成一段电脑菜单噪声文本："
        )
        return self.call_llm(prompt)

    def generate_noise_block(self, noise_type: str, context: str = "", existing_info: Dict[str, str] = None, main_info=None) -> str:
        """根据噪声类型生成对应的噪声块"""
        if noise_type == "administrative":
            return self.generate_administrative_noise(context, existing_info, main_info)
        elif noise_type == "hospital_info":
            return self.generate_hospital_info_noise(context, main_info)
        elif noise_type == "examination":
            return self.generate_examination_noise(context, main_info)
        elif noise_type == "electronic_trace":
            return self.generate_electronic_trace_noise(context)
        elif noise_type == "address":
            return self.generate_address_noise(context, main_info)
        elif noise_type == "duplicate":
            return self.generate_duplicate_noise(context)
        elif noise_type == "covid_test":
            return self.generate_covid_test_noise(context)
        elif noise_type == "table_header":
            return self.generate_table_header_noise(context, main_info)
        elif noise_type == "table_row_merge":
            return self.generate_table_row_merge_noise(context, main_info)
        elif noise_type == "detailed_lab_result":
            return self.generate_detailed_lab_result_noise(context, main_info)
        elif noise_type == "serial_merge":
            return self.generate_serial_merge_noise(context, main_info)
        elif noise_type == "doctor_advice":
            return self.generate_doctor_advice_noise(context)
        elif noise_type == "remove_space":
            # 删除空格噪声直接对context处理
            return self.generate_remove_space_noise(context)
        elif noise_type == "computer_menu":
            return self.generate_computer_menu_noise(context)
        else:
            return ""

    def clean_text(self, text: str) -> str:
        """清理文本，去掉**符号，统一性别为女"""
        # 去掉**符号
        text = text.replace("**", "")
        
        # 统一性别为女（包括性别字段和描述）
        text = re.sub(r'性别[：: ]*男', '性别：女', text)
        text = re.sub(r'性别[：: ]*女', '性别：女', text)
        text = re.sub(r'男', '女', text)
        
        # 去掉换行符，合并为一行
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 去掉多余的空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def inject_content_noise(self, text: str, main_info=None) -> str:
        """第一阶段：病历内容级噪声注入"""
        # 清理原文
        text = self.clean_text(text)
        
        # 提取已有信息
        existing_info = self.extract_existing_info(text)
        
        # 提高串行、截断、ocr错乱等噪声类型的采样概率
        high_prob_types = ["serial_merge", "detailed_lab_result", "table_row_merge"]
        all_types = self.noise_types + high_prob_types * 2  # 这些类型概率提升
        
        # 在文本前后随机添加0-3类噪声
        front_noise_count = random.randint(0, 3)
        back_noise_count = random.randint(0, 3)
        
        front_noises = []
        back_noises = []
        
        # 生成前置噪声
        for _ in range(front_noise_count):
            noise_type = random.choice(all_types)
            noise_block = self.generate_noise_block(noise_type, text[:100], existing_info, main_info)
            if noise_block:
                front_noises.append(noise_block)
        
        # 生成后置噪声
        for _ in range(back_noise_count):
            noise_type = random.choice(all_types)
            noise_block = self.generate_noise_block(noise_type, text[-100:], existing_info, main_info)
            if noise_block:
                back_noises.append(noise_block)
        
        # 拼接噪声和原文（不换行）
        result = ""
        if front_noises:
            result += " ".join(front_noises) + " "
        result += text
        if back_noises:
            result += " " + " ".join(back_noises)
        
        return result

    def add_character_level_noise(self, text: str) -> str:
        """添加字符级噪声，模拟OCR识别错误"""
        # 1. 去掉一半的空格
        if random.random() < 0.5:
            text = re.sub(r'\s+', '', text)
        # 2. 随机添加更多乱码符号
        if random.random() < 0.5:
            noise_symbols = ['·', '•', '●', '◆', '★', '☆', '※', '→', '←', '—', '–', '…', '', '~', '!', '?', '#', '$', '%', '&', '*', '@', '‰', '¤', '¢', '§', '¤', '¿', '¡', '™', '©', '®', 'µ', 'Ω', 'Ξ', 'Ψ', '∑', '∏', '∫', '√', '∝', '∞', '≡', '≠', '≤', '≥', '⊕', '⊙', '⊥', '⊿', '⊗', '⊙', '⊥', '⊿', '∷', '∵', '∴', '∠', '∟', '∩', '∪', '∈', '∷', '∽', '≌', '≒', '≦', '≧', '≮', '≯', '≒', '≡', '≦', '≧', '≮', '≯', '≒', '≡', '≦', '≧', '≮', '≯']
            for _ in range(random.randint(2, 8)):
                pos = random.randint(0, len(text))
                text = text[:pos] + random.choice(noise_symbols) + text[pos:]
        # 3. 随机添加额外字符
        if random.random() < 0.1:  # 10%概率添加额外字符
            extra_chars = [' ', '  ', '\t', '|', '-', '_']
            if len(text) > 10:
                pos = random.randint(0, len(text))
                text = text[:pos] + random.choice(extra_chars) + text[pos:]
        
        return text

    def random_truncate(self, text: str) -> str:
        """随机截断文本，模拟随机取一段文字的情况"""
        if len(text) < 50:  # 文本太短不截断
            return text
        
        # 随机决定是否截断开头或结尾
        truncate_type = random.choice(['start', 'end', 'both', 'none'])
        
        if truncate_type == 'none':
            return text
        
        # 计算截断长度（10%-30%）
        truncate_ratio = random.uniform(0.1, 0.3)
        truncate_length = int(len(text) * truncate_ratio)
        
        if truncate_type == 'start':
            return text[truncate_length:]
        elif truncate_type == 'end':
            return text[:-truncate_length]
        elif truncate_type == 'both':
            return text[truncate_length:-truncate_length]
        
        return text

    def add_final_character_noise(self, text: str) -> str:
        """添加最终字符级噪声"""
        import unicodedata
        # 1. 字符替换错误/全角半角混乱
        char_map = {
            'A': ['Ａ', 'Λ', '4'], 'B': ['Ｂ', 'ß'], 'C': ['Ｃ', '匚'],
            '1': ['l', 'I', '１'], '0': ['O', '０', '●'], 'O': ['0', '〇', 'Ｏ'],
            'a': ['@', 'ａ'], 'e': ['€', 'ｅ'], 'i': ['！', 'ｉ'], ':': ['：'], ',': ['，'], '.': ['。'],
            '-': ['–', '—', '－'], ' ': ['　', ''], 'n': ['η', 'ń'],
        }
        text_chars = list(text)
        for i, c in enumerate(text_chars):
            if c in char_map and random.random() < 0.1:
                text_chars[i] = random.choice(char_map[c])
        text = ''.join(text_chars)

        # 2. 非标准符号/乱码字符
        noise_symbols = ['·', '•', '●', '◆', '★', '☆', '※', '→', '←', '—', '–', '…', '', '~', '!', '?', '#', '$', '%', '&', '*', '@']
        if random.random() < 0.2:
            pos = random.randint(0, len(text))
            text = text[:pos] + random.choice(noise_symbols) + text[pos:]

        # 3. 标点混乱
        punct_map = {',': ['，', ',', '、'], '.': ['。', '.', '·'], ':': ['：', ':'], ';': ['；', ';']}
        for p, opts in punct_map.items():
            if random.random() < 0.2:
                text = text.replace(p, random.choice(opts))

        # 4. 字符缺失/粘连
        if random.random() < 0.4:
            text = re.sub(r'([：:])\s*', '', text)  # 去掉冒号后的空格
        if random.random() < 0.1:
            text = re.sub(r'\s+', '', text, count=1)  # 去掉一次空格

        # 5. 行内错行/断行
        if random.random() < 0.2 and len(text) > 20:
            pos = random.randint(10, len(text)-5)
            text = text[:pos] + '\n' + text[pos:]

        # 6. 表格结构丢失（去掉分隔符）
        if random.random() < 0.2:
            text = re.sub(r'[|\t]', '', text)

        return text

    def inject_ocr_noise(self, text: str) -> str:
        """第二阶段：OCR风格格式级噪声注入"""
        # 1. 字段粘连（去除标点和空格）
        if random.random() < 0.3:  # 30%概率进行字段粘连
            # 随机选择一些标点符号和空格进行删除
            text = re.sub(r'[，。；：！？、]', '', text, count=random.randint(1, 3))
            text = re.sub(r'\s+', '', text, count=random.randint(1, 2))
        
        # 2. 换行错误（由于我们要求不换行，这里主要是处理可能的残留换行）
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 3. 字符乱码
        if random.random() < 0.3:  # 15%概率出现字符乱码
            # 随机替换一些字符为OCR错误字符
            for char, replacements in self.ocr_errors.items():
                if random.random() < 0.05 and char in text:
                    text = text.replace(char, random.choice(replacements), 1)
        
        # 4. 排版错乱
        if random.random() < 0.2:  # 10%概率出现排版错乱
            # 随机插入一些空格或制表符
            words = text.split()
            for i in range(len(words)):
                if random.random() < 0.05:  # 5%概率在单词间插入额外空格
                    words[i] = words[i] + ' ' * random.randint(1, 3)
            text = ' '.join(words)
        
        # 5. 错别字注入
        if random.random() < 0.3:  # 10%概率出现错别字
            # 常见错别字映射
            typo_mapping = {
                "的": ["得", "地"],
                "是": ["事", "时"],
                "有": ["又", "右"],
                "在": ["再", "载"],
                "和": ["合", "河"],
                "与": ["于", "雨"],
                "或": ["和", "活"],
                "及": ["即", "级"],
                "等": ["等", "邓"],
                "为": ["位", "未"]
            }
            
            for char, replacements in typo_mapping.items():
                if random.random() < 0.1 and char in text:
                    text = text.replace(char, random.choice(replacements), 1)
        
        # 6. 添加字符级噪声
        text = self.add_character_level_noise(text)
        
        # 7. 随机截断
        text = self.random_truncate(text)
        
        # 8. 最后添加字符级噪声
        text = self.add_final_character_noise(text)
        
        return text

    def inject_noise(self, text: str, case_data=None) -> str:
        """完整的噪声注入流程"""
        # 先补全或生成姓名
        main_info = extract_main_info(case_data) if case_data else ("", "")
        text = self.complete_or_generate_name(text)
        
        # 第一阶段：内容级噪声注入
        text_with_content_noise = self.inject_content_noise(text, main_info)
        
        # 第二阶段：OCR风格噪声注入
        text_with_ocr_noise = self.inject_ocr_noise(text_with_content_noise)
        
        # 后处理：强制所有姓名、性别、年龄一致
        text_with_ocr_noise = self.enforce_main_info(text_with_ocr_noise, main_info[0], main_info[1])
        
        return text_with_ocr_noise

def main():
    """主函数：处理已生成的临床风格文本，注入噪声"""
    # 初始化噪声注入器
    noise_injector = LLMNoiseInjector()
    
    # 检查是否有生成的病例文件
    if not os.path.exists("data/generated_cases"):
        print("错误：data/generated_cases目录不存在，请先运行text_generate_cases.py生成临床风格文本")
        return
    
    case_files = [f for f in os.listdir("data/generated_cases") if f.endswith('.json')]
    if not case_files:
        print("错误：没有找到生成的病例文件，请先运行text_generate_cases.py生成临床风格文本")
        return
    
    print(f"找到 {len(case_files)} 个病例文件，开始注入噪声...")
    
    for idx, case_file in enumerate(case_files):
        print(f"处理第 {idx+1}/{len(case_files)} 个文件: {case_file}")
        
        # 读取病例文件
        with open(f"data/generated_cases/{case_file}", 'r', encoding='utf-8') as f:
            case_data = json.load(f)
        
        # 获取临床风格文本
        clinical_text = case_data.get("text", "")
        if not clinical_text:
            print(f"警告：{case_file} 中没有找到文本内容")
            continue
        
        # 注入噪声
        noisy_text = noise_injector.inject_noise(clinical_text, case_data)
        
        # 只写 noisy_text 到 json
        case_data["noisy_text"] = noisy_text
        with open(f"data/generated_cases/{case_file}", "w", encoding="utf-8") as f:
            json.dump(case_data, f, ensure_ascii=False, indent=2)
        
        # 追加 noisy_text 到 txt 文件，和原text之间隔三行，处理/n和/n/n
        txt_file = f"data/generated_cases/{case_file.replace('.json', '.txt')}"
        noisy_text_for_txt = noisy_text.replace('/n/n', '\n\n').replace('/n', '\n')
        if os.path.exists(txt_file):
            with open(txt_file, "a", encoding="utf-8") as ftxt:
                ftxt.write("\n\n\n" + noisy_text_for_txt)
        else:
            with open(txt_file, "w", encoding="utf-8") as ftxt:
                ftxt.write(clinical_text + "\n\n\n" + noisy_text_for_txt)
        
        print(f"已写入噪声文本到: data/generated_cases/{case_file}")
    
    print("噪声注入完成！")

if __name__ == "__main__":
    main() 