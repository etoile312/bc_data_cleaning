#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试提示词拼接情况
检查三个步骤中知识库和提示词模板的拼接效果
"""

import json
from pathlib import Path
from scripts.step1_format_fix import FormatFix
from scripts.step2_noise_removal import NoiseRemoval
from scripts.step4_terminology_standardization import TerminologyStandardization
from scripts.llm_api import LLMAPI

def test_prompt_concatenation():
    """测试提示词拼接情况"""
    
    # 初始化LLM API（仅用于测试）
    llm_api = LLMAPI()
    
    # 测试文本
    test_text = "吉安市中心人民医院, CT诊断报告单, 检查号：CT223959, 门诊, 年龄：47岁, 姓名：欧阳建英, 性别：女, ID号：801174741, 申请科室：, 申请医生：郭小靖, 病床：, 临床诊断：乳腺恶性肿瘤, 检查项目：[胸部（包括纵隔、肺、胸膜）CT,常规], 影像表现：, 两肺纹理增多，双肺下叶各见一团片状影，范围更大者位于右肺下叶，范, 围约2.6cmX1.5cm,CT值约31HU,可见支气管截断征及分叶征，双肺另见散在, 分布条索影及直径约0.2-0.6cm的小结节影，部分钙化。右肺中叶及左肺上叶, 舌段部分支气管稍扩张，肺门影不大。右位主动脉弓及右位胸主动脉。纵隔内, 未见肿大淋巴结。双侧胸膜无增厚，胸腔未见积液。左乳切除术后改变。, 影像诊断：, u201c乳腺Ca术后u201d病史，左乳切除术后改变；, 双肺下叶异常影，结合病史考虑转移可能，与2022-12-31号CT片比较大致相仿, 双肺慢性炎性改变, 双肺多发小结节，建议随诊；, 右肺中叶及左肺上叶舌段部分支气管稍扩张；, 右位主动脉弓及右位胸主动脉。, 报告医师刘筠, 审核医师：刘筠, 注：本报告签字有效，仅供临床医师参考，不作法律依据。报告日期：2023-03-1314：54：57"
    
    print("=" * 80)
    print("测试三个步骤的提示词拼接情况")
    print("=" * 80)
    
    # Step 1: 格式纠正与拼写修复
    print("\n" + "=" * 40)
    print("Step 1: 格式纠正与拼写修复")
    print("=" * 40)
    
    format_fix = FormatFix(llm_api)
    
    # 获取知识库内容
    knowledge_base_content = json.dumps(format_fix.knowledge_base, ensure_ascii=False, indent=2)
    print(f"知识库内容长度: {len(knowledge_base_content)} 字符")
    print("知识库内容预览:")
    print(knowledge_base_content[:500] + "..." if len(knowledge_base_content) > 500 else knowledge_base_content)
    
    # 获取提示词模板
    prompt_template = format_fix.prompt_template
    print(f"\n提示词模板长度: {len(prompt_template)} 字符")
    print("提示词模板预览:")
    print(prompt_template[:500] + "..." if len(prompt_template) > 500 else prompt_template)
    
    # 拼接后的完整提示词
    full_prompt = prompt_template.format(text=test_text, knowledge_base=knowledge_base_content)
    print(f"\n拼接后完整提示词长度: {len(full_prompt)} 字符")
    print("拼接后完整提示词:")
    print("-" * 40)
    print(full_prompt)
    print("-" * 40)
    
    # Step 2: 噪声剔除
    print("\n" + "=" * 40)
    print("Step 2: 噪声剔除")
    print("=" * 40)
    
    noise_removal = NoiseRemoval(llm_api)
    
    # 获取知识库内容
    knowledge_base_str = noise_removal._format_knowledge_base()
    print(f"知识库内容长度: {len(knowledge_base_str)} 字符")
    print("知识库内容:")
    print(knowledge_base_str)
    
    # 获取提示词模板
    prompt_template = noise_removal.prompt_template
    print(f"\n提示词模板长度: {len(prompt_template)} 字符")
    print("提示词模板预览:")
    print(prompt_template[:500] + "..." if len(prompt_template) > 500 else prompt_template)
    
    # 拼接后的完整提示词
    full_prompt = prompt_template.format(text=test_text, knowledge_base=knowledge_base_str)
    print(f"\n拼接后完整提示词长度: {len(full_prompt)} 字符")
    print("拼接后完整提示词:")
    print("-" * 40)
    print(full_prompt)
    print("-" * 40)
    
    # Step 3: 术语标准化
    print("\n" + "=" * 40)
    print("Step 3: 术语标准化")
    print("=" * 40)
    
    terminology_standardization = TerminologyStandardization(llm_api)
    
    # 获取知识库内容
    knowledge_base_content = json.dumps(terminology_standardization.knowledge_base, ensure_ascii=False, indent=2)
    print(f"知识库内容长度: {len(knowledge_base_content)} 字符")
    print("知识库内容预览:")
    print(knowledge_base_content[:500] + "..." if len(knowledge_base_content) > 500 else knowledge_base_content)
    
    # 获取提示词模板
    prompt_template = terminology_standardization.prompt_template
    print(f"\n提示词模板长度: {len(prompt_template)} 字符")
    print("提示词模板预览:")
    print(prompt_template[:500] + "..." if len(prompt_template) > 500 else prompt_template)
    
    # 拼接后的完整提示词
    full_prompt = prompt_template.format(text=test_text, knowledge_base=knowledge_base_content)
    print(f"\n拼接后完整提示词长度: {len(full_prompt)} 字符")
    print("拼接后完整提示词:")
    print("-" * 40)
    print(full_prompt)
    print("-" * 40)
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_prompt_concatenation() 