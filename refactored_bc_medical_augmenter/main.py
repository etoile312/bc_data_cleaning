"""
乳腺癌医学数据增强系统 - 主入口脚本
重构版本：模块化、配置化、可维护的医学数据生成系统

功能模块：
1. 结构化数据生成 (structured/)
2. 临床风格文本生成 (clinical/)
3. 噪声注入 (noise/)
4. 通用API调用 (core/)
5. 配置管理 (config/)
"""

import os
import sys
import argparse
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_structured_generation():
    """运行结构化数据生成"""
    print("🚀 开始结构化数据生成...")
    try:
        from structured.generate_structured import StructuredDataGenerator
        generator = StructuredDataGenerator()
        results = generator.run_full_pipeline(
            samples_per_group=100,
            n_cases=100,
            validate=True
        )
        print("✅ 结构化数据生成完成")
        return True
    except Exception as e:
        print(f"❌ 结构化数据生成失败: {e}")
        return False

def run_clinical_generation():
    """运行临床风格文本生成"""
    print("🚀 开始临床风格文本生成...")
    try:
        from clinical.generate_clinical import ClinicalTextGenerator
        generator = ClinicalTextGenerator()
        results = generator.run()
        print("✅ 临床风格文本生成完成")
        return True
    except Exception as e:
        print(f"❌ 临床风格文本生成失败: {e}")
        return False

def run_noise_injection():
    """运行噪声注入"""
    print("🚀 开始噪声注入...")
    try:
        from noise.generate_noisy import NoisyTextGenerator
        generator = NoisyTextGenerator()
        results = generator.run()
        print("✅ 噪声注入完成")
        return True
    except Exception as e:
        print(f"❌ 噪声注入失败: {e}")
        return False

def run_full_pipeline():
    """运行完整的数据生成流水线"""
    print("🎯 开始完整的数据生成流水线...")
    
    success = True
    
    # 1. 结构化数据生成
    if not run_structured_generation():
        success = False
        print("❌ 结构化数据生成失败，停止后续流程")
        return False
    
    # 2. 临床风格文本生成
    if not run_clinical_generation():
        success = False
        print("❌ 临床风格文本生成失败，停止后续流程")
        return False
    
    # 3. 噪声注入
    if not run_noise_injection():
        success = False
        print("❌ 噪声注入失败")
        return False
    
    if success:
        print("🎉 完整数据生成流水线执行成功！")
        print("\n📊 生成结果统计:")
        print("   - 结构化病例数据: data/combined_cases.json")
        print("   - 临床风格文本: data/generated_cases/")
        print("   - 带噪声文本: data/generated_cases/ (带_noisy后缀)")
    
    return success

def test_modules():
    """测试各个模块"""
    print("🧪 开始模块测试...")
    
    tests = [
        ("结构化数据模块", test_structured_module),
        ("临床文本模块", test_clinical_module),
        ("噪声注入模块", test_noise_module),
        ("API调用模块", test_api_module)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n测试 {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"✅ {test_name} 测试{'通过' if success else '失败'}")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print(f"\n📋 测试结果汇总:")
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   - {test_name}: {status}")
    
    return all(success for _, success in results)

def test_structured_module():
    """测试结构化数据模块"""
    try:
        from structured.field_parser import FieldRuleParser
        from structured.field_sampler import FieldSampler
        from structured.segment_groups import SEGMENT_GROUPS
        
        # 测试字段解析器
        parser = FieldRuleParser('rules/breast_cancer_rules.json')
        fields = parser.get_field_defs()
        assert len(fields) > 0, "字段定义不能为空"
        
        # 测试字段采样器
        sampler = FieldSampler(parser.get_field_defs(), parser.get_logic_rules())
        sample = sampler.sample_basic_info(['年龄', '绝经状态'])
        assert '年龄' in sample, "采样结果应包含年龄字段"
        
        return True
    except Exception as e:
        print(f"结构化模块测试失败: {e}")
        return False

def test_clinical_module():
    """测试临床文本模块"""
    try:
        from clinical.preprocess_rules import preprocess_case_fields
        from clinical.text_generator import generate_clinical_text
        
        # 测试字段预处理
        test_case = {'年龄': '45', '绝经状态': '否'}
        processed = preprocess_case_fields(test_case)
        assert 'expressions' in processed, "预处理应包含expressions字段"
        
        return True
    except Exception as e:
        print(f"临床模块测试失败: {e}")
        return False

def test_noise_module():
    """测试噪声注入模块"""
    try:
        from noise.noise_injector import NoiseInjector
        from noise.noise_types import extract_main_info
        
        # 测试噪声注入器
        injector = NoiseInjector()
        test_text = "患者王**，女，56岁。"
        noisy_text = injector.inject_noise(test_text)
        assert len(noisy_text) > 0, "噪声注入应返回非空文本"
        
        # 测试主要信息提取
        test_case = {'name': '王丽', 'age': '45'}
        name, age = extract_main_info(test_case)
        assert name == '王丽', "姓名提取错误"
        assert age == '45', "年龄提取错误"
        
        return True
    except Exception as e:
        print(f"噪声模块测试失败: {e}")
        return False

def test_api_module():
    """测试API调用模块"""
    try:
        from core.llm_api import load_api_config, get_default_api_config
        
        # 测试配置加载
        config = load_api_config()
        assert 'url' in config, "配置应包含URL"
        
        # 测试默认配置
        default_config = get_default_api_config()
        assert 'url' in default_config, "默认配置应包含URL"
        
        return True
    except Exception as e:
        print(f"API模块测试失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='乳腺癌医学数据增强系统')
    parser.add_argument('--mode', choices=['structured', 'clinical', 'noise', 'full', 'test'], 
                       default='full', help='运行模式')
    parser.add_argument('--config', type=str, help='配置文件路径')
    
    args = parser.parse_args()
    
    print("🏥 乳腺癌医学数据增强系统 (重构版本)")
    print("=" * 50)
    
    if args.mode == 'structured':
        run_structured_generation()
    elif args.mode == 'clinical':
        run_clinical_generation()
    elif args.mode == 'noise':
        run_noise_injection()
    elif args.mode == 'full':
        run_full_pipeline()
    elif args.mode == 'test':
        test_modules()
    else:
        print("❌ 未知的运行模式")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 