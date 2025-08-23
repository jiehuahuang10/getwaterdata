#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制获取真实数据 - 必须成功获取指定日期的真实水表数据
"""

import requests
import json
import hashlib
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random

def md5_hash(text):
    """计算MD5哈希值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def force_get_real_data(target_date):
    """强制获取指定日期的真实数据 - 多种方法尝试直到成功"""
    
    print(f"🎯 强制获取 {target_date} 的真实数据")
    print("💪 使用多种策略确保成功获取")
    
    strategies = [
        "single_day_query",
        "range_query_small", 
        "range_query_medium",
        "range_query_large",
        "different_api_params",
        "retry_with_delay",
        "browser_simulation",
        "direct_page_scraping"
    ]
    
    for strategy_name in strategies:
        print(f"\n🔄 尝试策略: {strategy_name}")
        result = try_strategy(target_date, strategy_name)
        
        if result and result.get('data') and result['data'].get('rows'):
            print(f"✅ 策略 {strategy_name} 成功！获取到 {len(result['data']['rows'])} 个水表数据")
            return result
        else:
            print(f"❌ 策略 {strategy_name} 失败")
    
    print("🚨 所有策略都失败了，但我们必须获取真实数据！")
    print("🔧 使用最后的备用方案...")
    
    # 最后的备用方案：使用已知有效的数据文件，但明确告知用户
    return get_closest_real_data(target_date)

def try_strategy(target_date, strategy):
    """尝试不同的策略获取数据"""
    
    session = requests.Session()
    
    # 登录
    if not login_to_system(session):
        return None
    
    if strategy == "single_day_query":
        return single_day_api_call(session, target_date)
    
    elif strategy == "range_query_small":
        # 小范围查询：目标日期前后1天
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        start_date = (target_dt - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (target_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        return range_api_call(session, start_date, end_date, target_date)
    
    elif strategy == "range_query_medium":
        # 中等范围查询：目标日期前后3天
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        start_date = (target_dt - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = (target_dt + timedelta(days=3)).strftime('%Y-%m-%d')
        return range_api_call(session, start_date, end_date, target_date)
    
    elif strategy == "range_query_large":
        # 大范围查询：目标日期前后7天
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        start_date = (target_dt - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = (target_dt + timedelta(days=7)).strftime('%Y-%m-%d')
        return range_api_call(session, start_date, end_date, target_date)
    
    elif strategy == "different_api_params":
        # 尝试不同的API参数组合
        return try_different_params(session, target_date)
    
    elif strategy == "retry_with_delay":
        # 重试策略：多次尝试，每次间隔随机延迟
        return retry_with_random_delay(session, target_date)
    
    elif strategy == "browser_simulation":
        # 模拟浏览器行为
        return browser_like_request(session, target_date)
    
    elif strategy == "direct_page_scraping":
        # 直接抓取网页数据
        return direct_page_scraping(session, target_date)
    
    return None

def login_to_system(session):
    """登录到水务系统"""
    try:
        login_url = "http://axwater.dmas.cn/login.aspx"
        login_page = session.get(login_url)
        
        soup = BeautifulSoup(login_page.text, 'html.parser')
        form = soup.find('form')
        
        form_data = {}
        if form:
            for input_elem in form.find_all('input'):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
        
        username = "13509288500"
        password = "288500"
        form_data['user'] = username
        form_data['pwd'] = md5_hash(password)
        
        login_response = session.post(login_url, data=form_data)
        
        if 'window.location' in login_response.text:
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

def single_day_api_call(session, target_date):
    """单日API调用"""
    try:
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        report_response = session.get(report_url)
        
        if report_response.status_code != 200:
            return None
        
        # 水表ID
        meter_ids = [
            '1261181000263', '1261181000300', '1262330402331', '2190066',
            '2190493', '2501200108', '2520005', '2520006'
        ]
        
        formatted_node_ids = "'" + "','".join(meter_ids) + "'"
        
        # 获取ASP.NET状态
        report_soup = BeautifulSoup(report_response.text, 'html.parser')
        viewstate = report_soup.find('input', {'name': '__VIEWSTATE'})
        eventvalidation = report_soup.find('input', {'name': '__EVENTVALIDATION'})
        
        api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
        api_params = {
            'nodeId': formatted_node_ids,
            'startDate': target_date,
            'endDate': target_date,
            'rptType': 'day'
        }
        
        if viewstate:
            api_params['__VIEWSTATE'] = viewstate.get('value', '')
        if eventvalidation:
            api_params['__EVENTVALIDATION'] = eventvalidation.get('value', '')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': report_url
        }
        
        api_response = session.post(api_url, data=api_params, headers=headers)
        
        print(f"📡 API响应: {api_response.status_code}, 长度: {len(api_response.text)}")
        
        if api_response.status_code == 200 and len(api_response.text.strip()) > 0:
            try:
                json_data = json.loads(api_response.text)
                if 'rows' in json_data and len(json_data['rows']) > 0:
                    # 检查是否包含目标日期的数据
                    for row in json_data['rows']:
                        if target_date in row and isinstance(row[target_date], (int, float)):
                            return {
                                'success': True,
                                'data': json_data,
                                'source': 'force_real_data_single_day'
                            }
                return None
            except json.JSONDecodeError:
                return None
        
        return None
        
    except Exception as e:
        print(f"❌ 单日查询异常: {e}")
        return None

def range_api_call(session, start_date, end_date, target_date):
    """范围API调用"""
    try:
        print(f"📅 范围查询: {start_date} ~ {end_date}")
        
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        report_response = session.get(report_url)
        
        meter_ids = [
            '1261181000263', '1261181000300', '1262330402331', '2190066',
            '2190493', '2501200108', '2520005', '2520006'
        ]
        
        formatted_node_ids = "'" + "','".join(meter_ids) + "'"
        
        report_soup = BeautifulSoup(report_response.text, 'html.parser')
        viewstate = report_soup.find('input', {'name': '__VIEWSTATE'})
        eventvalidation = report_soup.find('input', {'name': '__EVENTVALIDATION'})
        
        api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
        api_params = {
            'nodeId': formatted_node_ids,
            'startDate': start_date,
            'endDate': end_date,
            'rptType': 'day'
        }
        
        if viewstate:
            api_params['__VIEWSTATE'] = viewstate.get('value', '')
        if eventvalidation:
            api_params['__EVENTVALIDATION'] = eventvalidation.get('value', '')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': report_url
        }
        
        api_response = session.post(api_url, data=api_params, headers=headers)
        
        if api_response.status_code == 200 and len(api_response.text.strip()) > 0:
            try:
                json_data = json.loads(api_response.text)
                if 'rows' in json_data and len(json_data['rows']) > 0:
                    # 检查是否包含目标日期
                    for row in json_data['rows']:
                        if target_date in row and isinstance(row[target_date], (int, float)):
                            print(f"✅ 在范围数据中找到 {target_date} 的真实数据！")
                            return {
                                'success': True,
                                'data': json_data,
                                'source': f'force_real_data_range_{start_date}_{end_date}'
                            }
                return None
            except json.JSONDecodeError:
                return None
        
        return None
        
    except Exception as e:
        print(f"❌ 范围查询异常: {e}")
        return None

def try_different_params(session, target_date):
    """尝试不同的参数组合"""
    print("🔧 尝试不同的API参数组合...")
    
    # 不同的rptType
    rpt_types = ['day', 'hour', 'month']
    
    for rpt_type in rpt_types:
        print(f"  🔄 尝试 rptType: {rpt_type}")
        result = single_day_with_rpt_type(session, target_date, rpt_type)
        if result:
            return result
    
    return None

def single_day_with_rpt_type(session, target_date, rpt_type):
    """使用指定的rptType进行单日查询"""
    try:
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        report_response = session.get(report_url)
        
        meter_ids = [
            '1261181000263', '1261181000300', '1262330402331', '2190066',
            '2190493', '2501200108', '2520005', '2520006'
        ]
        
        formatted_node_ids = "'" + "','".join(meter_ids) + "'"
        
        api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
        api_params = {
            'nodeId': formatted_node_ids,
            'startDate': target_date,
            'endDate': target_date,
            'rptType': rpt_type
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        
        api_response = session.post(api_url, data=api_params, headers=headers)
        
        if api_response.status_code == 200 and len(api_response.text.strip()) > 0:
            try:
                json_data = json.loads(api_response.text)
                if 'rows' in json_data and len(json_data['rows']) > 0:
                    return {
                        'success': True,
                        'data': json_data,
                        'source': f'force_real_data_rptType_{rpt_type}'
                    }
            except json.JSONDecodeError:
                pass
        
        return None
        
    except Exception:
        return None

def retry_with_random_delay(session, target_date):
    """重试策略：多次尝试，随机延迟"""
    print("⏱️ 使用重试策略...")
    
    for attempt in range(5):  # 尝试5次
        delay = random.uniform(1, 3)  # 随机延迟1-3秒
        print(f"  🔄 第 {attempt + 1} 次尝试，延迟 {delay:.1f} 秒...")
        time.sleep(delay)
        
        result = single_day_api_call(session, target_date)
        if result:
            return result
    
    return None

def browser_like_request(session, target_date):
    """模拟浏览器行为"""
    print("🌐 模拟浏览器行为...")
    
    try:
        # 先访问主页面
        main_url = "http://axwater.dmas.cn/frmMain.aspx"
        session.get(main_url)
        time.sleep(1)
        
        # 再访问报表页面
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        session.get(report_url)
        time.sleep(1)
        
        # 然后进行API调用
        return single_day_api_call(session, target_date)
        
    except Exception:
        return None

def direct_page_scraping(session, target_date):
    """直接抓取网页表格数据"""
    print("🕷️ 直接抓取网页表格数据...")
    
    try:
        # 构建报表页面URL，带查询参数
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        
        # 先访问报表页面
        report_response = session.get(report_url)
        if report_response.status_code != 200:
            return None
        
        # 解析页面，寻找表单
        soup = BeautifulSoup(report_response.text, 'html.parser')
        
        # 查找表单元素
        form = soup.find('form')
        if not form:
            return None
        
        # 获取所有input字段
        form_data = {}
        for input_elem in form.find_all('input'):
            name = input_elem.get('name')
            value = input_elem.get('value', '')
            if name:
                form_data[name] = value
        
        # 设置查询参数
        # 这里需要根据实际的表单字段来设置
        # 可能的字段名：startDate, endDate, nodeIds等
        
        # 尝试不同的表单字段组合
        possible_date_fields = ['startDate', 'start_date', 'dateFrom', 'beginDate']
        possible_end_fields = ['endDate', 'end_date', 'dateTo', 'endDate']
        
        for start_field in possible_date_fields:
            if start_field in form_data:
                form_data[start_field] = target_date
                break
        
        for end_field in possible_end_fields:
            if end_field in form_data:
                form_data[end_field] = target_date
                break
        
        # 提交表单
        form_response = session.post(report_url, data=form_data)
        
        if form_response.status_code == 200:
            # 解析返回的页面，查找数据表格
            result_soup = BeautifulSoup(form_response.text, 'html.parser')
            
            # 查找数据表格
            tables = result_soup.find_all('table')
            
            for table in tables:
                # 查找包含水表数据的表格
                rows = table.find_all('tr')
                if len(rows) > 1:  # 至少有表头和数据行
                    # 尝试解析表格数据
                    table_data = parse_table_data(table, target_date)
                    if table_data:
                        return {
                            'success': True,
                            'data': table_data,
                            'source': 'direct_page_scraping'
                        }
        
        return None
        
    except Exception as e:
        print(f"❌ 网页抓取异常: {e}")
        return None

def parse_table_data(table, target_date):
    """解析表格数据"""
    try:
        rows = table.find_all('tr')
        if len(rows) < 2:
            return None
        
        # 解析表头
        header_row = rows[0]
        headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
        
        # 查找日期列
        date_col_index = -1
        for i, header in enumerate(headers):
            if target_date in header or '日期' in header:
                date_col_index = i
                break
        
        if date_col_index == -1:
            return None
        
        # 解析数据行
        data_rows = []
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) > date_col_index:
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.get_text().strip()
                
                # 检查是否包含目标日期的数据
                if target_date in str(row_data):
                    data_rows.append(row_data)
        
        if data_rows:
            return {
                'total': len(data_rows),
                'rows': data_rows
            }
        
        return None
        
    except Exception:
        return None

def get_closest_real_data(target_date):
    """获取最接近的真实数据作为备用方案"""
    print("🔄 使用备用方案：获取最接近的真实数据...")
    
    try:
        import glob
        import os
        data_files = (glob.glob("*COMPLETE_8_METERS*.json") + 
                     glob.glob("WEB_COMPLETE*.json"))
        
        if not data_files:
            return None
        
        latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 使用数据文件: {latest_file}")
        
        # 检查是否有目标日期的数据
        if 'data' in data and 'rows' in data['data']:
            for row in data['data']['rows']:
                if target_date in row and isinstance(row[target_date], (int, float)):
                    print(f"🎉 在备用数据中找到 {target_date} 的真实数据！")
                    return {
                        'success': True,
                        'data': data['data'],
                        'source': f'backup_real_data_from_{latest_file}'
                    }
        
        print(f"⚠️ 备用数据中没有 {target_date} 的数据")
        return None
        
    except Exception as e:
        print(f"❌ 备用方案失败: {e}")
        return None

if __name__ == "__main__":
    # 先测试一个最近的日期（更可能有数据）
    test_date = "2025-08-15"  # 改为8月15日测试
    print(f"🚀 强制获取真实数据测试: {test_date}")
    print("=" * 60)
    
    result = force_get_real_data(test_date)
    
    if result and result.get('success'):
        print(f"\n🎉 成功获取 {test_date} 的真实数据！")
        print(f"📊 数据来源: {result.get('source', 'unknown')}")
        
        if 'data' in result and 'rows' in result['data']:
            print(f"📈 包含 {len(result['data']['rows'])} 个水表的数据")
            
            # 显示第一个水表的示例数据
            first_row = result['data']['rows'][0]
            if test_date in first_row:
                print(f"💧 示例数据 ({first_row.get('Name', 'Unknown')}): {first_row[test_date]}")
    else:
        print(f"\n❌ 无法获取 {test_date} 的真实数据")
    
    print("=" * 60)
