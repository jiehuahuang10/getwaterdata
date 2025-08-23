#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
水务数据获取脚本 - 调试版本
详细分析API响应
"""

import requests
import re
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin
from datetime import datetime, timedelta


class DebugWaterDataScraper:
    def __init__(self):
        """初始化HTTP爬虫"""
        self.session = requests.Session()
        
        # 系统登录信息
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 真实的API端点
        self.api_url = f"{self.base_url}/reports/ashx/getRptWaterYield.ashx"
        
        # 设置请求头
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
            '1261181000263',    
            '1262330402331',    
            '2520005',
            '2520006',
            '1261181000300'     
        ]
        
        # 禁用SSL验证警告
        requests.packages.urllib3.disable_warnings()
    
    def login(self):
        """执行登录"""
        print("开始登录系统...")
        
        try:
            response = self.session.get(self.login_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            
            if not form:
                return False
            
            form_data = {}
            inputs = form.find_all('input')
            for input_elem in inputs:
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
            
            # 找到用户名和密码字段
            for input_elem in inputs:
                name = input_elem.get('name', '')
                input_type = input_elem.get('type', 'text')
                
                if 'user' in name.lower():
                    form_data[name] = self.username
                elif input_type == 'password':
                    form_data[name] = self.password
            
            login_response = self.session.post(self.login_url, data=form_data, timeout=15, allow_redirects=True)
            
            if "Login.aspx" not in login_response.url or "ThinkWater" in login_response.text:
                print("✅ 登录成功！")
                return True
            else:
                print("❌ 登录失败")
                return False
                
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def setup_session(self):
        """设置会话状态"""
        print("正在设置会话状态...")
        
        try:
            report_page_url = f"{self.base_url}/reports/FluxRpt.aspx"
            response = self.session.get(report_page_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 成功访问报表页面")
                return True
            else:
                print(f"❌ 访问报表页面失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"设置会话状态失败: {e}")
            return False
    
    def try_different_parameter_combinations(self):
        """尝试不同的参数组合"""
        print("正在尝试不同的参数组合...")
        
        # 不同的日期格式
        date_formats = [
            ('2025-07-24', '2025-07-31'),
            ('2025/07/24', '2025/07/31'),
            ('20250724', '20250731'),
            ('2024-07-24', '2024-07-31'),  # 历史数据
            ('2024/07/24', '2024/07/31'),
        ]
        
        # 不同的参数组合
        parameter_sets = [
            # 组合1：基础参数
            {
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'dayRpt'
            },
            # 组合2：简化参数
            {
                'meterType': '',
                'type': 'dayRpt'
            },
            # 组合3：不同的type值
            {
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'daily'
            },
            # 组合4：包含分页参数
            {
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'dayRpt',
                'page': '1',
                'rows': '100'
            },
            # 组合5：尝试实时数据
            {
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'realtime'
            }
        ]
        
        formatted_node_ids = "'" + "','".join(self.target_meters) + "'"
        
        for date_start, date_end in date_formats:
            for param_set in parameter_sets:
                print(f"\n🔄 测试组合 - 日期: {date_start}~{date_end}, 参数: {param_set}")
                
                api_params = {
                    'nodeId': formatted_node_ids,
                    'startDate': date_start,
                    'endDate': date_end,
                    **param_set
                }
                
                if self.test_api_call(api_params):
                    return True
        
        return False
    
    def test_single_meter(self):
        """测试单个水表"""
        print("正在测试单个水表...")
        
        for meter_id in self.target_meters:
            print(f"\n🔄 测试单个水表: '{meter_id}'")
            
            api_params = {
                'nodeId': f"'{meter_id}'",
                'startDate': '2024-07-24',
                'endDate': '2024-07-31',
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'dayRpt'
            }
            
            if self.test_api_call(api_params):
                return True
        
        return False
    
    def test_api_call(self, params):
        """测试API调用"""
        try:
            print(f"  参数: {params}")
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'Referer': f'{self.base_url}/reports/FluxRpt.aspx',
                'Origin': self.base_url,
                'Host': 'axwater.dmas.cn'
            }
            
            response = self.session.post(self.api_url, data=params, headers=headers, timeout=15)
            
            print(f"  状态码: {response.status_code}")
            print(f"  响应长度: {len(response.text)} 字符")
            print(f"  响应头: {dict(response.headers)}")
            
            content = response.text.strip()
            
            if content:
                print(f"  响应内容预览: {content[:200]}...")
                
                # 尝试解析JSON
                try:
                    data = response.json()
                    print("  ✅ JSON数据:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                    return True
                except:
                    pass
                
                # 检查HTML
                if '<table' in content or 'error' in content.lower():
                    print(f"  📄 HTML/错误内容: {content}")
                    
                return len(content) > 10  # 如果有实质内容就认为成功
            else:
                print("  ❌ 响应为空")
                return False
                
        except Exception as e:
            print(f"  ❌ API调用失败: {e}")
            return False
    
    def debug_session_info(self):
        """调试会话信息"""
        print("\n🔍 会话调试信息:")
        print(f"Cookies: {len(self.session.cookies)} 个")
        for cookie in self.session.cookies:
            print(f"  {cookie.name}={cookie.value[:50]}...")
        
        print(f"Headers: {dict(self.session.headers)}")
    
    def run_debug(self):
        """运行调试流程"""
        print("\n" + "="*60)
        print("🔍 开始调试版水务数据获取流程")
        print("="*60)
        
        try:
            # 1. 登录
            if not self.login():
                print("❌ 登录失败，终止流程")
                return False
            
            # 2. 设置会话状态
            if not self.setup_session():
                print("❌ 设置会话状态失败，终止流程")
                return False
            
            # 3. 调试会话信息
            self.debug_session_info()
            
            # 4. 尝试不同参数组合
            if self.try_different_parameter_combinations():
                print("\n🎉 找到有效的参数组合！")
                return True
            
            # 5. 测试单个水表
            if self.test_single_meter():
                print("\n🎉 单个水表测试成功！")
                return True
            
            print("\n❌ 所有调试尝试都失败了")
            return False
            
        except Exception as e:
            print(f"❌ 调试流程中发生错误: {e}")
            return False


def main():
    """主函数"""
    scraper = DebugWaterDataScraper()
    
    try:
        if scraper.run_debug():
            print("\n✅ 调试成功找到解决方案！")
        else:
            print("\n❌ 调试未找到解决方案")
            
    except KeyboardInterrupt:
        print("用户中断程序")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()