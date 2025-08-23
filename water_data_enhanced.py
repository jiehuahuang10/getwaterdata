#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
水务数据获取脚本 - 增强版本
优化功能：
- 命令行参数支持
- 环境变量配置
- 请求重试机制
- 自动重登录
- 数据保存为JSON/CSV
- 更好的错误处理和日志
"""

import requests
import re
import argparse
import os
import sys
import json
import csv
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 是可选的


class EnhancedWaterDataScraper:
    def __init__(self, username: str = None, password: str = None, base_url: str = None):
        """初始化增强版HTTP爬虫"""
        self.session = requests.Session()
        
        # 系统登录信息（优先级：参数 > 环境变量 > 默认值）
        self.base_url = base_url or os.getenv('WATER_BASE_URL', "http://axwater.dmas.cn")
        self.login_url = f"{self.base_url}/Login.aspx"
        self.username = username or os.getenv('WATER_USERNAME', "13509288500")
        self.password = password or os.getenv('WATER_PASSWORD', "288500")
        
        # 真实的API端点
        self.api_url = f"{self.base_url}/reports/ashx/getRptWaterYield.ashx"
        
        # 配置日志
        self.setup_logging()
        
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
        
        # 默认水表ID列表
        self.default_meters = [
            '2501200108',
            '1261181000263',
            '1262330402331', 
            '2520005',
            '2520006',
            '1261181000300'
        ]
        
        # 会话状态
        self.viewstate = ""
        self.eventvalidation = ""
        self.is_logged_in = False
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 2
        
        # 禁用SSL验证警告
        requests.packages.urllib3.disable_warnings()
    
    def setup_logging(self):
        """设置日志配置"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('water_data.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def retry_on_failure(self, func, *args, **kwargs):
        """重试机制装饰器"""
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                self.logger.warning(f"尝试 {attempt + 1}/{self.max_retries} 失败: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"所有重试都失败了")
                    raise
        return False
    
    def login(self) -> bool:
        """执行登录"""
        self.logger.info("开始登录系统...")
        
        try:
            # 获取登录页面
            response = self.session.get(self.login_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            
            if not form:
                self.logger.error("未找到登录表单")
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
                
                self.logger.info("正在发送登录请求...")
                login_response = self.session.post(
                    self.login_url,
                    data=form_data,
                    timeout=15,
                    allow_redirects=True
                )
                
                # 检查登录是否成功
                if "Login.aspx" not in login_response.url or "ThinkWater" in login_response.text:
                    self.logger.info("登录成功！")
                    self.is_logged_in = True
                    
                    # 保存重要的Cookie信息
                    cookies_count = len(self.session.cookies)
                    self.logger.info(f"保存了 {cookies_count} 个Cookie")
                    
                    return True
                else:
                    self.logger.error("登录失败")
                    return False
            else:
                self.logger.error("未找到用户名或密码字段")
                return False
                
        except Exception as e:
            self.logger.error(f"登录过程中发生错误: {e}")
            return False
    
    def setup_session_state(self) -> bool:
        """设置正确的会话状态"""
        self.logger.info("正在设置会话状态...")
        
        try:
            # 访问报表页面建立会话状态
            report_page_url = f"{self.base_url}/reports/FluxRpt.aspx"
            self.logger.info(f"访问报表页面: {report_page_url}")
            
            response = self.session.get(report_page_url, timeout=10)
            if response.status_code == 200:
                self.logger.info("成功访问报表页面")
                
                # 解析页面获取必要的状态信息
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 获取ViewState等ASP.NET状态
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                if viewstate and eventvalidation:
                    self.viewstate = viewstate.get('value', '')
                    self.eventvalidation = eventvalidation.get('value', '')
                    self.logger.info("获取到ASP.NET状态信息")
                else:
                    self.logger.warning("未找到ASP.NET状态信息")
                
                return True
            else:
                self.logger.error(f"访问报表页面失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"设置会话状态失败: {e}")
            return False
    
    def get_water_data_with_params(self, meter_ids: List[str], start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """使用指定参数获取水表数据"""
        self.logger.info(f"正在获取水表数据: {len(meter_ids)}个水表，时间范围 {start_date} 到 {end_date}")
        
        # 每次请求前都重新登录和设置会话状态（解决会话超时问题）
        self.logger.info("重新建立会话以确保数据获取成功...")
        if not self.login():
            self.logger.error("重新登录失败")
            return None
        
        if not self.setup_session_state():
            self.logger.error("重新设置会话状态失败")
            return None
        
        try:
            # 构造API请求参数
            formatted_node_ids = "'" + "','".join(meter_ids) + "'"
            api_params = {
                'nodeId': formatted_node_ids,
                'startDate': start_date,
                'endDate': end_date,
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'dayRpt'
            }
            
            self.logger.info("API请求参数:")
            for key, value in api_params.items():
                if key == 'nodeId':
                    self.logger.info(f"  {key}: {value[:50]}...")  # 截断长ID列表
                else:
                    self.logger.info(f"  {key}: {value}")
            
            # 更新请求头，添加更多必要的头信息
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # 添加ASP.NET状态参数到请求数据中
            if hasattr(self, 'viewstate') and self.viewstate:
                api_params['__VIEWSTATE'] = self.viewstate
            if hasattr(self, 'eventvalidation') and self.eventvalidation:
                api_params['__EVENTVALIDATION'] = self.eventvalidation
            
            # 发送API请求
            response = self.session.post(
                self.api_url,
                data=api_params,
                headers=headers,
                timeout=15
            )
            
            self.logger.info(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                return self.parse_api_response(response)
            else:
                self.logger.error(f"API请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"API请求过程中发生错误: {e}")
            return None
    
    def parse_api_response(self, response) -> Optional[Dict[str, Any]]:
        """解析API响应数据"""
        try:
            content = response.text.strip()
            self.logger.info(f"响应数据长度: {len(content)} 字符")
            
            # 检查是否为空响应
            if not content:
                self.logger.warning("响应内容为空")
                return None
            
            # 检查是否为登录超时
            if '登录超时' in content or 'Login.aspx' in content:
                self.logger.warning("检测到登录超时，标记需要重新登录")
                self.is_logged_in = False
                return None
            
            # 尝试解析JSON
            try:
                data = response.json()
                self.logger.info("成功解析JSON数据")
                self.display_water_data_summary(data)  # 显示数据摘要
                return {
                    'success': True,
                    'data_type': 'json',
                    'data': data,
                    'raw_content': content
                }
            except json.JSONDecodeError:
                pass
            
            # 检查HTML表格
            if '<table' in content or '<tr' in content:
                soup = BeautifulSoup(content, 'html.parser')
                tables = soup.find_all('table')
                
                if tables:
                    self.logger.info("发现HTML表格数据")
                    table_data = self.extract_table_data(tables)
                    self.display_table_summary(table_data)  # 显示表格摘要
                    return {
                        'success': True,
                        'data_type': 'html_table',
                        'data': table_data,
                        'raw_content': content
                    }
            
            # 如果内容包含水表相关字段，认为是有效数据
            if any(keyword in content.lower() for keyword in 
                   ['水表', 'meter', 'flux', '流量', '用水量', '抄表', '数据']):
                self.logger.info("检测到水表相关数据")
                self.logger.info(f"文本数据预览: {content[:200]}...")
                return {
                    'success': True,
                    'data_type': 'text',
                    'data': content,
                    'raw_content': content
                }
            
            self.logger.warning("未识别的响应格式")
            self.logger.debug(f"响应内容预览: {content[:200]}...")
            return {
                'success': False,
                'data_type': 'unknown',
                'data': None,
                'raw_content': content
            }
            
        except Exception as e:
            self.logger.error(f"解析API响应失败: {e}")
            return None
    
    def extract_table_data(self, tables) -> List[List[str]]:
        """提取HTML表格数据"""
        try:
            all_table_data = []
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                table_data = []
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        if any(row_data):  # 只保存非空行
                            table_data.append(row_data)
                
                if table_data:
                    all_table_data.extend(table_data)
            
            return all_table_data
            
        except Exception as e:
            self.logger.error(f"提取表格数据失败: {e}")
            return []
    
    def display_water_data_summary(self, data: Dict[str, Any]) -> None:
        """显示水表数据摘要"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("📊 获取到的水表数据摘要:")
            self.logger.info("=" * 60)
            
            if isinstance(data, dict) and 'rows' in data:
                total = data.get('total', 0)
                rows = data.get('rows', [])
                self.logger.info(f"总记录数: {total}, 实际行数: {len(rows)}")
                
                for i, row in enumerate(rows[:10]):  # 只显示前10个
                    if isinstance(row, dict):
                        meter_id = row.get('ID', 'N/A')
                        meter_name = row.get('Name', 'N/A')
                        max_value = row.get('maxvalue', 'N/A')
                        min_value = row.get('minvalue', 'N/A')
                        avg_value = row.get('avg', 'N/A')
                        
                        self.logger.info(f"水表 {i+1}: {meter_name} ({meter_id})")
                        if max_value != 'N/A' and max_value is not None:
                            self.logger.info(f"  最大值: {max_value}, 最小值: {min_value}, 平均值: {avg_value}")
                        
                        # 显示每日数据
                        daily_data = []
                        for key, value in row.items():
                            if key.startswith('202') and value is not None:
                                daily_data.append((key, value))
                        
                        if daily_data:
                            daily_data.sort()
                            daily_str = ", ".join([f"{date}: {val}" for date, val in daily_data[:5]])
                            if len(daily_data) > 5:
                                daily_str += f"... (共{len(daily_data)}天)"
                            self.logger.info(f"  每日数据: {daily_str}")
                
                if len(rows) > 10:
                    self.logger.info(f"... 还有 {len(rows) - 10} 个水表")
            
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"显示数据摘要失败: {e}")
    
    def display_table_summary(self, table_data: List[List[str]]) -> None:
        """显示表格数据摘要"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("📋 获取到的表格数据摘要:")
            self.logger.info("=" * 60)
            
            if table_data:
                self.logger.info(f"表格行数: {len(table_data)}")
                
                # 显示表头
                if len(table_data) > 0:
                    headers = table_data[0]
                    self.logger.info(f"表头: {' | '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
                
                # 显示前几行数据
                for i, row in enumerate(table_data[1:6]):  # 显示前5行数据
                    if row:
                        row_str = " | ".join([str(cell)[:20] for cell in row[:5]])
                        if len(row) > 5:
                            row_str += "..."
                        self.logger.info(f"第{i+1}行: {row_str}")
                
                if len(table_data) > 6:
                    self.logger.info(f"... 还有 {len(table_data) - 6} 行数据")
            
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"显示表格摘要失败: {e}")
    
    def save_data_to_json(self, data: Dict[str, Any], filename: str) -> bool:
        """保存数据为JSON格式"""
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加元数据
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'source': 'enhanced_water_data_scraper',
                'success': data.get('success', False),
                'data_type': data.get('data_type', 'unknown'),
                'data': data.get('data'),
                'raw_content_length': len(data.get('raw_content', ''))
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据已保存到JSON文件: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存JSON文件失败: {e}")
            return False
    
    def save_data_to_csv(self, data: Dict[str, Any], filename: str) -> bool:
        """保存数据为CSV格式"""
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 根据数据类型处理
            if data.get('data_type') == 'json' and isinstance(data.get('data'), dict):
                json_data = data['data']
                if 'rows' in json_data and isinstance(json_data['rows'], list):
                    rows = json_data['rows']
                    if rows and isinstance(rows[0], dict):
                        # JSON表格数据
                        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows)
                        
                        self.logger.info(f"JSON数据已保存到CSV文件: {filename}")
                        return True
            
            elif data.get('data_type') == 'html_table' and isinstance(data.get('data'), list):
                table_data = data['data']
                if table_data:
                    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerows(table_data)
                    
                    self.logger.info(f"表格数据已保存到CSV文件: {filename}")
                    return True
            
            # 如果无法转换为CSV，保存为文本
            text_filename = str(output_path).replace('.csv', '.txt')
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(f"数据类型: {data.get('data_type', 'unknown')}\n")
                f.write(f"获取时间: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n")
                f.write(str(data.get('data', '')))
            
            self.logger.info(f"数据已保存为文本文件: {text_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存CSV文件失败: {e}")
            return False
    
    def try_multiple_date_ranges(self, meter_ids: List[str]) -> Optional[Dict[str, Any]]:
        """尝试多个日期范围获取数据"""
        # 定义多个可能有数据的日期范围，优先使用最近7天
        today = datetime.now()
        date_ranges = [
            # 最近7天（优先）
            ((today - timedelta(days=7)).strftime('%Y-%m-%d'), 
             today.strftime('%Y-%m-%d')),
            # 最近8-14天
            ((today - timedelta(days=14)).strftime('%Y-%m-%d'), 
             (today - timedelta(days=7)).strftime('%Y-%m-%d')),
            # 最近15-21天
            ((today - timedelta(days=21)).strftime('%Y-%m-%d'), 
             (today - timedelta(days=14)).strftime('%Y-%m-%d')),
            # 上个月同期
            ((today - timedelta(days=37)).strftime('%Y-%m-%d'), 
             (today - timedelta(days=30)).strftime('%Y-%m-%d')),
            # 已知有数据的日期范围
            ('2025-07-26', '2025-08-01'),
            ('2025-07-25', '2025-08-01'),
            ('2024-07-24', '2024-07-31'),
            ('2024-12-01', '2024-12-07'),
        ]
        
        for start_date, end_date in date_ranges:
            self.logger.info(f"尝试日期范围: {start_date} 到 {end_date}")
            
            result = self.get_water_data_with_params(meter_ids, start_date, end_date)
            if result and result.get('success'):
                self.logger.info(f"成功获取数据，日期范围: {start_date} 到 {end_date}")
                result['date_range'] = {'start': start_date, 'end': end_date}
                return result
            
            # 短暂延迟避免请求过频
            time.sleep(1)
        
        self.logger.warning("所有日期范围都未能获取到数据")
        return None
    
    def run(self, meter_ids: List[str] = None, start_date: str = None, end_date: str = None, 
            output_json: str = None, output_csv: str = None) -> bool:
        """运行完整的数据获取流程"""
        self.logger.info("开始增强版水务数据获取流程")
        
        try:
            # 1. 登录
            if not self.retry_on_failure(self.login):
                self.logger.error("登录失败，终止流程")
                return False
            
            # 2. 设置会话状态
            if not self.setup_session_state():
                self.logger.error("设置会话状态失败，终止流程")
                return False
            
            # 3. 获取数据
            if meter_ids is None:
                meter_ids = self.default_meters
            
            if start_date and end_date:
                # 使用指定日期范围
                result = self.get_water_data_with_params(meter_ids, start_date, end_date)
                if result:
                    result['date_range'] = {'start': start_date, 'end': end_date}
            else:
                # 尝试多个日期范围
                result = self.try_multiple_date_ranges(meter_ids)
            
            if not result or not result.get('success'):
                self.logger.error("无法获取到有效数据")
                return False
            
            # 4. 保存数据
            success_count = 0
            
            if output_json:
                if self.save_data_to_json(result, output_json):
                    success_count += 1
            
            if output_csv:
                if self.save_data_to_csv(result, output_csv):
                    success_count += 1
            
            # 如果没有指定输出文件，使用默认文件名
            if not output_json and not output_csv:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                default_json = f"water_data_{timestamp}.json"
                default_csv = f"water_data_{timestamp}.csv"
                
                self.save_data_to_json(result, default_json)
                self.save_data_to_csv(result, default_csv)
                success_count += 2
            
            self.logger.info(f"数据获取流程完成！成功保存 {success_count} 个文件")
            return True
            
        except Exception as e:
            self.logger.error(f"数据获取流程中发生错误: {e}")
            return False


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='增强版水务数据获取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 使用默认参数获取数据
  python water_data_enhanced.py
  
  # 指定水表ID和日期范围
  python water_data_enhanced.py -m 2501200108,2520005 -s 2024-07-24 -e 2024-07-31
  
  # 指定输出文件
  python water_data_enhanced.py --json output.json --csv output.csv
  
  # 使用环境变量配置登录信息
  export WATER_USERNAME=your_username
  export WATER_PASSWORD=your_password
  python water_data_enhanced.py
        '''
    )
    
    parser.add_argument('-u', '--username', 
                       help='登录用户名 (也可通过环境变量 WATER_USERNAME 设置)')
    parser.add_argument('-p', '--password', 
                       help='登录密码 (也可通过环境变量 WATER_PASSWORD 设置)')
    parser.add_argument('--base-url', 
                       help='系统基础URL (默认: http://axwater.dmas.cn)')
    
    parser.add_argument('-m', '--meters', 
                       help='水表ID列表，用逗号分隔 (例如: 2501200108,2520005)')
    parser.add_argument('-s', '--start-date', 
                       help='开始日期 (格式: YYYY-MM-DD)')
    parser.add_argument('-e', '--end-date', 
                       help='结束日期 (格式: YYYY-MM-DD)')
    
    parser.add_argument('--json', 
                       help='JSON输出文件路径')
    parser.add_argument('--csv', 
                       help='CSV输出文件路径')
    
    parser.add_argument('--log-level', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='日志级别 (默认: INFO)')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    if args.log_level:
        os.environ['LOG_LEVEL'] = args.log_level
    
    # 创建爬虫实例
    scraper = EnhancedWaterDataScraper(
        username=args.username,
        password=args.password,
        base_url=args.base_url
    )
    
    # 解析水表ID列表
    meter_ids = None
    if args.meters:
        meter_ids = [mid.strip() for mid in args.meters.split(',')]
    
    try:
        # 运行数据获取流程
        success = scraper.run(
            meter_ids=meter_ids,
            start_date=args.start_date,
            end_date=args.end_date,
            output_json=args.json,
            output_csv=args.csv
        )
        
        if success:
            print("\n✅ 增强版数据获取成功！")
            sys.exit(0)
        else:
            print("\n❌ 增强版数据获取失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
        sys.exit(130)
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
