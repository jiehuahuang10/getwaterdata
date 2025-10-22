#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs水务数据写入器
将水务数据写入到KDocs在线表格
"""

import requests
import json
from datetime import datetime, timedelta

class KDocsWaterWriter:
    def __init__(self):
        self.session = requests.Session()
        self.load_cookies()
        
        # 文档信息
        self.link_id = "cqagXO1NDs4P"
        self.file_id = "456521205074"
        
        # 水表配置
        self.meters = {
            '1#水表': '1号水表',
            '2#水表': '2号水表', 
            '3#水表': '3号水表',
            '4#水表': '4号水表',
            '5#水表': '5号水表',
            '6#水表': '6号水表',
            '7#水表': '7号水表',
            '8#水表': '8号水表'
        }
    
    def load_cookies(self):
        """
        加载Cookie
        """
        try:
            with open('kdocs_cookies.json', 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Referer': 'https://www.kdocs.cn/'
            })
            
            print("Cookie加载成功")
            return True
        
        except Exception as e:
            print(f"Cookie加载失败: {e}")
            return False
    
    def write_water_data(self, target_date, water_data):
        """
        写入水务数据到KDocs表格
        
        参数:
            target_date: 日期字符串，如 "2025-01-14"
            water_data: 水表数据字典，如 {'1#水表': 1000, '2#水表': 2000, ...}
        """
        print("=" * 60)
        print(f"写入水务数据到KDocs: {target_date}")
        print("=" * 60)
        
        # 准备数据行
        row_data = [target_date]
        
        for meter_name in ['1#水表', '2#水表', '3#水表', '4#水表', 
                           '5#水表', '6#水表', '7#水表', '8#水表']:
            value = water_data.get(meter_name)
            if value is not None:
                row_data.append(str(value))
                print(f"  {meter_name}: {value}")
            else:
                row_data.append("")
                print(f"  {meter_name}: (空)")
        
        print(f"\n准备写入的数据: {row_data}")
        
        # TODO: 实现实际的写入逻辑
        # 由于KDocs的表格API比较复杂，需要：
        # 1. 获取文档的编辑权限token
        # 2. 找到正确的sheet ID
        # 3. 调用写入API
        
        print("\n注意: KDocs的表格写入API需要进一步研究")
        print("当前Cookie已验证有效，可以访问文档")
        print("但表格的单元格写入需要特定的API调用")
        
        return {
            'success': False,
            'message': 'KDocs表格写入API待实现',
            'data': row_data
        }

def test_write():
    """
    测试写入功能
    """
    writer = KDocsWaterWriter()
    
    # 测试数据
    test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    test_data = {
        '1#水表': 1000,
        '2#水表': 2000,
        '3#水表': 1500,
        '4#水表': 1800,
        '5#水表': 2200,
        '6#水表': 1600,
        '7#水表': 1900,
        '8#水表': 2100
    }
    
    result = writer.write_water_data(test_date, test_data)
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 60)

if __name__ == "__main__":
    test_write()

