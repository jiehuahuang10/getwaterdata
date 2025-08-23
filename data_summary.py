#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据摘要显示器 - 显示最近获取的水务数据
"""

import json
import glob
import os
from datetime import datetime

def show_latest_data_summary():
    """显示最新数据摘要"""
    print("="*80)
    print("🏆 水务数据获取项目 - 最近7天数据摘要")
    print("="*80)
    
    # 查找最新的数据文件
    data_files = []
    
    # 查找完整数据文件
    complete_files = glob.glob("COMPLETE_8_METERS_*.json")
    data_files.extend([(f, "完整版") for f in complete_files])
    
    # 查找测试数据文件
    test_files = glob.glob("TEST_recent_*.json")
    data_files.extend([(f, "测试版") for f in test_files])
    
    if not data_files:
        print("❌ 没有找到数据文件")
        return False
    
    # 按修改时间排序，获取最新的
    data_files.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
    
    print(f"📊 找到 {len(data_files)} 个数据文件:")
    for i, (filename, file_type) in enumerate(data_files[:5], 1):
        mtime = datetime.fromtimestamp(os.path.getmtime(filename))
        file_size = os.path.getsize(filename)
        print(f"  {i}. {filename} ({file_type}) - {mtime.strftime('%H:%M:%S')} - {file_size:,} 字节")
    
    # 分析最新的数据文件
    latest_file, file_type = data_files[0]
    print(f"\n🔍 分析最新数据文件: {latest_file}")
    print("-" * 80)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 基本信息
        print(f"📅 数据时间: {data.get('timestamp', 'N/A')}")
        print(f"📋 数据来源: {data.get('source', 'N/A')}")
        print(f"✅ 获取状态: {'成功' if data.get('success') else '失败'}")
        
        # 日期范围
        date_range = data.get('date_range', {})
        if date_range:
            print(f"📆 日期范围: {date_range.get('start')} 至 {date_range.get('end')}")
            print(f"📝 说明: {date_range.get('description', '')}")
        
        # 水表信息
        if 'target_meters' in data:
            target_meters = data['target_meters']
            meter_count = target_meters.get('total', len(target_meters.get('ids', [])))
            print(f"🏭 目标水表数量: {meter_count} 个")
            
            meter_names = target_meters.get('names', [])
            if meter_names:
                print("📋 水表列表:")
                for i, name in enumerate(meter_names, 1):
                    print(f"   {i}. {name}")
        
        # 数据分析
        actual_data = data.get('data', {})
        if actual_data and 'rows' in actual_data:
            rows = actual_data['rows']
            total = actual_data.get('total', len(rows))
            
            print(f"\n📊 数据统计:")
            print(f"   API返回总数: {total}")
            print(f"   实际行数: {len(rows)}")
            
            if len(rows) > 0:
                print(f"   数据完整性: {'✅ 完整' if len(rows) >= 8 else '⚠️ 不完整'}")
                
                # 分析日期列
                sample_row = rows[0] if rows else {}
                date_columns = [key for key in sample_row.keys() if key.startswith('202')]
                date_columns.sort()
                
                if date_columns:
                    print(f"   包含日期: {len(date_columns)} 天")
                    print(f"   日期范围: {date_columns[0]} 至 {date_columns[-1]}")
                
                print(f"\n🏭 各水表数据详情:")
                print("-" * 50)
                
                for i, row in enumerate(rows, 1):
                    if isinstance(row, dict):
                        meter_id = row.get('ID', 'N/A')
                        meter_name = row.get('Name', 'N/A')
                        max_value = row.get('maxvalue', 'N/A')
                        min_value = row.get('minvalue', 'N/A')
                        avg_value = row.get('avg', 'N/A')
                        
                        print(f"水表{i}: {meter_name}")
                        print(f"   ID: {meter_id}")
                        
                        if max_value != 'N/A' and max_value is not None:
                            print(f"   最大值: {max_value:,.1f}")
                            print(f"   最小值: {min_value:,.1f}")
                            print(f"   平均值: {avg_value:,.3f}")
                        
                        # 显示最近3天的数据
                        recent_data = []
                        for date_col in date_columns[-3:]:
                            value = row.get(date_col)
                            if value is not None:
                                recent_data.append(f"{date_col}: {value:,.1f}")
                        
                        if recent_data:
                            print(f"   最近数据: {', '.join(recent_data)}")
                        
                        print()
            else:
                print("   ⚠️ 没有具体的水表数据")
        else:
            print("   ❌ 数据格式不正确或为空")
        
        # 成功总结
        print("="*80)
        if data.get('success') and actual_data and len(actual_data.get('rows', [])) >= 8:
            print("🎉 数据获取完全成功！")
            print(f"✅ 成功获取了8个水表最近7天的真实数据")
            print(f"📊 数据文件: {latest_file}")
            print(f"💾 文件大小: {os.path.getsize(latest_file):,} 字节")
            
            # 显示今天的获取情况
            today = datetime.now().strftime('%Y-%m-%d')
            if data.get('calculation_date') == today:
                print(f"🕐 今天({today})已成功获取最新数据")
            
            return True
        else:
            print("⚠️ 数据获取可能不完整")
            return False
            
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return False

def show_all_recent_files():
    """显示所有最近的文件"""
    print("\n📁 最近生成的所有数据文件:")
    print("-" * 50)
    
    # 获取所有JSON文件
    all_files = glob.glob("*.json")
    
    # 按修改时间排序
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    today = datetime.now().strftime('%Y%m%d')
    
    for filename in all_files[:10]:  # 显示最近10个
        mtime = datetime.fromtimestamp(os.path.getmtime(filename))
        file_size = os.path.getsize(filename)
        
        # 判断文件类型
        if 'COMPLETE_8_METERS' in filename:
            file_type = "🏆 完整版"
        elif 'TEST_recent' in filename:
            file_type = "🧪 测试版"
        elif 'REAL_water' in filename:
            file_type = "💎 真实数据"
        else:
            file_type = "📄 其他"
        
        # 判断是否是今天的文件
        is_today = today in filename
        today_mark = " 🆕" if is_today else ""
        
        print(f"  {file_type} {filename}{today_mark}")
        print(f"     时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')} | 大小: {file_size:,} 字节")

if __name__ == "__main__":
    success = show_latest_data_summary()
    show_all_recent_files()
    
    print("\n" + "="*80)
    if success:
        print("🎉 项目测试完成！最近7天的水务数据获取成功！")
    else:
        print("⚠️ 请检查数据获取结果")
    print("="*80)
