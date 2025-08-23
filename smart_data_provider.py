#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据提供器 - 当API不可用时使用现有真实数据
"""

import json
import os
import glob
from datetime import datetime, timedelta

def get_latest_data_file():
    """获取最新的数据文件"""
    data_files = (glob.glob("*COMPLETE_8_METERS*.json") + 
                 glob.glob("WEB_COMPLETE*.json"))
    
    if data_files:
        latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
        return latest_file
    return None

def load_real_data():
    """加载真实的历史数据"""
    latest_file = get_latest_data_file()
    if not latest_file:
        return None
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 加载数据文件: {latest_file}")
        print(f"📅 数据时间戳: {data.get('timestamp', 'Unknown')}")
        print(f"📊 包含水表数量: {data.get('meter_count', 0)}")
        
        return data
    except Exception as e:
        print(f"❌ 加载数据文件失败: {e}")
        return None

def get_available_dates(data):
    """获取数据中可用的日期列表"""
    if not data or 'data' not in data or 'rows' not in data['data']:
        return []
    
    dates = set()
    for row in data['data']['rows']:
        for key in row.keys():
            if key.startswith('2025-') and isinstance(row[key], (int, float)):
                dates.add(key)
    
    return sorted(list(dates))

def get_real_data_for_date(target_date):
    """获取指定日期的真实数据，如果没有则返回None"""
    print(f"🎯 智能数据提供器：获取 {target_date} 的数据")
    
    # 加载真实数据
    real_data = load_real_data()
    if not real_data:
        print("❌ 无法加载任何真实数据文件")
        return None
    
    # 检查可用日期
    available_dates = get_available_dates(real_data)
    print(f"📅 数据文件中可用的日期: {available_dates}")
    
    if target_date in available_dates:
        print(f"✅ 找到 {target_date} 的真实数据！")
        
        # 构建返回数据结构
        result_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'smart_data_provider',
            'success': True,
            'data_type': 'json',
            'calculation_date': datetime.now().strftime('%Y-%m-%d'),
            'date_range': {
                'start': target_date,
                'end': target_date,
                'description': f'智能提供器获取的真实数据: {target_date}'
            },
            'meter_count': real_data.get('meter_count', 8),
            'data': {
                'total': len(real_data['data']['rows']),
                'rows': []
            }
        }
        
        # 提取目标日期的数据
        for row in real_data['data']['rows']:
            if target_date in row and isinstance(row[target_date], (int, float)):
                # 创建新的行数据，只包含目标日期
                new_row = row.copy()
                # 保留基本信息和目标日期的数据
                result_data['data']['rows'].append(new_row)
        
        print(f"📊 成功提取 {len(result_data['data']['rows'])} 个水表的数据")
        return result_data
    
    else:
        print(f"⚠️ {target_date} 不在可用数据中")
        print(f"💡 可用的最近日期: {available_dates[-3:] if len(available_dates) >= 3 else available_dates}")
        
        # 返回空数据结构，表示该日期无真实数据
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'smart_data_provider',
            'success': True,
            'data_type': 'json',
            'calculation_date': datetime.now().strftime('%Y-%m-%d'),
            'date_range': {
                'start': target_date,
                'end': target_date,
                'description': f'该日期无真实数据: {target_date}'
            },
            'meter_count': 8,
            'data': {
                'total': 0,
                'rows': []
            },
            'no_real_data': True
        }

def show_available_data_summary():
    """显示可用数据的摘要"""
    real_data = load_real_data()
    if not real_data:
        print("❌ 无可用数据")
        return
    
    available_dates = get_available_dates(real_data)
    print("\n" + "="*60)
    print("📊 可用真实数据摘要")
    print("="*60)
    print(f"📂 数据文件: {get_latest_data_file()}")
    print(f"📅 数据时间范围: {available_dates[0]} ~ {available_dates[-1]}")
    print(f"📊 包含日期数量: {len(available_dates)}")
    print(f"🏭 水表数量: {real_data.get('meter_count', 0)}")
    
    print(f"\n📅 具体可用日期:")
    for date in available_dates:
        print(f"  ✅ {date}")
    
    # 显示第一个水表的示例数据
    if real_data['data']['rows']:
        first_meter = real_data['data']['rows'][0]
        print(f"\n📊 示例水表数据 ({first_meter.get('Name', 'Unknown')}):")
        for date in available_dates[:5]:  # 显示前5个日期的数据
            if date in first_meter:
                print(f"  {date}: {first_meter[date]:,.2f}")
    
    print("="*60)

if __name__ == "__main__":
    print("🚀 智能数据提供器测试")
    
    # 显示数据摘要
    show_available_data_summary()
    
    # 测试几个日期
    test_dates = [
        "2025-07-22",  # 用户想要的日期
        "2025-08-15",  # 应该有数据的日期
        "2025-08-10",  # 应该有数据的日期
        "2025-06-01"   # 应该没有数据的日期
    ]
    
    for test_date in test_dates:
        print(f"\n" + "-"*50)
        result = get_real_data_for_date(test_date)
        if result and result.get('data', {}).get('rows'):
            print(f"✅ {test_date}: 找到 {len(result['data']['rows'])} 个水表的数据")
        else:
            print(f"⚠️ {test_date}: 无真实数据")

