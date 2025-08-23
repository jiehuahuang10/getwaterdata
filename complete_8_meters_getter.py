#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整8个水表动态获取最近7天数据
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import json
import time
from datetime import datetime, timedelta

def md5_hash(text):
    """计算MD5哈希"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def calculate_recent_7days():
    """计算最近7天的日期范围（昨天往前推7天）"""
    today = datetime.now()
    
    # 昨天作为结束日期
    end_date = today - timedelta(days=1)
    
    # 昨天往前推7天作为开始日期
    start_date = end_date - timedelta(days=7)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    return start_str, end_str

def login_to_system(session):
    """登录到水务系统"""
    try:
        login_url = "http://axwater.dmas.cn/Login.aspx"
        login_page = session.get(login_url)
        
        soup = BeautifulSoup(login_page.text, 'html.parser')
        form = soup.find('form')
        
        # 提取表单数据
        form_data = {}
        for input_elem in form.find_all('input'):
            name = input_elem.get('name')
            value = input_elem.get('value', '')
            if name:
                form_data[name] = value
        
        # 设置登录凭据
        username = '13509288500'
        password = '288500'
        form_data['user'] = username
        form_data['pwd'] = md5_hash(password)
        
        # 执行登录
        login_response = session.post(login_url, data=form_data)
        print(f"登录响应状态: {login_response.status_code}")
        
        # 检查JavaScript重定向
        if "window.location='frmMain.aspx'" in login_response.text:
            print("✅ 检测到JavaScript重定向，登录成功！")
            
            # 跳转到主页面
            main_url = "http://axwater.dmas.cn/frmMain.aspx"
            main_response = session.get(main_url)
            print(f"主页面状态: {main_response.status_code}")
            
            if main_response.status_code == 200:
                print("✅ 成功访问主页面")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ 登录失败: {str(e)}")
        return False

def fetch_water_data(session, meter_ids, start_date, end_date):
    """获取水表数据"""
    try:
        # 访问报表页面
        print("📊 访问报表页面...")
        time.sleep(1)
        
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        report_response = session.get(report_url)
        print(f"报表页面状态: {report_response.status_code}")
        
        if '登录超时' in report_response.text:
            print("❌ 登录超时，需要重新登录")
            return None
            
        print("✅ 成功访问报表页面！")
        
        # 格式化nodeId参数（所有水表ID）
        formatted_node_ids = "'" + "','".join(meter_ids) + "'"
        print(f"🔧 nodeId参数: {formatted_node_ids}")
        
        # API调用
        api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
        api_params = {
            'nodeId': formatted_node_ids,
            'startDate': start_date,
            'endDate': end_date,
            'rptType': 'day'
        }
        
        print(f"🔗 API调用参数: {api_params}")
        
        # 获取报表页面的状态数据
        report_soup = BeautifulSoup(report_response.text, 'html.parser')
        viewstate = report_soup.find('input', {'name': '__VIEWSTATE'})
        eventvalidation = report_soup.find('input', {'name': '__EVENTVALIDATION'})
        
        api_data = api_params.copy()
        if viewstate:
            api_data['__VIEWSTATE'] = viewstate.get('value', '')
        if eventvalidation:
            api_data['__EVENTVALIDATION'] = eventvalidation.get('value', '')
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': report_url
        }
        
        print(f"🔗 发送API请求到: {api_url}")
        api_response = session.post(api_url, data=api_data, headers=headers)
        print(f"API响应状态码: {api_response.status_code}")
        print(f"响应数据长度: {len(api_response.text)} 字符")
        
        # 调试信息：显示响应头和部分内容
        print(f"🔍 响应头Content-Type: {api_response.headers.get('content-type', 'N/A')}")
        if len(api_response.text.strip()) > 0:
            preview = api_response.text[:200] if len(api_response.text) > 200 else api_response.text
            print(f"🔍 响应内容预览: {preview}")
        else:
            print("🔍 响应内容为空")
        
        if api_response.status_code == 200 and len(api_response.text.strip()) > 0:
            try:
                json_data = json.loads(api_response.text)
                print(f"✅ 成功解析JSON数据")
                return {'data': json_data}
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return None
        else:
            print("❌ API响应为空或无效")
            return None
            
    except Exception as e:
        print(f"❌ 获取水表数据失败: {str(e)}")
        return None

def get_water_data_for_date_range(start_date, end_date):
    """获取指定日期范围的水表数据"""
    session = requests.Session()
    
    # 如果传入的是datetime对象，转换为字符串
    if isinstance(start_date, datetime):
        start_str = start_date.strftime('%Y-%m-%d')
    else:
        start_str = start_date
        
    if isinstance(end_date, datetime):
        end_str = end_date.strftime('%Y-%m-%d')
    else:
        end_str = end_date
    
    print(f"🎯 获取日期范围: {start_str} ~ {end_str}")
    
    # 完整的8个水表ID列表
    meter_ids = [
        '1261181000263',  # 荔新大道DN1200流量计
        '1261181000300',  # 新城大道医院DN800流量计
        '1262330402331',  # 宁西总表DN1200
        '2190066',        # 三江新总表DN800
        '2190493',        # 沙庄总表
        '2501200108',     # 2501200108
        '2520005',        # 如丰大道600监控表
        '2520006'         # 三棵树600监控表
    ]
    
    try:
        # 1. 登录
        print("🔐 正在登录...")
        login_success = login_to_system(session)
        if not login_success:
            return {'success': False, 'message': '登录失败'}
        
        # 2. 获取数据
        print("📊 正在获取水表数据...")
        water_data = fetch_water_data(session, meter_ids, start_str, end_str)
        
        if water_data and 'data' in water_data and water_data['data']['total'] > 0:
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'dynamic_date_getter',
                'success': True,
                'data_type': 'json',
                'calculation_date': datetime.now().strftime('%Y-%m-%d'),
                'date_range': {
                    'start': start_str,
                    'end': end_str,
                    'description': f'指定日期范围: {start_str} ~ {end_str}'
                },
                'meter_count': len(meter_ids),
                'data': water_data['data']
            }
            
            print(f"✅ 成功获取数据，包含 {water_data['data']['total']} 个水表")
            return result
        else:
            print("❌ 未获取到有效数据")
            return {'success': False, 'message': '未获取到有效数据'}
            
    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}")
        return {'success': False, 'message': str(e)}

def get_complete_8_meters_data():
    """获取完整8个水表的最近7天数据"""
    session = requests.Session()
    
    print("🏭 完整8个水表数据获取器启动...")
    
    # 完整的8个水表ID列表（按图片顺序）
    meter_ids = [
        '1261181000263',  # 荔新大道DN1200流量计
        '1261181000300',  # 新城大道医院DN800流量计
        '1262330402331',  # 宁西总表DN1200
        '2190066',        # 三江新总表DN800
        '2190493',        # 沙庄总表
        '2501200108',     # 2501200108
        '2520005',        # 如丰大道600监控表
        '2520006'         # 三棵树600监控表
    ]
    
    meter_names = [
        '荔新大道DN1200流量计',
        '新城大道医院DN800流量计', 
        '宁西总表DN1200',
        '三江新总表DN800',
        '沙庄总表',
        '2501200108',
        '如丰大道600监控表',
        '三棵树600监控表'
    ]
    
    print(f"📋 目标水表列表 (共{len(meter_ids)}个):")
    for i, (meter_id, name) in enumerate(zip(meter_ids, meter_names), 1):
        print(f"  {i}. {name} ({meter_id})")
    
    # 计算日期范围
    start_date, end_date = calculate_recent_7days()
    print(f"📅 今天: {datetime.now().strftime('%Y年%m月%d日')}")
    print(f"📅 数据范围: {start_date} 至 {end_date} (昨天往前推7天)")
    
    # 步骤1: 登录
    print("\n步骤1: 执行登录")
    login_url = "http://axwater.dmas.cn/Login.aspx"
    login_page = session.get(login_url)
    
    soup = BeautifulSoup(login_page.text, 'html.parser')
    form = soup.find('form')
    
    # 提取表单数据
    form_data = {}
    for input_elem in form.find_all('input'):
        name = input_elem.get('name')
        value = input_elem.get('value', '')
        if name:
            form_data[name] = value
    
    # 设置登录凭据
    username = '13509288500'
    password = '288500'
    form_data['user'] = username
    form_data['pwd'] = md5_hash(password)
    
    # 执行登录
    login_response = session.post(login_url, data=form_data)
    print(f"登录响应状态: {login_response.status_code}")
    
    # 检查JavaScript重定向
    if "window.location='frmMain.aspx'" in login_response.text:
        print("✅ 检测到JavaScript重定向，登录成功！")
        
        # 步骤2: 手动跳转到主页面
        print("步骤2: 跳转到主页面")
        main_url = "http://axwater.dmas.cn/frmMain.aspx"
        main_response = session.get(main_url)
        print(f"主页面状态: {main_response.status_code}")
        
        if main_response.status_code == 200:
            print("✅ 成功访问主页面")
            
            # 步骤3: 访问报表页面
            print("步骤3: 访问报表页面")
            time.sleep(1)  # 稍等一下
            
            report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
            report_response = session.get(report_url)
            print(f"报表页面状态: {report_response.status_code}")
            
            if '登录超时' not in report_response.text:
                print("✅ 成功访问报表页面！")
                
                # 步骤4: 获取完整8个水表的数据
                print(f"步骤4: 获取完整8个水表 {start_date} 至 {end_date} 的数据")
                
                # 格式化nodeId参数（所有8个水表ID）
                formatted_node_ids = "'" + "','".join(meter_ids) + "'"
                print(f"🔧 完整nodeId参数: {formatted_node_ids}")
                
                # API调用 - 使用完整的8个水表ID
                api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
                api_params = {
                    'nodeId': formatted_node_ids,  # 完整的8个水表
                    'startDate': start_date,
                    'endDate': end_date,
                    'meterType': '-1',
                    'statisticsType': 'flux',
                    'type': 'dayRpt'
                }
                
                api_headers = {
                    'Referer': report_url,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                print(f"🔄 API请求参数:")
                for key, value in api_params.items():
                    if key == 'nodeId':
                        print(f"  {key}: {value}")
                    elif key in ['startDate', 'endDate']:
                        print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
                
                api_response = session.post(api_url, data=api_params, headers=api_headers)
                print(f"API响应状态: {api_response.status_code}")
                print(f"API响应长度: {len(api_response.text)}")
                
                if api_response.text and len(api_response.text) > 10:
                    print("🎉 API返回数据！")
                    
                    try:
                        data = api_response.json()
                        print("✅ 成功解析JSON数据")
                        
                        # 保存完整8个水表的数据
                        timestamp = time.strftime('%Y%m%d_%H%M%S')
                        today_str = datetime.now().strftime('%Y%m%d')
                        filename = f"COMPLETE_8_METERS_data_{today_str}_{timestamp}.json"
                        
                        output_data = {
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'source': 'complete_8_meters_scraper',
                            'success': True,
                            'data_type': 'json',
                            'calculation_date': datetime.now().strftime('%Y-%m-%d'),
                            'date_range': {
                                'start': start_date,
                                'end': end_date,
                                'description': '昨天往前推7天的数据'
                            },
                            'meter_count': len(meter_ids),
                            'target_meters': {
                                'ids': meter_ids,
                                'names': meter_names,
                                'total': len(meter_ids)
                            },
                            'data': data,
                            'note': f'这是{datetime.now().strftime("%Y年%m月%d日")}获取的完整8个水表最近7天真实数据'
                        }
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(output_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"🎉 完整8个水表数据已保存到: {filename}")
                        
                        # 显示详细数据摘要
                        print(f"\n📊 完整8个水表 {start_date} 至 {end_date} 数据摘要:")
                        if isinstance(data, dict):
                            total = data.get('total', 0)
                            rows = data.get('rows', [])
                            print(f"API返回总记录数: {total}")
                            print(f"实际获取行数: {len(rows)}")
                            print(f"目标水表数量: {len(meter_ids)}")
                            
                            if len(rows) == len(meter_ids):
                                print("✅ 成功获取所有8个水表数据！")
                            else:
                                print(f"⚠️  只获取到 {len(rows)} 个水表，缺少 {len(meter_ids) - len(rows)} 个")
                            
                            if rows:
                                # 分析日期范围
                                sample_row = rows[0] if rows else {}
                                date_columns = [key for key in sample_row.keys() if key.startswith('202')]
                                date_columns.sort()
                                
                                print(f"数据包含日期: {', '.join(date_columns)}")
                                print(f"实际天数: {len(date_columns)} 天")
                                
                                # 显示每个水表的详细信息
                                print(f"\n📋 各水表数据详情:")
                                for i, row in enumerate(rows):
                                    if isinstance(row, dict):
                                        meter_id = row.get('ID', 'N/A')
                                        meter_name = row.get('Name', 'N/A')
                                        max_value = row.get('maxvalue', 'N/A')
                                        min_value = row.get('minvalue', 'N/A')
                                        avg_value = row.get('avg', 'N/A')
                                        
                                        print(f"\n水表{i+1}: {meter_name} ({meter_id})")
                                        
                                        # 检查这个水表是否在我们的目标列表中
                                        if meter_id in meter_ids:
                                            target_index = meter_ids.index(meter_id)
                                            expected_name = meter_names[target_index]
                                            print(f"  ✅ 目标水表 #{target_index+1}: {expected_name}")
                                        else:
                                            print(f"  ⚠️  意外的水表ID")
                                        
                                        if max_value != 'N/A' and max_value is not None:
                                            print(f"  最大值: {max_value}")
                                            print(f"  最小值: {min_value}")
                                            print(f"  平均值: {avg_value}")
                                        
                                        # 显示最近几天的数据
                                        recent_data = []
                                        for date_col in date_columns[-3:]:  # 最近3天
                                            value = row.get(date_col)
                                            if value is not None:
                                                recent_data.append(f"{date_col}: {value}")
                                        
                                        if recent_data:
                                            print(f"  最近数据: {', '.join(recent_data)}")
                                
                                # 检查缺失的水表
                                returned_ids = [row.get('ID') for row in rows if isinstance(row, dict)]
                                missing_ids = [mid for mid in meter_ids if mid not in returned_ids]
                                
                                if missing_ids:
                                    print(f"\n⚠️  缺失的水表ID:")
                                    for mid in missing_ids:
                                        idx = meter_ids.index(mid)
                                        print(f"  - {mid} ({meter_names[idx]})")
                                else:
                                    print(f"\n✅ 所有8个目标水表数据都已获取！")
                            
                            else:
                                print("⚠️  没有返回水表数据")
                        
                        return True
                        
                    except json.JSONDecodeError:
                        print("响应不是JSON格式")
                        with open('complete_8_meters_api_response.txt', 'w', encoding='utf-8') as f:
                            f.write(api_response.text)
                        print("API响应已保存到 complete_8_meters_api_response.txt")
                        return False
                
                else:
                    print("❌ API返回空响应")
                    return False
            else:
                print("❌ 访问报表页面时显示登录超时")
                return False
        else:
            print("❌ 无法访问主页面")
            return False
    else:
        print("❌ 登录失败，未检测到重定向")
        return False

if __name__ == "__main__":
    success = get_complete_8_meters_data()
    if success:
        print(f"\n🎉🎉🎉 成功获取完整8个水表的最近7天真实数据！🎉🎉🎉")
        print("所有目标水表的数据都已保存到文件中！")
    else:
        print("\n❌ 获取完整8个水表数据失败")
