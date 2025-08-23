#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能水务数据获取脚本 - 使用实际日期和更智能的参数探测
"""

import requests
import re
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta


class SmartWaterDataScraper:
    def __init__(self):
        """初始化HTTP爬虫"""
        self.session = requests.Session()
        
        # 系统登录信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 计算实际的日期范围（使用过去的日期，可能有数据）
        today = datetime.now()
        end_date = today - timedelta(days=30)  # 30天前（更可能有历史数据）
        start_date = end_date - timedelta(days=6)  # 再往前7天
        
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.end_date = end_date.strftime('%Y-%m-%d')
        
        print(f"📅 使用日期范围: {self.start_date} 到 {self.end_date}")
        
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
                
                # 发送登录请求
                login_response = self.session.post(
                    self.login_url,
                    data=form_data,
                    timeout=15,
                    allow_redirects=True
                )
                
                # 检查登录是否成功
                if "Login.aspx" not in login_response.url or "ThinkWater" in login_response.text:
                    print("✅ 登录成功！")
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
    
    def find_report_page(self):
        """查找报表页面"""
        print("正在查找报表页面...")
        
        try:
            # 获取主页面
            main_response = self.session.get(f"{self.base_url}/frmMain.aspx", timeout=10)
            if main_response.status_code == 200:
                soup = BeautifulSoup(main_response.text, 'html.parser')
                
                # 查找报表链接
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    text = link.text.strip()
                    
                    if '报表' in text or 'report' in href.lower():
                        full_url = urljoin(self.base_url, href)
                        print(f"找到报表链接: {text} -> {full_url}")
                        return full_url
            
            # 如果没找到，尝试直接访问已知的报表页面
            report_url = f"{self.base_url}/reports/FluxRpt.aspx"
            test_response = self.session.get(report_url, timeout=10)
            if test_response.status_code == 200:
                print(f"✅ 直接访问报表页面成功: {report_url}")
                return report_url
                
        except Exception as e:
            print(f"查找报表页面失败: {e}")
        
        return None
    
    def try_different_parameters(self, report_url):
        """尝试不同的参数组合获取数据"""
        print("正在尝试不同的参数组合...")
        
        # 不同的水表ID格式
        meter_variations = [
            "126118100026",
            "126118100030", 
            "126233040233",
            "2190066",
            "2190493",
            "2501200108",
            "2520005",
            "2520006"
        ]
        
        # 不同的参数组合
        param_combinations = [
            # 组合1：基本参数
            {
                'rptType': '1',
                'startDate': self.start_date,
                'endDate': self.end_date,
                'user': meter_variations[3],  # 使用2190066
                'meterType': '',
                'page': '1',
                'rows': '50'
            },
            # 组合2：实时数据
            {
                'reportType': 'realtime',
                'dateFrom': self.start_date,
                'dateTo': self.end_date,
                'meterId': meter_variations[3],
                'type': 'flux'
            },
            # 组合3：日报表格式
            {
                'type': 'daily',
                'begin': self.start_date,
                'end': self.end_date,
                'meters': meter_variations[3],
                'format': 'json'
            },
            # 组合4：使用不同日期格式
            {
                'rptType': '1',
                'startDate': self.start_date.replace('-', '/'),
                'endDate': self.end_date.replace('-', '/'),
                'user': meter_variations[3],
                'statisticsType': '1'
            }
        ]
        
        # 可能的Ajax端点
        ajax_endpoints = [
            f"{report_url}",
            f"{report_url}?action=getData",
            f"{self.base_url}/reports/GetFluxData.aspx",
            f"{self.base_url}/Handler/GetReportData.ashx",
            f"{self.base_url}/ajax/FluxReport.ashx",
            f"{self.base_url}/reports/ajax/getData.aspx"
        ]
        
        # 尝试每个参数组合和端点
        for i, params in enumerate(param_combinations):
            print(f"\n🔄 尝试参数组合 {i+1}: {params}")
            
            for endpoint in ajax_endpoints:
                try:
                    # GET请求
                    response = self.session.get(endpoint, params=params, timeout=10)
                    if self.check_response_has_data(response, f"GET {endpoint}"):
                        return True
                    
                    # POST请求
                    response = self.session.post(endpoint, data=params, timeout=10)
                    if self.check_response_has_data(response, f"POST {endpoint}"):
                        return True
                        
                except Exception as e:
                    continue
        
        return False
    
    def check_login_timeout(self, content):
        """检查是否登录超时"""
        if '登录超时' in content or '重新登录' in content or 'Login.aspx' in content:
            print("⚠️  检测到登录超时，尝试重新登录...")
            if self.login():
                print("✅ 重新登录成功")
                return True
            else:
                print("❌ 重新登录失败")
                return False
        return False
    
    def check_response_has_data(self, response, request_info):
        """检查响应是否包含数据"""
        try:
            if response.status_code != 200:
                return False
            
            content = response.text.strip()
            if not content:
                return False
            
            # 检查登录超时
            if self.check_login_timeout(content):
                return False  # 需要重试
            
            # 排除无意义的响应
            if (len(content) < 50 or 
                '登录超时' in content or 
                'alert(' in content or
                content == 'null' or
                content == '[]' or
                content == '{}'):
                return False
            
            # 检查JSON响应
            try:
                if response.headers.get('content-type', '').lower().find('json') >= 0:
                    data = response.json()
                    if data and (isinstance(data, dict) and data.get('rows') or 
                               isinstance(data, list) and len(data) > 0):
                        print(f"✅ {request_info} - 获取到JSON数据:")
                        self.display_json_data(data)
                        return True
            except:
                pass
            
            # 检查HTML响应
            if '<table' in content or '<tr' in content:
                soup = BeautifulSoup(content, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # 有数据行
                        data_rows = []
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if cells:
                                row_data = [cell.get_text(strip=True) for cell in cells]
                                if any(row_data):  # 非空行
                                    data_rows.append(row_data)
                        
                        if len(data_rows) > 1:  # 除了表头还有数据
                            print(f"✅ {request_info} - 获取到HTML表格数据:")
                            self.display_table_data(data_rows)
                            return True
            
            # 检查其他格式的有意义数据
            meaningful_keywords = ['水表', 'meter', 'flux', '流量', '用水量', '抄表时间', '最小值', '平均值']
            if (len(content) > 100 and 
                any(keyword in content.lower() for keyword in meaningful_keywords) and
                'alert(' not in content):
                print(f"✅ {request_info} - 获取到文本数据:")
                print(content[:500] + "..." if len(content) > 500 else content)
                return True
                
        except Exception as e:
            print(f"❌ 检查响应数据失败: {e}")
        
        return False
    
    def display_json_data(self, data):
        """显示JSON数据"""
        try:
            print("\n" + "="*80)
            print("📊 水表数据获取结果（JSON格式）：")
            print("="*80)
            
            if isinstance(data, dict):
                if 'rows' in data and data['rows']:
                    rows = data['rows']
                    if isinstance(rows[0], dict):
                        headers = list(rows[0].keys())
                        print("表头:", " | ".join(headers))
                        print("-" * 80)
                        
                        for i, row in enumerate(rows[:10]):  # 只显示前10行
                            row_data = [str(row.get(h, '')) for h in headers]
                            print(f"第{i+1}行:", " | ".join(row_data))
                        
                        if len(rows) > 10:
                            print(f"... 还有 {len(rows) - 10} 行数据")
                
                else:
                    print("完整数据:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            
            elif isinstance(data, list) and data:
                for i, item in enumerate(data[:5]):  # 只显示前5项
                    print(f"项目 {i+1}:", json.dumps(item, indent=2, ensure_ascii=False))
                
                if len(data) > 5:
                    print(f"... 还有 {len(data) - 5} 项数据")
            
            print("="*80)
            
        except Exception as e:
            print(f"显示JSON数据失败: {e}")
    
    def display_table_data(self, data_rows):
        """显示表格数据"""
        try:
            print("\n" + "="*80)
            print("📊 水表数据获取结果（表格格式）：")
            print("="*80)
            
            if data_rows:
                # 表头
                print("表头:", " | ".join(data_rows[0]))
                print("-" * 80)
                
                # 数据行
                for i, row in enumerate(data_rows[1:11]):  # 只显示前10行数据
                    print(f"第{i+1}行:", " | ".join(row))
                
                if len(data_rows) > 11:
                    print(f"... 还有 {len(data_rows) - 11} 行数据")
            
            print("="*80)
            
        except Exception as e:
            print(f"显示表格数据失败: {e}")
    
    def get_water_data(self):
        """完整的数据获取流程"""
        print("\n" + "="*60)
        print("🚀 开始智能水务数据获取流程")
        print("="*60)
        
        try:
            # 1. 登录
            if not self.login():
                print("❌ 登录失败，终止流程")
                return False
            
            # 2. 查找报表页面
            report_url = self.find_report_page()
            if not report_url:
                print("❌ 未找到报表页面，终止流程")
                return False
            
            # 3. 使用不同参数尝试获取数据
            if self.try_different_parameters(report_url):
                print("\n🎉 成功获取到水务数据！")
                return True
            else:
                print("\n❌ 尝试了所有参数组合，仍未获取到数据")
                return False
            
        except Exception as e:
            print(f"❌ 数据获取流程中发生错误: {e}")
            return False


def main():
    """主函数"""
    scraper = SmartWaterDataScraper()
    
    try:
        if scraper.get_water_data():
            print("\n✅ 智能数据获取成功！")
        else:
            print("\n❌ 智能数据获取失败！")
            
    except KeyboardInterrupt:
        print("用户中断程序")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()