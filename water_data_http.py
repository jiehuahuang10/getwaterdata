#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据获取脚本 - HTTP请求版本
功能：使用HTTP请求直接获取广州增城自来水公司ThinkWater智慧水网系统数据
"""

import requests
import re
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, urlparse


class WaterDataHttpScraper:
    def __init__(self):
        """初始化HTTP爬虫"""
        self.session = requests.Session()
        
        # 系统登录信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 设置请求头，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 禁用SSL验证警告
        requests.packages.urllib3.disable_warnings()
    
    def get_login_page(self):
        """获取登录页面，提取必要的参数"""
        print("正在获取登录页面...")
        
        try:
            response = self.session.get(self.login_url, timeout=10)
            response.raise_for_status()
            
            print(f"登录页面状态码: {response.status_code}")
            print(f"页面标题: {response.text[:100]}...")
            
            # 解析HTML页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找表单
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            if not form:
                print("❌ 未找到登录表单")
                return None
            
            print("✅ 找到登录表单")
            
            # 提取表单数据
            form_data = {}
            
            # 查找所有input元素
            inputs = form.find_all('input')
            for input_elem in inputs:
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                input_type = input_elem.get('type', 'text')
                
                if name:
                    form_data[name] = value
                    print(f"表单字段: {name} = {value} (type: {input_type})")
            
            # 查找用户名和密码字段
            username_field = None
            password_field = None
            
            for input_elem in inputs:
                name = input_elem.get('name', '')
                input_type = input_elem.get('type', 'text')
                
                if 'user' in name.lower() or 'name' in name.lower():
                    username_field = name
                elif input_type == 'password':
                    password_field = name
            
            print(f"用户名字段: {username_field}")
            print(f"密码字段: {password_field}")
            
            return {
                'form_data': form_data,
                'username_field': username_field,
                'password_field': password_field,
                'action': form.get('action', ''),
                'soup': soup
            }
            
        except requests.RequestException as e:
            print(f"获取登录页面失败: {e}")
            return None
    
    def login(self):
        """执行登录"""
        print("开始登录系统...")
        
        # 获取登录页面信息
        login_info = self.get_login_page()
        if not login_info:
            return False
        
        form_data = login_info['form_data']
        username_field = login_info['username_field']
        password_field = login_info['password_field']
        action = login_info['action']
        
        if not username_field or not password_field:
            print("❌ 未找到用户名或密码字段")
            return False
        
        # 设置登录凭据
        form_data[username_field] = self.username
        form_data[password_field] = self.password
        
        print(f"准备登录数据:")
        for key, value in form_data.items():
            if 'password' in key.lower():
                print(f"  {key}: {'*' * len(str(value))}")
            else:
                print(f"  {key}: {value}")
        
        # 确定登录URL
        if action:
            login_post_url = urljoin(self.base_url, action)
        else:
            login_post_url = self.login_url
        
        print(f"登录POST URL: {login_post_url}")
        
        try:
            # 发送登录请求
            print("正在发送登录请求...")
            response = self.session.post(
                login_post_url,
                data=form_data,
                timeout=15,
                allow_redirects=True
            )
            
            print(f"登录响应状态码: {response.status_code}")
            print(f"最终URL: {response.url}")
            
            # 检查是否登录成功
            if self.check_login_success(response):
                print("✅ 登录成功！")
                return True
            else:
                print("❌ 登录失败")
                # 打印响应内容以便调试
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                print(f"页面标题: {title.text if title else '未知'}")
                
                # 查找错误信息
                error_elements = soup.find_all(['div', 'span'], class_=re.compile(r'error|alert|warning', re.I))
                for error in error_elements:
                    if error.text.strip():
                        print(f"错误信息: {error.text.strip()}")
                
                return False
                
        except requests.RequestException as e:
            print(f"登录请求失败: {e}")
            return False
    
    def check_login_success(self, response):
        """检查登录是否成功"""
        # 检查URL变化
        if "Login.aspx" not in response.url and ("Main" in response.url or "main" in response.url):
            return True
        
        # 检查页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找成功登录的标志
        success_indicators = [
            'ThinkWater',
            '智慧水网',
            '用户',
            '退出',
            '报表',
            'frmMain'
        ]
        
        page_text = response.text.lower()
        for indicator in success_indicators:
            if indicator.lower() in page_text:
                print(f"找到登录成功标志: {indicator}")
                return True
        
        # 检查是否还在登录页面
        if "用户名" in response.text and "密码" in response.text:
            return False
        
        return True
    
    def get_reports_page(self):
        """获取报表页面"""
        print("正在获取报表页面...")
        
        # 常见的报表页面URL
        report_urls = [
            f"{self.base_url}/Report/Default.aspx",
            f"{self.base_url}/Reports.aspx",
            f"{self.base_url}/Report.aspx",
            f"{self.base_url}/frmReport.aspx"
        ]
        
        for url in report_urls:
            try:
                print(f"尝试访问: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ 成功访问报表页面: {url}")
                    return response
                else:
                    print(f"❌ 访问失败，状态码: {response.status_code}")
                    
            except requests.RequestException as e:
                print(f"❌ 访问 {url} 失败: {e}")
                continue
        
        print("❌ 无法访问报表页面，尝试查找链接...")
        return None
    
    def find_report_links(self):
        """查找主页面中的报表链接"""
        print("正在查找报表相关链接...")
        
        try:
            # 获取主页面
            main_urls = [
                f"{self.base_url}/frmMain.aspx",
                f"{self.base_url}/Main.aspx",
                f"{self.base_url}/Default.aspx"
            ]
            
            for url in main_urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # 查找包含"报表"的链接
                        links = soup.find_all('a', href=True)
                        for link in links:
                            href = link.get('href')
                            text = link.text.strip()
                            
                            if '报表' in text or 'report' in href.lower():
                                full_url = urljoin(self.base_url, href)
                                print(f"找到报表链接: {text} -> {full_url}")
                                
                                # 尝试访问这个链接
                                try:
                                    report_response = self.session.get(full_url, timeout=10)
                                    if report_response.status_code == 200:
                                        return report_response
                                except:
                                    continue
                        
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"查找报表链接失败: {e}")
        
        return None
    
    def get_water_data_api(self):
        """尝试通过API直接获取数据"""
        print("正在尝试通过API获取数据...")
        
        # 常见的API端点
        api_endpoints = [
            f"{self.base_url}/api/WaterData",
            f"{self.base_url}/Handler/WaterData.ashx",
            f"{self.base_url}/ajax/GetWaterData.aspx",
            f"{self.base_url}/GetData.aspx"
        ]
        
        # 目标水表ID
        meter_ids = [
            "126118100026",  # 荔新大道DN1200流量计
            "126118100030",  # 新塘大道医院DN800流量计  
            "126233040233",  # 宁西总表DN1200
            "2190066",       # 三江新总表DN800
            "2190493",       # 沙庄总表
            "2501200108",    # 2501200108
            "2520005",       # 如丰大道600监控表
            "2520006"        # 三棒桥600监控表
        ]
        
        # 构造请求参数
        params = {
            'reportType': 'daily',
            'startDate': '2025-07-24',
            'endDate': '2025-07-31',
            'meterIds': ','.join(meter_ids)
        }
        
        for endpoint in api_endpoints:
            try:
                print(f"尝试API端点: {endpoint}")
                
                # GET请求
                response = self.session.get(endpoint, params=params, timeout=10)
                if response.status_code == 200:
                    print(f"✅ API调用成功: {endpoint}")
                    return self.parse_api_response(response)
                
                # POST请求
                response = self.session.post(endpoint, data=params, timeout=10)
                if response.status_code == 200:
                    print(f"✅ API调用成功: {endpoint}")
                    return self.parse_api_response(response)
                    
            except Exception as e:
                print(f"❌ API调用失败 {endpoint}: {e}")
                continue
        
        return False
    
    def parse_api_response(self, response):
        """解析API响应"""
        try:
            # 尝试解析JSON
            if 'json' in response.headers.get('content-type', '').lower():
                data = response.json()
                print("✅ 获取到JSON数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return True
            
            # 尝试解析HTML表格
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            
            if tables:
                print("✅ 找到数据表格:")
                for i, table in enumerate(tables):
                    print(f"\n表格 {i+1}:")
                    rows = table.find_all('tr')
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            print(f"  行 {j+1}: {' | '.join(row_data)}")
                return True
            
            # 打印原始文本
            if response.text.strip():
                print("响应内容:")
                print(response.text[:1000])
                return True
                
        except Exception as e:
            print(f"解析响应失败: {e}")
        
        return False
    
    def get_water_data(self):
        """完整的数据获取流程"""
        print("\n" + "="*60)
        print("🚀 开始HTTP请求方式的水务数据获取流程")
        print("="*60)
        
        try:
            # 1. 登录
            if not self.login():
                print("❌ 登录失败，终止流程")
                return False
            
            # 2. 尝试通过API获取数据
            if self.get_water_data_api():
                print("✅ 通过API成功获取数据")
                return True
            
            # 3. 尝试访问报表页面
            report_response = self.get_reports_page()
            if not report_response:
                report_response = self.find_report_links()
            
            if report_response:
                print("✅ 成功访问报表页面")
                
                # 先尝试从当前页面提取数据
                if self.extract_data_from_html(report_response.text, report_response.url):
                    return True
                
                # 如果没有数据，尝试提交查询请求
                print("当前页面无数据，尝试提交查询请求...")
                soup = BeautifulSoup(report_response.text, 'html.parser')
                query_response = self.submit_report_query(report_response.url, soup)
                
                if query_response:
                    return self.extract_data_from_html(query_response.text, query_response.url)
                else:
                    print("❌ 查询请求失败")
                    return False
            else:
                print("❌ 无法访问报表页面")
                return False
            
        except Exception as e:
            print(f"❌ 数据获取流程中发生错误: {e}")
            return False
    
    def analyze_report_page(self, html_content):
        """分析报表页面结构"""
        print("正在分析报表页面结构...")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 保存页面内容到文件以便调试
            with open('report_page.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("✅ 报表页面内容已保存到 report_page.html")
            
            # 查找表单
            forms = soup.find_all('form')
            print(f"找到 {len(forms)} 个表单")
            
            for i, form in enumerate(forms):
                print(f"\n表单 {i+1}:")
                print(f"  Action: {form.get('action', '未设置')}")
                print(f"  Method: {form.get('method', '未设置')}")
                
                # 查找表单中的输入字段
                inputs = form.find_all(['input', 'select', 'textarea'])
                for input_elem in inputs:
                    name = input_elem.get('name', '')
                    input_type = input_elem.get('type', input_elem.name)
                    value = input_elem.get('value', '')
                    
                    if name:
                        print(f"    {name}: {input_type} = {value}")
            
            # 查找下拉框选项
            selects = soup.find_all('select')
            for select in selects:
                select_name = select.get('name', '未知')
                print(f"\n下拉框 {select_name}:")
                options = select.find_all('option')
                for option in options:
                    value = option.get('value', '')
                    text = option.get_text(strip=True)
                    print(f"  {value}: {text}")
            
            return soup
            
        except Exception as e:
            print(f"分析报表页面失败: {e}")
            return None
    
    def get_ajax_data(self, report_url):
        """尝试通过Ajax获取数据"""
        print("正在尝试通过Ajax获取数据...")
        
        # 常见的Ajax端点
        ajax_endpoints = [
            f"{report_url}?action=getData",
            f"{report_url}?method=getdata",
            f"{self.base_url}/reports/GetFluxData.aspx",
            f"{self.base_url}/Handler/FluxData.ashx",
            f"{self.base_url}/reports/ajax/GetData.aspx"
        ]
        
        # 构造Ajax请求参数
        ajax_params = {
            'rptType': '1',  # 日报表
            'meterType': '',  # 所有类型
            'startDate': '2025-07-24',
            'endDate': '2025-07-31',
            'user': '126118100026,126118100030,126233040233,2190066,2190493,2501200108,2520005,2520006',
            'page': '1',
            'rows': '100'
        }
        
        for endpoint in ajax_endpoints:
            try:
                print(f"尝试Ajax端点: {endpoint}")
                
                # GET请求
                response = self.session.get(endpoint, params=ajax_params, timeout=10)
                if response.status_code == 200 and response.text.strip():
                    print(f"✅ Ajax GET成功: {endpoint}")
                    return self.parse_ajax_response(response)
                
                # POST请求
                response = self.session.post(endpoint, data=ajax_params, timeout=10)
                if response.status_code == 200 and response.text.strip():
                    print(f"✅ Ajax POST成功: {endpoint}")
                    return self.parse_ajax_response(response)
                    
            except Exception as e:
                print(f"❌ Ajax请求失败 {endpoint}: {e}")
                continue
        
        return False
    
    def parse_ajax_response(self, response):
        """解析Ajax响应"""
        try:
            content_type = response.headers.get('content-type', '').lower()
            
            # JSON响应
            if 'json' in content_type:
                data = response.json()
                print("✅ 获取到JSON数据:")
                self.format_json_data(data)
                return True
            
            # HTML表格响应
            elif 'html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                tables = soup.find_all('table')
                if tables:
                    print("✅ 获取到HTML表格数据:")
                    return self.extract_data_from_html(response.text)
            
            # 纯文本响应
            else:
                text = response.text.strip()
                if text:
                    print("✅ 获取到文本数据:")
                    print(text[:1000])
                    return True
                    
        except Exception as e:
            print(f"解析Ajax响应失败: {e}")
        
        return False
    
    def format_json_data(self, data):
        """格式化JSON数据"""
        try:
            print("\n" + "="*80)
            print("📊 水表数据获取结果（JSON格式）：")
            print("="*80)
            
            if isinstance(data, dict):
                if 'rows' in data:
                    rows = data['rows']
                    if rows:
                        # 打印表头
                        if isinstance(rows[0], dict):
                            headers = list(rows[0].keys())
                            print("表头:", " | ".join(headers))
                            print("-" * 80)
                            
                            # 打印数据行
                            for i, row in enumerate(rows):
                                row_data = [str(row.get(h, '')) for h in headers]
                                print(f"第{i+1}行:", " | ".join(row_data))
                
                elif 'data' in data:
                    print("数据内容:", json.dumps(data['data'], indent=2, ensure_ascii=False))
                
                else:
                    print("完整数据:", json.dumps(data, indent=2, ensure_ascii=False))
            
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    print(f"项目 {i+1}:", json.dumps(item, indent=2, ensure_ascii=False))
            
            print("="*80)
            
        except Exception as e:
            print(f"格式化JSON数据失败: {e}")
    
    def submit_report_query(self, report_url, soup):
        """提交报表查询请求"""
        print("正在提交报表查询请求...")
        
        # 首先尝试Ajax方式获取数据
        if self.get_ajax_data(report_url):
            return True
        
        try:
            # 查找表单
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            if not form:
                print("❌ 未找到查询表单")
                return None
            
            # 构建表单数据
            form_data = {}
            
            # 获取所有隐藏字段
            hidden_inputs = form.find_all('input', {'type': 'hidden'})
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value', '')
                if name:
                    form_data[name] = value
            
            # 添加查询参数（基于HTML分析）
            form_data.update({
                'rptType': '1',  # 日报表
                'startDate': '2025-07-24',
                'endDate': '2025-07-31',
                'user': '126118100026',  # 先测试一个水表
                'meterType': '',  # 所有类型
                'search': '查询'
            })
            
            print("查询表单数据:")
            for key, value in form_data.items():
                print(f"  {key}: {value}")
            
            # 发送查询请求
            query_url = urljoin(report_url, form.get('action', ''))
            print(f"查询URL: {query_url}")
            
            response = self.session.post(query_url, data=form_data, timeout=15)
            print(f"查询响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                return response
            else:
                print("❌ 查询请求失败")
                return None
                
        except Exception as e:
            print(f"提交查询请求失败: {e}")
            return None
    
    def extract_data_from_html(self, html_content, page_url=None):
        """从HTML内容中提取数据"""
        print("正在从HTML中提取数据...")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 分析页面结构
            analyzed_soup = self.analyze_report_page(html_content)
            if not analyzed_soup:
                return False
            
            # 查找所有表格
            tables = soup.find_all('table')
            print(f"找到 {len(tables)} 个表格")
            
            if not tables:
                print("❌ 未找到数据表格，可能需要提交查询请求")
                return False
            
            # 分析每个表格
            has_data = False
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) > 1:  # 有数据的表格
                    print(f"\n📊 表格 {i+1} 包含 {len(rows)} 行数据:")
                    print("="*80)
                    
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if any(row_data):  # 只打印非空行
                                has_data = True
                                if j == 0:
                                    print("表头:", " | ".join(row_data))
                                    print("-" * 80)
                                else:
                                    print(f"第{j}行:", " | ".join(row_data))
                    
                    print("="*80)
            
            if has_data:
                print("\n✅ 数据提取完成")
                return True
            else:
                print("⚠️  所有表格均为空")
                return False
            
        except Exception as e:
            print(f"数据提取失败: {e}")
            return False


def main():
    """主函数"""
    scraper = WaterDataHttpScraper()
    
    try:
        # 执行完整的数据获取流程
        if scraper.get_water_data():
            print("\n🎉 HTTP方式数据获取成功！")
        else:
            print("\n❌ HTTP方式数据获取失败！")
            
    except KeyboardInterrupt:
        print("用户中断程序")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()