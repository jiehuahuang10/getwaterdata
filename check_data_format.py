#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from force_real_data_web import force_get_real_data_for_web
import json

def check_data_format():
    """检查数据格式"""
    print("=== 检查数据格式 ===")
    
    # 获取昨天的数据
    result = force_get_real_data_for_web('2025-08-19')
    
    print(f"Success: {result.get('success')}")
    print(f"Data type: {type(result.get('data'))}")
    
    data = result.get('data', {})
    print(f"Data keys: {list(data.keys())}")
    
    print("\n=== 数据详细内容 ===")
    for key, value in data.items():
        print(f"\n{key}: {type(value)}")
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {type(sub_value)} = {sub_value}")
        elif isinstance(value, list) and len(value) > 0:
            print(f"  List length: {len(value)}")
            print(f"  First item: {value[0]}")
        else:
            print(f"  Value: {value}")

if __name__ == '__main__':
    check_data_format()
