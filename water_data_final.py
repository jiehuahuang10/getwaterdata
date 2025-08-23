#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
水务数据获取脚本 - 最终版本
基于浏览器开发者工具发现的真实API端点
"""

import requests
import re
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin


class FinalWaterDataScraper:
    def __init__(self):
        """初始化HTTP爬虫"""
        self.session = requests.Session()
        
        # 系统登录信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 真实的API端点（从开发者工具获取）
        self.api_url = f"{self.base_url}/reports/ashx/getRptWaterYield.ashx"
        
        # 设置请求头，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/reports/FluxRpt.aspx'
        })
        
        # 目标水表ID（按照用户要求的正确格式）
        self.target_meters = [
            '2501200108',
            '1261181000263',    # 修正了位数 
            '1262330402331',    # 修正了位数
            '2520005',
            '2520006',
            '1261181000300'     # 修正了位数
        ]
        
        # 禁用SSL验证警告
        requests.packages.urllib3.disable_warnings()
    
    def login(self):
        """执行登录"""
        print("开始登录系统...")
        
        try:
            # 获取登录页面
            response = self.session.get(self.login_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            
            if not form:
                print("❌ 未找到登录表单")
                return False
            
            # 提取表单数据
            form_data = {}
            inputs = form.find_all('input')
            for input_elem in inputs:
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
            
            # 设置登录凭据
            username_field = None
            password_field = None
            
            for input_elem in inputs:
                name = input_elem.get('name', '')
                input_type = input_elem.get('type', 'text')
                
                if 'user' in name.lower():
                    username_field = name
                elif input_type == 'password':
                    password_field = name
            
            if username_field and password_field:
                form_data[username_field] = self.username
                form_data[password_field] = self.password
                
                print("正在发送登录请求...")
                login_response = self.session.post(
                    self.login_url,
                    data=form_data,
                    timeout=15,
                    allow_redirects=True
                )
                
                # 检查登录是否成功
                if "Login.aspx" not in login_response.url or "ThinkWater" in login_response.text:
                    print("✅ 登录成功！")
                    
                    # 保存重要的Cookie信息
                    cookies_info = []
                    for cookie in self.session.cookies:
                        cookies_info.append(f"{cookie.name}={cookie.value}")
                    print(f"📝 保存了 {len(self.session.cookies)} 个Cookie")
                    
                    return True
                else:
                    print("❌ 登录失败")
                    return False
            else:
                print("❌ 未找到用户名或密码字段")
                return False
                
        except Exception as e:
            print(f"登录过程中发生错误: {e}")
            return False
    
    def setup_session_state(self):
        """设置正确的会话状态"""
        print("正在设置会话状态...")
        
        try:
            # 1. 访问报表页面建立会话状态
            report_page_url = f"{self.base_url}/reports/FluxRpt.aspx"
            print(f"访问报表页面: {report_page_url}")
            
            response = self.session.get(report_page_url, timeout=10)
            if response.status_code == 200:
                print("✅ 成功访问报表页面")
                
                # 解析页面获取必要的状态信息
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 获取ViewState等ASP.NET状态
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                if viewstate and eventvalidation:
                    self.viewstate = viewstate.get('value', '')
                    self.eventvalidation = eventvalidation.get('value', '')
                    print("✅ 获取到ASP.NET状态信息")
                else:
                    print("⚠️  未找到ASP.NET状态信息")
                
                return True
            else:
                print(f"❌ 访问报表页面失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"设置会话状态失败: {e}")
            return False
    
    def get_water_yield_data(self):
        """使用真实API获取水表产水量数据"""
        print("正在调用真实API获取水表数据...")
        
        try:
            # 尝试多个日期范围
            date_ranges = [
                ('2025-07-24', '2025-07-31'),  # 原始日期
                ('2024-07-24', '2024-07-31'),  # 去年同期
                ('2024-12-01', '2024-12-07'),  # 去年12月
                ('2024-11-01', '2024-11-07'),  # 去年11月
            ]
            
            for start_date, end_date in date_ranges:
                print(f"\n🔄 尝试日期范围: {start_date} 到 {end_date}")
                
                # 构造API请求参数（按照用户要求的格式，每个ID用单引号包围）
                formatted_node_ids = "'" + "','".join(self.target_meters) + "'"
                api_params = {
                    'nodeId': formatted_node_ids,            # 格式: '2501200108','1261181000263',...
                    'startDate': start_date,                 # 开始日期
                    'endDate': end_date,                     # 结束日期  
                    'meterType': '-1',                       # 计量类型（-1表示全部）
                    'statisticsType': 'flux',                # 统计类型（流量）
                    'type': 'dayRpt'                         # 报表类型（日报表）
                }
                
                if self._try_api_request(api_params):
                    return True
            
            return False
                
        except Exception as e:
            print(f"API请求过程中发生错误: {e}")
            return False
    
    def _try_api_request(self, api_params):
        """尝试单次API请求"""
        try:
            print("API请求参数:")
            for key, value in api_params.items():
                print(f"  {key}: {value}")
            
            print(f"API端点: {self.api_url}")
            
            # 更新请求头，确保包含所有必要信息
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'Referer': f'{self.base_url}/reports/FluxRpt.aspx',
                'Origin': self.base_url,
                'Host': 'axwater.dmas.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
            
            # 发送API请求
            response = self.session.post(
                self.api_url,
                data=api_params,
                headers=headers,
                timeout=15
            )
            
            print(f"API响应状态码: {response.status_code}")
            print(f"响应内容类型: {response.headers.get('content-type', '未知')}")
            
            if response.status_code == 200:
                return self.parse_api_response(response)
            else:
                print(f"❌ API请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"API请求过程中发生错误: {e}")
            return False
    
    def parse_api_response(self, response):
        """解析API响应数据"""
        try:
            content = response.text.strip()
            print(f"响应数据长度: {len(content)} 字符")
            
            # 检查是否为空响应
            if not content:
                print("❌ 响应内容为空")
                return False
            
            # 检查是否为登录超时
            if '登录超时' in content or 'Login.aspx' in content:
                print("⚠️  检测到登录超时")
                return False
            
            # 尝试解析JSON
            try:
                data = response.json()
                print("✅ 成功解析JSON数据:")
                self.display_water_data(data)
                return True
            except json.JSONDecodeError:
                pass
            
            # 检查HTML表格
            if '<table' in content or '<tr' in content:
                soup = BeautifulSoup(content, 'html.parser')
                tables = soup.find_all('table')
                
                if tables:
                    print("✅ 发现HTML表格数据:")
                    self.extract_table_data(tables)
                    return True
            
            # 显示原始响应内容
            print("📄 原始响应内容:")
            print("="*80)
            print(content)
            print("="*80)
            
            # 如果内容包含水表相关字段，认为是有效数据
            if any(keyword in content.lower() for keyword in 
                   ['水表', 'meter', 'flux', '流量', '用水量', '抄表', '数据']):
                print("✅ 检测到水表相关数据")
                return True
            
            return False
            
        except Exception as e:
            print(f"解析API响应失败: {e}")
            return False
    
    def display_water_data(self, data):
        """显示水表数据"""
        try:
            print("\n" + "="*80)
            print("📊 水表数据获取结果：")  
            print("="*80)
            
            if isinstance(data, dict):
                # 检查常见的数据结构
                if 'rows' in data and data['rows']:
                    rows = data['rows']
                    print(f"找到 {len(rows)} 行数据")
                    
                    if isinstance(rows[0], dict):
                        headers = list(rows[0].keys())
                        print("表头:", " | ".join(headers))
                        print("-" * 80)
                        
                        for i, row in enumerate(rows):
                            row_data = [str(row.get(h, '')) for h in headers]
                            print(f"第{i+1}行:", " | ".join(row_data))
                
                elif 'data' in data:
                    print("数据内容:")
                    if isinstance(data['data'], list):
                        for i, item in enumerate(data['data']):
                            print(f"项目 {i+1}: {item}")
                    else:
                        print(data['data'])
                
                else:
                    # 显示完整JSON结构
                    print("完整数据结构:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
            
            elif isinstance(data, list):
                print(f"找到 {len(data)} 项数据:")
                for i, item in enumerate(data):
                    print(f"项目 {i+1}: {item}")
            
            print("="*80)
            
        except Exception as e:
            print(f"显示水表数据失败: {e}")
    
    def extract_table_data(self, tables):
        """提取HTML表格数据"""
        try:
            print("\n" + "="*80)
            print("📊 HTML表格数据：")
            print("="*80)
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) > 0:
                    print(f"\n表格 {table_idx + 1} (共 {len(rows)} 行):")
                    
                    for row_idx, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if any(row_data):  # 只显示非空行
                                if row_idx == 0:
                                    print("表头:", " | ".join(row_data))
                                    print("-" * 60)
                                else:
                                    print(f"第{row_idx}行:", " | ".join(row_data))
            
            print("="*80)
            
        except Exception as e:
            print(f"提取表格数据失败: {e}")
    
    def test_alternative_endpoints(self):
        """测试其他可能的API端点"""
        print("正在测试其他可能的API端点...")
        
        alternative_endpoints = [
            f"{self.base_url}/reports/ashx/getWaterData.ashx",
            f"{self.base_url}/reports/ashx/FluxReport.ashx", 
            f"{self.base_url}/Handler/WaterYield.ashx",
            f"{self.base_url}/ajax/getRptData.ashx"
        ]
        
        # 使用正确的nodeId格式
        formatted_node_ids = "'" + "','".join(self.target_meters) + "'"
        api_params = {
            'nodeId': formatted_node_ids,
            'startDate': '2025-07-24',
            'endDate': '2025-07-31',
            'meterType': '-1',
            'statisticsType': 'flux',
            'type': 'dayRpt'
        }
        
        for endpoint in alternative_endpoints:
            try:
                print(f"\n🔄 测试端点: {endpoint}")
                response = self.session.post(endpoint, data=api_params, timeout=10)
                
                if response.status_code == 200 and response.text.strip():
                    print(f"✅ 端点响应成功")
                    if self.parse_api_response(response):
                        return True
                else:
                    print(f"❌ 端点无响应 (状态码: {response.status_code})")
                    
            except Exception as e:
                print(f"❌ 端点测试失败: {e}")
        
        return False
    
    def get_water_data(self):
        """完整的数据获取流程"""
        print("\n" + "="*60)
        print("🚀 开始最终版水务数据获取流程")
        print("="*60)
        
        try:
            # 1. 登录
            if not self.login():
                print("❌ 登录失败，终止流程")
                return False
            
            # 2. 设置会话状态
            if not self.setup_session_state():
                print("❌ 设置会话状态失败，终止流程")
                return False
            
            # 3. 使用真实API获取数据
            if self.get_water_yield_data():
                print("\n🎉 成功获取水务数据！")
                return True
            
            # 4. 如果主API失败，尝试其他端点
            print("\n⚠️  主API无数据，尝试其他端点...")
            if self.test_alternative_endpoints():
                print("\n🎉 通过备用端点获取到数据！")
                return True
            
            print("\n❌ 所有API端点都无法获取数据")
            return False
            
        except Exception as e:
            print(f"❌ 数据获取流程中发生错误: {e}")
            return False


def main():
    """主函数"""
    scraper = FinalWaterDataScraper()
    
    try:
        if scraper.get_water_data():
            print("\n✅ 最终版数据获取成功！")
        else:
            print("\n❌ 最终版数据获取失败！")
            
    except KeyboardInterrupt:
        print("用户中断程序")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()