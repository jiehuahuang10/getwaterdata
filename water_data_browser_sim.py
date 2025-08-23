#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
水务数据获取脚本 - 完整浏览器模拟版本
模拟浏览器的完整操作流程
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, parse_qs, urlparse


class BrowserSimWaterScraper:
    def __init__(self):
        """初始化"""
        self.session = requests.Session()
        
        # 系统信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 设置完整的浏览器请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 存储表单状态
        self.viewstate = ""
        self.eventvalidation = ""
        
        requests.packages.urllib3.disable_warnings()
    
    def login(self):
        """登录"""
        print("开始登录...")
        
        try:
            # 获取登录页面
            response = self.session.get(self.login_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取表单数据
            form_data = {}
            for input_elem in soup.find_all('input'):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
            
            # 设置登录凭据
            form_data['user'] = self.username
            form_data['pwd'] = self.password
            
            # 登录
            login_response = self.session.post(
                self.login_url, 
                data=form_data, 
                timeout=15,
                allow_redirects=True
            )
            
            if "ThinkWater" in login_response.text:
                print("✅ 登录成功")
                return True
            else:
                print("❌ 登录失败")
                return False
                
        except Exception as e:
            print(f"登录异常: {e}")
            return False
    
    def get_report_page_state(self):
        """获取报表页面状态"""
        print("获取报表页面状态...")
        
        try:
            report_url = f"{self.base_url}/reports/FluxRpt.aspx"
            response = self.session.get(report_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取ASP.NET状态
                viewstate_elem = soup.find('input', {'name': '__VIEWSTATE'})
                eventvalidation_elem = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                if viewstate_elem and eventvalidation_elem:
                    self.viewstate = viewstate_elem.get('value', '')
                    self.eventvalidation = eventvalidation_elem.get('value', '')
                    print("✅ 获取页面状态成功")
                    return True
                else:
                    print("❌ 未找到页面状态信息")
                    return False
            else:
                print(f"❌ 访问报表页面失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"获取页面状态异常: {e}")
            return False
    
    def simulate_form_submission(self):
        """模拟表单提交"""
        print("模拟表单提交...")
        
        try:
            report_url = f"{self.base_url}/reports/FluxRpt.aspx"
            
            # 构造表单数据，模拟用户选择操作
            form_data = {
                '__VIEWSTATE': self.viewstate,
                '__EVENTVALIDATION': self.eventvalidation,
                'hiddenType': 'meterUseFluxRpt',
                # 尝试各种可能的参数名
                'rptType': '1',
                'startDate': '2024-07-24',
                'endDate': '2024-07-31',
                'user': '2501200108',  # 先试一个水表
                'meterType': '',
                'statisticsType': 'flux'
            }
            
            print("提交表单数据...")
            response = self.session.post(
                report_url,
                data=form_data,
                timeout=15,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': report_url
                }
            )
            
            print(f"表单提交响应: {response.status_code}")
            
            if response.status_code == 200:
                return self.analyze_response(response.text)
            else:
                print(f"表单提交失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"表单提交异常: {e}")
            return False
    
    def try_direct_data_request(self):
        """尝试直接数据请求"""
        print("尝试直接数据请求...")
        
        try:
            # 基于开发者工具的直接API调用
            api_url = f"{self.base_url}/reports/ashx/getRptWaterYield.ashx"
            
            # 尝试多种水表ID组合
            meter_combinations = [
                # 单个水表测试
                "'2501200108'",
                "'2520005'", 
                "'2520006'",
                # 组合测试
                "'2501200108','2520005'",
                "'2501200108','2520005','2520006'",
                # 您提供的完整组合
                "'2501200108','1261181000263','1262330402331','2520005','2520006','1261181000300'"
            ]
            
            for meter_ids in meter_combinations:
                print(f"\n🔄 测试水表组合: {meter_ids}")
                
                params = {
                    'nodeId': meter_ids,
                    'startDate': '2024-07-24',
                    'endDate': '2024-07-31',
                    'meterType': '-1',
                    'statisticsType': 'flux',
                    'type': 'dayRpt'
                }
                
                # 发送请求
                response = self.session.post(
                    api_url,
                    data=params,
                    timeout=15,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': f'{self.base_url}/reports/FluxRpt.aspx'
                    }
                )
                
                print(f"  状态码: {response.status_code}")
                print(f"  响应长度: {len(response.text)}")
                
                if response.text.strip():
                    print(f"  ✅ 有响应内容: {response.text[:200]}")
                    return True
                else:
                    print("  ❌ 响应为空")
            
            return False
            
        except Exception as e:
            print(f"直接数据请求异常: {e}")
            return False
    
    def explore_water_meters(self):
        """探索可用的水表"""
        print("探索可用的水表...")
        
        try:
            # 尝试获取水表列表的各种可能端点
            endpoints = [
                f"{self.base_url}/reports/ashx/getMeterList.ashx",
                f"{self.base_url}/ajax/getMeterList.aspx",
                f"{self.base_url}/reports/getMeterData.aspx",
                f"{self.base_url}/Handler/MeterList.ashx"
            ]
            
            for endpoint in endpoints:
                try:
                    print(f"尝试端点: {endpoint}")
                    response = self.session.get(endpoint, timeout=10)
                    
                    if response.status_code == 200 and response.text.strip():
                        print(f"✅ 端点有响应: {response.text[:300]}")
                        
                        # 尝试解析JSON
                        try:
                            data = response.json()
                            print("JSON数据:")
                            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                            return True
                        except:
                            pass
                        
                        return True
                    else:
                        print(f"端点无响应: {response.status_code}")
                        
                except Exception as e:
                    print(f"端点访问失败: {e}")
            
            return False
            
        except Exception as e:
            print(f"探索水表异常: {e}")
            return False
    
    def analyze_response(self, html_content):
        """分析响应内容"""
        try:
            if not html_content.strip():
                print("❌ 响应内容为空")
                return False
            
            print(f"响应内容长度: {len(html_content)}")
            
            # 检查是否包含数据
            if any(keyword in html_content.lower() for keyword in 
                   ['table', 'data', '数据', '水表', 'meter', 'flux']):
                print("✅ 响应包含相关内容:")
                print(html_content[:500])
                
                # 尝试提取表格
                soup = BeautifulSoup(html_content, 'html.parser')
                tables = soup.find_all('table')
                
                if tables:
                    print(f"找到 {len(tables)} 个表格")
                    for i, table in enumerate(tables):
                        rows = table.find_all('tr')
                        if rows:
                            print(f"\n📊 表格 {i+1}: {len(rows)} 行")
                            print("="*80)
                            
                            # 显示所有行
                            for j, row in enumerate(rows):
                                cells = row.find_all(['td', 'th'])
                                if cells:
                                    row_data = [cell.get_text(strip=True) for cell in cells]
                                    if any(row_data):  # 只显示非空行
                                        if j == 0:
                                            print("表头:", " | ".join(row_data))
                                            print("-" * 80)
                                        else:
                                            print(f"第{j}行:", " | ".join(row_data))
                            
                            print("="*80)
                
                return True
            else:
                print("响应内容预览:")
                print(html_content[:300])
                return False
                
        except Exception as e:
            print(f"分析响应异常: {e}")
            return False
    
    def run_simulation(self):
        """运行完整模拟"""
        print("\n" + "="*60)
        print("🌐 开始浏览器完整模拟")
        print("="*60)
        
        try:
            # 1. 登录
            if not self.login():
                return False
            
            # 2. 获取页面状态
            if not self.get_report_page_state():
                return False
            
            # 3. 探索可用水表
            print("\n--- 探索阶段 ---")
            self.explore_water_meters()
            
            # 4. 模拟表单提交
            print("\n--- 表单提交阶段 ---")
            if self.simulate_form_submission():
                print("✅ 表单提交成功获取数据")
                return True
            
            # 5. 直接数据请求
            print("\n--- 直接请求阶段 ---")
            if self.try_direct_data_request():
                print("✅ 直接请求成功获取数据")
                return True
            
            print("❌ 所有方法都未能获取数据")
            return False
            
        except Exception as e:
            print(f"模拟过程异常: {e}")
            return False


def main():
    scraper = BrowserSimWaterScraper()
    
    try:
        if scraper.run_simulation():
            print("\n🎉 浏览器模拟成功获取数据！")
        else:
            print("\n❌ 浏览器模拟未能获取数据")
            
    except KeyboardInterrupt:
        print("用户中断")
    except Exception as e:
        print(f"程序异常: {e}")


if __name__ == "__main__":
    main()