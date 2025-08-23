#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版强制获取真实数据 - 只保留成功的策略
"""

import requests
import json
import hashlib
import time
from bs4 import BeautifulSoup
from datetime import datetime
import random

def md5_hash(text):
    """计算MD5哈希值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def force_get_real_data_for_web(target_date):
    """为Web应用强制获取指定日期的真实数据 - 优化版"""
    
    print(f"🎯 获取 {target_date} 的真实数据（优化版）")
    
    # 直接使用成功的API调用
    print(f"🚀 API调用获取真实数据...")
    
    try:
        result = api_get_real_data(target_date)
        if result and result.get('success'):
            print(f"✅ API获取成功！")
            return result
        else:
            print(f"⚠️ API调用失败，尝试本地数据...")
            # 备用：从本地文件获取
            result = get_from_local_files(target_date)
            if result and result.get('success'):
                print(f"✅ 本地数据获取成功！")
                return result
    except Exception as e:
        print(f"❌ 获取异常: {e}")
    
    # 最后备用：创建标准数据结构
    print("🔧 创建标准数据结构...")
    return create_data_structure(target_date)

def api_get_real_data(target_date, max_retries=2):
    """API获取真实数据"""
    
    for attempt in range(max_retries):
        print(f"  🔄 API调用 {attempt + 1}/{max_retries}")
        
        session = requests.Session()
        
        # 登录
        if not login_to_system(session):
            continue
        
        # 获取数据
        result = fetch_api_data(session, target_date)
        if result and result.get('success'):
            return result
        
        # 短暂延迟后重试
        if attempt < max_retries - 1:
            time.sleep(random.uniform(1, 3))
    
    return None

def login_to_system(session):
    """登录到水务系统"""
    try:
        login_url = "http://axwater.dmas.cn/login.aspx"
        login_page = session.get(login_url, timeout=20)
        
        soup = BeautifulSoup(login_page.text, 'html.parser')
        form = soup.find('form')
        
        form_data = {}
        if form:
            for input_elem in form.find_all('input'):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
        
        # 设置登录信息
        form_data['user'] = "13509288500"
        form_data['pwd'] = md5_hash("288500")
        
        login_response = session.post(login_url, data=form_data, timeout=20)
        
        if 'window.location' in login_response.text:
            # 访问主页面
            main_url = "http://axwater.dmas.cn/frmMain.aspx"
            session.get(main_url, timeout=20)
            return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ 登录异常: {e}")
        return False

def fetch_api_data(session, target_date):
    """从API获取数据"""
    try:
        # 访问报表页面
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        report_response = session.get(report_url, timeout=20)
        
        if report_response.status_code != 200:
            return None
        
        # 水表ID列表
        meter_ids = [
            '1261181000263', '1261181000300', '1262330402331', '2190066',
            '2190493', '2501200108', '2520005', '2520006'
        ]
        
        formatted_node_ids = "'" + "','".join(meter_ids) + "'"
        
        # API调用
        api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
        api_params = {
            'nodeId': formatted_node_ids,
            'startDate': target_date,
            'endDate': target_date,
            'meterType': '-1',
            'statisticsType': 'flux',
            'type': 'dayRpt'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': report_url
        }
        
        api_response = session.post(api_url, data=api_params, headers=headers, timeout=20)
        
        if api_response.status_code == 200 and len(api_response.text.strip()) > 0:
            try:
                json_data = json.loads(api_response.text)
                if 'rows' in json_data and len(json_data['rows']) > 0:
                    # 检查是否有真实数据
                    has_real_data = False
                    for row in json_data['rows']:
                        if target_date in row and isinstance(row[target_date], (int, float)):
                            has_real_data = True
                            break
                    
                    if has_real_data:
                        return {
                            'success': True,
                            'data': json_data,
                            'source': 'optimized_api_call',
                            'target_date': target_date
                        }
            except json.JSONDecodeError:
                pass
        
        return None
        
    except Exception as e:
        print(f"  ❌ API调用异常: {e}")
        return None

def get_from_local_files(target_date):
    """从本地数据文件获取"""
    
    try:
        import glob
        import os
        
        # 查找数据文件
        data_files = (glob.glob("*COMPLETE_8_METERS*.json") + 
                     glob.glob("WEB_COMPLETE*.json") +
                     glob.glob("REAL_*.json"))
        
        for filename in sorted(data_files, key=lambda x: os.path.getmtime(x), reverse=True):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'data' in data and 'rows' in data['data']:
                    for row in data['data']['rows']:
                        if isinstance(row, dict) and target_date in row:
                            value = row[target_date]
                            if isinstance(value, (int, float)) and value > 0:
                                print(f"  ✅ 在 {filename} 中找到真实数据")
                                return {
                                    'success': True,
                                    'data': data['data'],
                                    'source': f'local_file_{filename}',
                                    'target_date': target_date
                                }
            except Exception:
                continue
        
        return None
        
    except Exception as e:
        print(f"  ❌ 本地文件检查异常: {e}")
        return None

def create_data_structure(target_date):
    """创建标准数据结构"""
    
    # 8个水表信息
    meter_info = [
        {'id': '1261181000263', 'name': '荔新大道DN1200流量计'},
        {'id': '1261181000300', 'name': '新城大道医院DN800流量计'},
        {'id': '1262330402331', 'name': '宁西总表DN1200'},
        {'id': '2190066', 'name': '三江新总表DN800（2190066）'},
        {'id': '2190493', 'name': '沙庄总表'},
        {'id': '2501200108', 'name': '2501200108'},
        {'id': '2520005', 'name': '如丰大道600监控表'},
        {'id': '2520006', 'name': '三棵树600监控表'},
    ]
    
    # 创建数据行
    rows = []
    for meter in meter_info:
        rows.append({
            'ID': meter['id'],
            'Name': meter['name'],
            target_date: None  # 明确标记为无真实数据
        })
    
    return {
        'success': True,
        'data': {
            'total': len(rows),
            'rows': rows
        },
        'source': 'optimized_data_structure',
        'target_date': target_date,
        'note': f'{target_date} 无真实数据，所有水表值为空'
    }

# 测试函数
def test_optimized():
    """测试优化版本"""
    test_dates = ["2025-08-19", "2025-07-22", "2025-07-23"]
    
    for test_date in test_dates:
        print(f"\n🚀 测试日期: {test_date}")
        print("=" * 50)
        
        result = force_get_real_data_for_web(test_date)
        
        if result and result.get('success'):
            print(f"✅ 成功获取数据")
            print(f"📊 数据来源: {result.get('source', 'unknown')}")
            
            if 'data' in result and 'rows' in result['data']:
                print(f"📈 包含 {len(result['data']['rows'])} 个水表")
                
                # 显示第一个水表的数据
                if result['data']['rows']:
                    first_row = result['data']['rows'][0]
                    value = first_row.get(test_date, '无数据')
                    name = first_row.get('Name', '未知水表')
                    print(f"💧 示例: {name} = {value}")
        else:
            print(f"❌ 获取失败")
        
        print("=" * 50)

if __name__ == "__main__":
    test_optimized()

