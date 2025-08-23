#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
水务数据获取脚本 - 成功版本
基于验证有效的表单提交方式
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime


class SuccessWaterScraper:
    def __init__(self):
        """初始化"""
        self.session = requests.Session()
        
        # 系统信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 设置浏览器请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 目标水表ID
        self.target_meters = [
            '2501200108',
            '1261181000263',    
            '1262330402331',    
            '2520005',
            '2520006',
            '1261181000300'     
        ]
        
        # 存储表单状态
        self.viewstate = ""
        self.eventvalidation = ""
        
        requests.packages.urllib3.disable_warnings()
    
    def login(self):
        """登录系统"""
        print("🔐 开始登录...")
        
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
            
            # 发送登录请求
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
            print(f"❌ 登录异常: {e}")
            return False
    
    def get_report_page_state(self):
        """获取报表页面状态"""
        print("📄 获取报表页面状态...")
        
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
            print(f"❌ 获取页面状态异常: {e}")
            return False
    
    def get_water_data(self, meter_id, start_date='2024-07-24', end_date='2024-07-31'):
        """获取指定水表的数据"""
        print(f"📊 获取水表 {meter_id} 的数据...")
        
        try:
            report_url = f"{self.base_url}/reports/FluxRpt.aspx"
            
            # 构造表单数据
            form_data = {
                '__VIEWSTATE': self.viewstate,
                '__EVENTVALIDATION': self.eventvalidation,
                'hiddenType': 'meterUseFluxRpt',
                'rptType': '1',              # 日报表
                'startDate': start_date,     # 开始日期
                'endDate': end_date,         # 结束日期
                'user': meter_id,            # 水表ID
                'meterType': '',             # 计量类型
                'statisticsType': 'flux'     # 统计类型
            }
            
            print(f"  查询日期范围: {start_date} ~ {end_date}")
            
            # 提交表单
            response = self.session.post(
                report_url,
                data=form_data,
                timeout=15,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': report_url
                }
            )
            
            if response.status_code == 200:
                # 保存响应到文件
                filename = f"water_data_{meter_id}_{start_date}_{end_date}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  ✅ 响应已保存到: {filename}")
                
                # 解析数据
                return self.parse_water_data(response.text, meter_id)
            else:
                print(f"  ❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 获取数据异常: {e}")
            return False
    
    def parse_water_data(self, html_content, meter_id):
        """解析水表数据"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tables = soup.find_all('table')
            
            print(f"  📋 发现 {len(tables)} 个表格")
            
            data_found = False
            
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                if len(rows) > 1:  # 有数据的表格
                    print(f"\n  📊 表格 {i+1} - 水表 {meter_id} 数据:")
                    print("  " + "="*76)
                    
                    valid_rows = []
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            if any(row_data):  # 非空行
                                valid_rows.append(row_data)
                    
                    if valid_rows:
                        # 显示表头
                        if valid_rows:
                            print("  表头:", " | ".join(valid_rows[0]))
                            print("  " + "-" * 76)
                            
                            # 显示所有数据行
                            for k, row_data in enumerate(valid_rows[1:], 1):
                                print(f"  第{k}行:", " | ".join(row_data))
                            
                            data_found = True
                    
                    print("  " + "="*76)
            
            if not data_found:
                print("  ⚠️  未找到有效的数据表格")
                # 检查是否有错误信息
                if '无数据' in html_content or '没有数据' in html_content:
                    print("  ℹ️  系统提示：该时间范围内无数据")
                elif '权限' in html_content:
                    print("  ⚠️  可能存在权限问题")
            
            return data_found
            
        except Exception as e:
            print(f"  ❌ 解析数据异常: {e}")
            return False
    
    def get_all_water_data(self):
        """获取所有水表数据"""
        print("\n" + "="*60)
        print("🚀 开始获取所有水表数据")
        print("="*60)
        
        success_count = 0
        
        try:
            # 1. 登录
            if not self.login():
                return False
            
            # 2. 获取页面状态
            if not self.get_report_page_state():
                return False
            
            # 3. 获取每个水表的数据
            print(f"\n📋 计划获取 {len(self.target_meters)} 个水表的数据")
            
            for i, meter_id in enumerate(self.target_meters, 1):
                print(f"\n[{i}/{len(self.target_meters)}] 处理水表: {meter_id}")
                
                if self.get_water_data(meter_id):
                    success_count += 1
                    print(f"  ✅ 成功获取数据")
                else:
                    print(f"  ❌ 获取数据失败")
                
                # 避免请求过于频繁
                time.sleep(1)
            
            print(f"\n📊 处理完成:")
            print(f"  总计: {len(self.target_meters)} 个水表")
            print(f"  成功: {success_count} 个")
            print(f"  失败: {len(self.target_meters) - success_count} 个")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 获取数据流程异常: {e}")
            return False
    
    def test_single_meter(self, meter_id='2501200108'):
        """测试单个水表"""
        print(f"\n🧪 测试单个水表: {meter_id}")
        
        try:
            if not self.login():
                return False
            
            if not self.get_report_page_state():
                return False
            
            return self.get_water_data(meter_id)
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False


def main():
    """主函数"""
    scraper = SuccessWaterScraper()
    
    print("🌊 水务数据获取系统 - 成功版本")
    print("基于验证有效的表单提交方式")
    
    try:
        # 选择运行模式
        mode = input("\n请选择运行模式:\n1. 测试单个水表\n2. 获取所有水表数据\n请输入选择 (1-2): ").strip()
        
        if mode == '1':
            # 测试模式
            test_meter = input("请输入要测试的水表ID (默认: 2501200108): ").strip()
            if not test_meter:
                test_meter = '2501200108'
            
            if scraper.test_single_meter(test_meter):
                print(f"\n✅ 水表 {test_meter} 测试成功！")
            else:
                print(f"\n❌ 水表 {test_meter} 测试失败")
        
        elif mode == '2':
            # 完整获取模式
            if scraper.get_all_water_data():
                print("\n🎉 水表数据获取任务完成！")
                print("📁 数据文件已保存到当前目录")
            else:
                print("\n❌ 水表数据获取失败")
        
        else:
            print("❌ 无效的选择")
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")


if __name__ == "__main__":
    main()