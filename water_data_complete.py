#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
水务数据获取完整版 - 基于开发者工具分析
仅使用HTTP请求方式，根据浏览器网络请求完全复制API调用
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import sys
import hashlib
from datetime import datetime, timedelta
from requests.exceptions import (
    ConnectionError, HTTPError, Timeout, 
    TooManyRedirects, RequestException, SSLError
)


class WaterDataCompleteCollector:
    """水务数据完整收集器 - 基于开发者工具的精确实现"""
    
    def __init__(self):
        """初始化数据收集器"""
        
        # 系统信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.api_url = f"{self.base_url}/reports/ashx/getRptWaterYield.ashx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 创建Session对象
        self.session = requests.Session()
        
        # 设置基础请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 目标水表ID（来自开发者工具截图）
        self.target_node_ids = [
            '2501200108',
            '1261181000263', 
            '1262330402331',
            '2520005',
            '2520006', 
            '1261181000300',
            '2190066',
            '2190493'
        ]
        
        # 禁用SSL警告
        requests.packages.urllib3.disable_warnings()
    
    def login(self):
        """执行登录（复用之前成功的登录逻辑）"""
        print("🔐 开始登录系统...")
        
        try:
            # 获取登录页面
            response = self.session.get(self.login_url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 获取登录页面失败: {response.status_code}")
                return False
            
            # 解析表单
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            
            if not form:
                print("❌ 未找到登录表单")
                return False
            
            # 提取表单数据
            form_data = {}
            for input_elem in form.find_all('input'):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
            
            # 设置登录凭据（MD5加密密码）
            form_data['user'] = self.username
            form_data['pwd'] = hashlib.md5(self.password.encode('utf-8')).hexdigest()
            
            # 发送登录请求
            login_response = self.session.post(
                self.login_url,
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=15,
                allow_redirects=True
            )
            
            # 验证登录成功（检查JavaScript重定向）
            if "window.location=" in login_response.text:
                print("✅ 登录成功！")
                print(f"📝 获得Cookie数量: {len(self.session.cookies)}")
                return True
            else:
                print("❌ 登录失败")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def get_water_yield_data(self, start_date='2025-07-25', end_date='2025-08-01'):
        """获取水量数据 - 完全按照开发者工具的请求格式"""
        print(f"📊 获取水量数据 ({start_date} 到 {end_date})...")
        
        try:
            # 构造nodeId参数（每个ID用单引号包围，逗号分隔）
            formatted_node_ids = "'" + "','".join(self.target_node_ids) + "'"
            
            # API请求参数（完全按照开发者工具截图）
            api_params = {
                'nodeId': formatted_node_ids,
                'startDate': start_date,
                'endDate': end_date,
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'dayRpt'
            }
            
            # API请求头（完全按照开发者工具截图）
            api_headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/reports/FluxRpt.aspx',
                'Origin': self.base_url,
                'Host': 'axwater.dmas.cn'
            }
            
            print("🔄 发送API请求...")
            print(f"   端点: {self.api_url}")
            print(f"   参数: {api_params}")
            
            # 发送POST请求
            response = self.session.post(
                self.api_url,
                data=api_params,
                headers=api_headers,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应长度: {len(response.text)} 字符")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                return self._process_api_response(response, start_date, end_date)
            else:
                print(f"❌ API请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取数据异常: {e}")
            return False
    
    def _process_api_response(self, response, start_date, end_date):
        """处理API响应数据"""
        print("🔍 处理API响应...")
        
        try:
            content = response.text.strip()
            
            if not content:
                print("❌ 响应内容为空")
                return False
            
            # 保存原始响应
            filename = f"water_data_response_{start_date}_{end_date}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📁 原始响应已保存到: {filename}")
            
            # 尝试解析JSON
            try:
                data = json.loads(content)
                print("✅ 成功解析JSON响应")
                return self._display_json_data(data, start_date, end_date)
            except json.JSONDecodeError:
                print("⚠️  响应不是JSON格式，尝试HTML解析...")
                return self._display_html_data(content, start_date, end_date)
                
        except Exception as e:
            print(f"❌ 处理响应异常: {e}")
            return False
    
    def _display_json_data(self, data, start_date, end_date):
        """显示JSON数据"""
        print("\n" + "="*80)
        print(f"📊 水量数据报表 ({start_date} 到 {end_date})")
        print("="*80)
        
        try:
            # 根据实际的JSON结构显示数据
            if isinstance(data, dict):
                if 'rows' in data:
                    # 如果有rows字段，可能是表格数据
                    rows = data.get('rows', [])
                    print(f"📋 找到 {len(rows)} 条记录")
                    
                    for i, row in enumerate(rows, 1):
                        print(f"\n📌 记录 {i}:")
                        if isinstance(row, dict):
                            for key, value in row.items():
                                print(f"   {key}: {value}")
                        else:
                            print(f"   数据: {row}")
                            
                elif 'data' in data:
                    # 如果有data字段
                    data_content = data.get('data')
                    print(f"📋 数据内容:")
                    print(json.dumps(data_content, indent=2, ensure_ascii=False))
                    
                else:
                    # 显示所有字段
                    print("📋 响应数据结构:")
                    for key, value in data.items():
                        print(f"   {key}: {value}")
                        
            elif isinstance(data, list):
                print(f"📋 找到 {len(data)} 条记录")
                for i, item in enumerate(data, 1):
                    print(f"\n📌 记录 {i}:")
                    print(json.dumps(item, indent=2, ensure_ascii=False))
                    
            else:
                print(f"📋 数据内容: {data}")
                
            print("="*80)
            return True
            
        except Exception as e:
            print(f"❌ 显示JSON数据异常: {e}")
            print("📋 原始数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
    
    def _display_html_data(self, content, start_date, end_date):
        """显示HTML数据"""
        print("\n" + "="*80)
        print(f"📊 水量数据报表 ({start_date} 到 {end_date}) - HTML格式")
        print("="*80)
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            tables = soup.find_all('table')
            
            if tables:
                print(f"📋 找到 {len(tables)} 个数据表格")
                
                for i, table in enumerate(tables, 1):
                    print(f"\n📌 表格 {i}:")
                    rows = table.find_all('tr')
                    
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            cell_data = [cell.get_text(strip=True) for cell in cells]
                            if any(cell_data):  # 只显示非空行
                                if j == 0:
                                    print(f"   表头: {' | '.join(cell_data)}")
                                    print("   " + "-" * len(' | '.join(cell_data)))
                                else:
                                    print(f"   第{j}行: {' | '.join(cell_data)}")
            else:
                print("📋 未找到表格，显示文本内容:")
                text_content = soup.get_text(strip=True)
                if text_content:
                    print(text_content[:1000])  # 显示前1000字符
                else:
                    print("⚠️  无文本内容")
                    
            print("="*80)
            return True
            
        except Exception as e:
            print(f"❌ 解析HTML异常: {e}")
            print("📋 原始内容预览:")
            print(content[:500])
            return True
    
    def collect_data_for_date_range(self, start_date, end_date):
        """收集指定日期范围的数据"""
        print(f"\n🎯 开始收集数据: {start_date} 到 {end_date}")
        
        try:
            success = self.get_water_yield_data(start_date, end_date)
            
            if success:
                print(f"✅ 成功收集 {start_date} 到 {end_date} 的数据")
            else:
                print(f"❌ 收集 {start_date} 到 {end_date} 的数据失败")
                
            return success
            
        except Exception as e:
            print(f"❌ 收集数据异常: {e}")
            return False
    
    def run_complete_collection(self):
        """运行完整的数据收集流程"""
        print("\n" + "="*80)
        print("🌊 水务数据完整收集系统")
        print("📸 基于开发者工具网络请求分析")
        print("🎯 目标: 获取水表用量数据并输出到后台")
        print("="*80)
        
        try:
            # 步骤1: 登录
            if not self.login():
                print("\n❌ 数据收集失败：登录失败")
                return False
            
            print("\n" + "-"*60)
            
            # 步骤2: 收集数据（多个日期范围）
            date_ranges = [
                ('2025-07-25', '2025-08-01'),  # 开发者工具中的日期
                ('2024-07-25', '2024-08-01'),  # 去年同期（可能有历史数据）
                ('2024-12-01', '2024-12-07'),  # 最近的历史数据
            ]
            
            success_count = 0
            
            for start_date, end_date in date_ranges:
                if self.collect_data_for_date_range(start_date, end_date):
                    success_count += 1
                
                # 避免请求过于频繁
                time.sleep(2)
            
            print(f"\n📊 数据收集总结:")
            print(f"   尝试收集: {len(date_ranges)} 个日期范围")
            print(f"   成功收集: {success_count} 个")
            print(f"   成功率: {success_count/len(date_ranges)*100:.1f}%")
            
            if success_count > 0:
                print("\n🎉 数据收集任务完成！")
                print("📁 所有响应数据已保存到本地文件")
                return True
            else:
                print("\n❌ 未能成功收集任何数据")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️  用户中断收集")
            return False
        except Exception as e:
            print(f"\n❌ 收集过程异常: {e}")
            return False
        finally:
            # 确保Session正确关闭
            try:
                self.session.close()
            except:
                pass


def main():
    """主函数"""
    collector = WaterDataCompleteCollector()
    
    try:
        success = collector.run_complete_collection()
        
        if success:
            print("\n✅ 水务数据收集成功完成！")
            sys.exit(0)
        else:
            print("\n❌ 水务数据收集失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()