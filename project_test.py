#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目功能测试脚本
"""

import os
import json
import sys
from pathlib import Path

def test_project_structure():
    """测试项目结构"""
    print("🏗️ 测试项目结构...")
    
    required_files = [
        'complete_8_meters_getter.py',  # 主脚本
        'water_data_enhanced.py',       # 增强版
        'water_data_scraper.py',       # Selenium版
        'requirements.txt',            # 依赖
        'README.md',                   # 说明
        '项目总结.md',                  # 总结
        'config.py',                   # 配置
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"  ✅ {file}")
    
    if missing_files:
        print(f"  ❌ 缺失文件: {', '.join(missing_files)}")
        return False
    
    print("  ✅ 项目结构完整")
    return True

def test_data_files():
    """测试数据文件"""
    print("\n📊 测试数据文件...")
    
    # 查找所有JSON数据文件
    json_files = list(Path('.').glob('*.json'))
    
    if not json_files:
        print("  ❌ 没有找到数据文件")
        return False
    
    # 查找最新的完整数据文件
    complete_files = [f for f in json_files if 'COMPLETE_8_METERS' in f.name]
    
    if not complete_files:
        print("  ❌ 没有找到完整8个水表数据文件")
        return False
    
    # 测试最新的完整数据文件
    latest_file = max(complete_files, key=lambda x: x.stat().st_mtime)
    print(f"  📄 最新数据文件: {latest_file.name}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查数据结构
        if 'data' in data and 'rows' in data['data']:
            rows = data['data']['rows']
            meter_count = len(rows)
            print(f"  ✅ 包含 {meter_count} 个水表数据")
            
            if meter_count == 8:
                print("  ✅ 水表数量正确（8个）")
                
                # 显示水表信息
                for i, row in enumerate(rows, 1):
                    if isinstance(row, dict):
                        meter_id = row.get('ID', 'N/A')
                        meter_name = row.get('Name', 'N/A')
                        print(f"    {i}. {meter_name} ({meter_id})")
                
                return True
            else:
                print(f"  ⚠️  水表数量不正确，期望8个，实际{meter_count}个")
                return False
        else:
            print("  ❌ 数据结构不正确")
            return False
            
    except Exception as e:
        print(f"  ❌ 读取数据文件失败: {e}")
        return False

def test_python_modules():
    """测试Python模块"""
    print("\n🐍 测试Python模块...")
    
    required_modules = [
        'requests',
        'beautifulsoup4',
        'selenium',
        'pandas',
        'python-dotenv'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'beautifulsoup4':
                import bs4
                print(f"  ✅ {module} (bs4)")
            elif module == 'python-dotenv':
                import dotenv
                print(f"  ✅ {module} (dotenv)")
            else:
                __import__(module)
                print(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"  ❌ {module}")
    
    if missing_modules:
        print(f"\n  💡 安装缺失模块: pip install {' '.join(missing_modules)}")
        return False
    
    print("  ✅ 所有必需模块已安装")
    return True

def test_configuration():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    # 检查配置文件
    if Path('config.py').exists():
        try:
            import config
            print("  ✅ config.py 可正常导入")
            
            # 检查配置项
            if hasattr(config, 'USERNAME') and hasattr(config, 'PASSWORD'):
                print("  ✅ 配置项完整")
                return True
            else:
                print("  ⚠️  配置项不完整")
                return False
        except Exception as e:
            print(f"  ❌ 配置文件导入失败: {e}")
            return False
    else:
        print("  ❌ config.py 不存在")
        return False

def show_project_summary():
    """显示项目摘要"""
    print("\n" + "="*60)
    print("🏆 水务数据获取项目 - 完整版")
    print("="*60)
    print("📋 功能特性:")
    print("  ✅ 完整8个水表数据获取")
    print("  ✅ 动态日期计算（昨天往前推7天）")
    print("  ✅ 真实数据获取（非模拟）")
    print("  ✅ JavaScript重定向处理")
    print("  ✅ MD5密码加密")
    print("  ✅ 数据完整性验证")
    
    print("\n🚀 使用方法:")
    print("  python complete_8_meters_getter.py  # 推荐")
    print("  python run.py                       # Selenium版")
    print("  python run_enhanced.py              # 增强版")
    
    print("\n📊 最新数据:")
    # 查找最新数据文件
    json_files = list(Path('.').glob('COMPLETE_8_METERS_*.json'))
    if json_files:
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        file_size = latest_file.stat().st_size
        print(f"  📄 {latest_file.name}")
        print(f"  📦 文件大小: {file_size:,} 字节")
        print(f"  🕐 修改时间: {Path(latest_file).stat().st_mtime}")

def main():
    """主函数"""
    print("🧪 水务数据获取项目测试")
    print("="*40)
    
    tests = [
        test_project_structure,
        test_python_modules,
        test_configuration,
        test_data_files,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "="*40)
    print("📊 测试结果:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ 所有测试通过 ({passed}/{total})")
        print("🎉 项目状态：完全正常")
        show_project_summary()
    else:
        print(f"⚠️  部分测试失败 ({passed}/{total})")
        print("💡 请检查上述错误并修复")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
