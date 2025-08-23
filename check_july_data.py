#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有JSON文件中是否包含7月22日的数据
"""

import json
import glob
import os

def check_file_for_july_data(filename):
    """检查文件是否包含7月数据"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'data' not in data or 'rows' not in data['data']:
            return None
        
        dates = set()
        for row in data['data']['rows']:
            if isinstance(row, dict):
                dates.update(row.keys())
        
        july_dates = sorted([d for d in dates if d.startswith('2025-07')])
        has_july_22 = '2025-07-22' in dates
        
        return {
            'july_dates': july_dates,
            'has_july_22': has_july_22,
            'total_dates': len([d for d in dates if d.count('-') == 2 and len(d) == 10])
        }
    
    except Exception as e:
        return {'error': str(e)}

def main():
    """主函数"""
    print("🔍 检查所有JSON文件中的7月数据...")
    print("=" * 60)
    
    json_files = glob.glob("*.json")
    
    files_with_july = []
    files_with_july_22 = []
    
    for filename in sorted(json_files):
        print(f"\n📄 检查文件: {filename}")
        result = check_file_for_july_data(filename)
        
        if result is None:
            print("  ❌ 文件格式不正确")
            continue
        
        if 'error' in result:
            print(f"  ❌ 读取错误: {result['error']}")
            continue
        
        if result['july_dates']:
            files_with_july.append(filename)
            print(f"  ✅ 包含7月数据: {len(result['july_dates'])} 天")
            print(f"     日期范围: {result['july_dates'][0]} ~ {result['july_dates'][-1]}")
            
            if result['has_july_22']:
                files_with_july_22.append(filename)
                print(f"  🎯 包含2025-07-22数据！")
        else:
            print(f"  ⚪ 无7月数据 (总共{result['total_dates']}天数据)")
    
    print("\n" + "=" * 60)
    print("📊 汇总结果:")
    print(f"🗂️  总文件数: {len(json_files)}")
    print(f"📅 包含7月数据的文件: {len(files_with_july)}")
    print(f"🎯 包含7月22日数据的文件: {len(files_with_july_22)}")
    
    if files_with_july_22:
        print("\n🎉 找到包含7月22日数据的文件:")
        for filename in files_with_july_22:
            print(f"   📁 {filename}")
    else:
        print("\n❌ 没有找到包含7月22日数据的文件")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
