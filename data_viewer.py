#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据查看器
用于展示和分析已获取的水务数据
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_and_display_json_data(file_path):
    """加载并显示JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📁 文件: {file_path}")
        print(f"📊 总记录数: {data.get('total', 0)}")
        print(f"📋 数据行数: {len(data.get('rows', []))}")
        print("=" * 80)
        
        if 'rows' in data and data['rows']:
            for i, row in enumerate(data['rows']):
                print(f"\n🏭 水表 {i+1}: {row.get('Name', '未知')}")
                print(f"   ID: {row.get('ID', 'N/A')}")
                print(f"   直径: {row.get('MeterDiameter', 'N/A')}")
                print(f"   用途: {row.get('FMApplication', 'N/A')}")
                print(f"   地址: {row.get('useAddress', 'N/A')}")
                
                # 显示统计数据
                if row.get('maxvalue'):
                    print(f"   📈 最大值: {row['maxvalue']} ({row.get('maxtime', 'N/A')})")
                    print(f"   📉 最小值: {row['minvalue']} ({row.get('mintime', 'N/A')})")
                    print(f"   📊 平均值: {row['avg']:.3f}")
                
                # 显示每日数据
                daily_data = []
                for key, value in row.items():
                    if key.startswith('2024-') or key.startswith('2025-'):
                        if value is not None:
                            daily_data.append((key, value))
                
                if daily_data:
                    print(f"   📅 每日数据:")
                    daily_data.sort()
                    for date, value in daily_data:
                        print(f"      {date}: {value}")
                
                print("-" * 60)
        
        return data
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None

def create_summary_table(data):
    """创建数据汇总表"""
    if not data or 'rows' not in data:
        return None
    
    summary = []
    for row in data['rows']:
        summary_row = {
            'ID': row.get('ID', 'N/A'),
            'Name': row.get('Name', 'N/A'),
            'Diameter': row.get('MeterDiameter', 'N/A'),
            'Application': row.get('FMApplication', 'N/A'),
            'MaxValue': row.get('maxvalue', 'N/A'),
            'MinValue': row.get('minvalue', 'N/A'),
            'AvgValue': row.get('avg', 'N/A'),
            'HasDailyData': any(key.startswith('202') for key in row.keys())
        }
        summary.append(summary_row)
    
    return pd.DataFrame(summary)

def main():
    """主函数"""
    print("=" * 80)
    print("🔍 水务数据查看器")
    print("=" * 80)
    
    # 查找所有JSON文件
    json_files = list(Path('.').glob('*.json'))
    json_files = [f for f in json_files if 'water' in f.name or 'recent' in f.name]
    
    if not json_files:
        print("❌ 未找到数据文件")
        return
    
    print(f"📁 找到 {len(json_files)} 个数据文件:")
    for i, file in enumerate(json_files, 1):
        print(f"   {i}. {file.name}")
    
    # 处理每个文件
    all_data = []
    for file in json_files:
        print(f"\n{'='*80}")
        data = load_and_display_json_data(file)
        if data:
            all_data.append((file.name, data))
    
    # 创建汇总
    if all_data:
        print(f"\n{'='*80}")
        print("📊 数据汇总")
        print("=" * 80)
        
        for file_name, data in all_data:
            print(f"\n📄 {file_name}:")
            summary_df = create_summary_table(data)
            if summary_df is not None:
                print(summary_df.to_string(index=False))

if __name__ == "__main__":
    main()
