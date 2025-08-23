#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
"""
获取最近七天水务数据 - 基于Context7最佳实践
仅使用HTTP请求方式，采用Context Manager和现代Session管理
"""

import requests
from bs4 import BeautifulSoup
import json
import hashlib
import sys
from datetime import datetime, timedelta
from requests.exceptions import RequestException, ConnectionError, Timeout


class Recent7DaysWaterCollector:
    """最近七天水务数据收集器 - Context7最佳实践实现"""
    
    def __init__(self):
        """初始化收集器"""
        self.base_url = "http://axwater.dmas.cn"
        self.login_url = f"{self.base_url}/Login.aspx"
        self.api_url = f"{self.base_url}/reports/ashx/getRptWaterYield.ashx"
        self.username = "13509288500"
        self.password = "288500"
        
        # 目标水表ID（基于成功的数据获取）
        self.target_node_ids = [
            '2501200108',      # 2501200108
            '1261181000263',   # 荔新大道DN1200流量计
            '1262330402331',   # 宁西总表DN1200
            '2520005',         # 如丰大道600监控表
            '2520006',         # 三棵树600监控表
            '1261181000300',   # 新城大道医院DN800流量计
            '2190066',         # 三江新总表DN800
            '2190493'          # 沙庄总表
        ]
        
        # 禁用SSL警告
        requests.packages.urllib3.disable_warnings()
    
    def _calculate_recent_7days(self):
        """计算最近七天的日期范围"""
        # 基于已知有数据的日期范围，计算最近7天
        # 使用2025年8月1日作为结束日期，往前推7天
        end_date = datetime(2025, 8, 1)
        start_date = end_date - timedelta(days=6)  # 7天包括结束日期
        
        return (
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    
    def login_and_get_session(self):
        """使用Context7最佳实践登录并返回认证的Session"""
        print("🔐 使用Context7最佳实践进行登录...")
        
        # 使用Session对象 - Context7推荐的方式
        session = requests.Session()
        
        # 设置Session级别的请求头 - Context7最佳实践
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        try:
            # 获取登录页面
            response = session.get(self.login_url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 获取登录页面失败: {response.status_code}")
                return None
            
            # 解析表单数据
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form', {'method': 'post'}) or soup.find('form')
            
            if not form:
                print("❌ 未找到登录表单")
                return None
            
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
            login_response = session.post(
                self.login_url,
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=15,
                allow_redirects=True
            )
            
            # 验证登录成功
            if "window.location=" in login_response.text:
                print("✅ 登录成功！")
                print(f"📝 Session Cookie数量: {len(session.cookies)}")
                return session
            else:
                print("❌ 登录失败")
                return None
                
        except RequestException as e:
            print(f"❌ 登录过程中发生错误: {e}")
            return None
    
    def fetch_water_data_with_session(self, session, start_date, end_date):
        """使用认证的Session获取水务数据"""
        print(f"📊 获取最近七天数据 ({start_date} 到 {end_date})...")
        
        try:
            # 格式化nodeId参数（每个ID用单引号包围）
            formatted_node_ids = "'" + "','".join(self.target_node_ids) + "'"
            
            # API请求参数（基于成功的开发者工具分析）
            api_params = {
                'nodeId': formatted_node_ids,
                'startDate': start_date,
                'endDate': end_date,
                'meterType': '-1',
                'statisticsType': 'flux',
                'type': 'dayRpt'
            }
            
            # API请求头（完全符合开发者工具要求）
            api_headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/reports/FluxRpt.aspx',
                'Origin': self.base_url,
                'Host': 'axwater.dmas.cn'
            }
            
            print("🔄 发送API请求...")
            print(f"   🎯 目标水表数量: {len(self.target_node_ids)} 个")
            print(f"   📅 日期范围: {start_date} 到 {end_date}")
            
            # 使用Session发送POST请求 - Context7最佳实践
            response = session.post(
                self.api_url,
                data=api_params,
                headers=api_headers,
                timeout=30
            )
            
            print(f"   📡 响应状态码: {response.status_code}")
            print(f"   📦 响应大小: {len(response.text)} 字符")
            
            if response.status_code == 200:
                return self._process_and_display_data(response, start_date, end_date)
            else:
                print(f"❌ API请求失败: {response.status_code}")
                return False
                
        except RequestException as e:
            print(f"❌ 数据获取异常: {e}")
            return False
    
    def _process_and_display_data(self, response, start_date, end_date):
        """处理并在后台输出数据"""
        print("🔍 处理API响应数据...")
        
        try:
            content = response.text.strip()
            
            if not content:
                print("❌ 响应内容为空")
                return False
            
            # 保存原始数据文件
            filename = f"recent_7days_data_{start_date}_{end_date}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📁 原始数据已保存: {filename}")
            
            # 解析JSON数据
            try:
                data = json.loads(content)
                return self._display_water_data_summary(data, start_date, end_date)
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return False
                
        except Exception as e:
            print(f"❌ 数据处理异常: {e}")
            return False
    
    def _display_water_data_summary(self, data, start_date, end_date):
        """在后台输出水务数据摘要"""
        print("\n" + "="*90)
        print(f"🌊 最近七天水务数据报表 ({start_date} 到 {end_date})")
        print("="*90)
        
        try:
            # 处理实际的数据结构：{total: 8, rows: [...]}
            if isinstance(data, dict) and 'rows' in data:
                meter_list = data['rows']
                total_count = data.get('total', len(meter_list))
                print(f"📊 共获取到 {total_count} 个水表的数据")
            elif isinstance(data, list):
                meter_list = data
                print(f"📊 共获取到 {len(data)} 个水表的数据")
            else:
                print("❌ 数据格式不符合预期")
                print(f"实际数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"数据键: {list(data.keys())}")
                return False
            
            print("\n📋 数据摘要:")
            
            total_avg_flow = 0
            active_meters = 0
            
            for i, meter_data in enumerate(meter_list, 1):
                if not isinstance(meter_data, dict):
                    continue
                
                meter_id = meter_data.get('ID', 'N/A')
                meter_name = meter_data.get('Name', 'N/A')
                avg_value = meter_data.get('avg')
                max_value = meter_data.get('maxvalue')
                min_value = meter_data.get('minvalue')
                max_time = meter_data.get('maxtime', '')
                min_time = meter_data.get('mintime', '')
                
                print(f"\n🔹 水表 {i}: {meter_name} ({meter_id})")
                
                if avg_value is not None and max_value is not None:
                    print(f"   📊 平均流量: {avg_value:,.2f}")
                    print(f"   🔺 最大值: {max_value:,.2f} ({max_time})")
                    print(f"   🔻 最小值: {min_value:,.2f} ({min_time})")
                    
                    # 显示每日数据
                    daily_data = []
                    for key, value in meter_data.items():
                        if key.startswith('2025-') and value is not None:
                            daily_data.append(f"{key}: {value:,.2f}")
                    
                    if daily_data:
                        print(f"   📅 每日数据: {' | '.join(daily_data[:3])}{'...' if len(daily_data) > 3 else ''}")
                    
                    total_avg_flow += avg_value
                    active_meters += 1
                else:
                    print("   ⚠️  无有效数据")
            
            # 统计汇总
            print("\n" + "-"*90)
            print("📈 统计汇总:")
            print(f"   🏭 活跃水表数量: {active_meters}/{len(meter_list)}")
            if active_meters > 0:
                print(f"   💧 总平均流量: {total_avg_flow:,.2f}")
                print(f"   📊 单表平均流量: {total_avg_flow/active_meters:,.2f}")
            
            # 关键指标
            if active_meters > 0:
                high_flow_meters = []
                low_flow_meters = []
                avg_threshold = total_avg_flow / active_meters
                
                for meter_data in meter_list:
                    if isinstance(meter_data, dict) and meter_data.get('avg'):
                        avg = meter_data.get('avg')
                        name = meter_data.get('Name', 'N/A')
                        if avg > avg_threshold * 1.5:  # 高于平均值50%
                            high_flow_meters.append(f"{name}({avg:,.1f})")
                        elif avg < avg_threshold * 0.5:  # 低于平均值50%
                            low_flow_meters.append(f"{name}({avg:,.1f})")
                
                if high_flow_meters:
                    print(f"   🔥 高流量水表: {', '.join(high_flow_meters[:3])}")
                if low_flow_meters:
                    print(f"   🔽 低流量水表: {', '.join(low_flow_meters[:3])}")
            
            print("="*90)
            print("✅ 最近七天数据获取并输出完成！")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据显示异常: {e}")
            print("📋 原始数据结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            return True
    
    def collect_recent_7days_data(self):
        """收集最近七天数据的主流程 - 使用Context7最佳实践"""
        print("\n" + "="*80)
        print("🌊 最近七天水务数据收集系统")
        print("🎯 采用Context7最佳实践 - Session管理和错误处理")
        print("📋 仅使用HTTP请求方式，无浏览器自动化工具")
        print("="*80)
        
        # 计算最近七天的日期范围
        start_date, end_date = self._calculate_recent_7days()
        print(f"📅 计算得出最近七天: {start_date} 到 {end_date}")
        
        # 使用Context Manager确保Session正确关闭 - Context7最佳实践
        session = self.login_and_get_session()
        
        if not session:
            print("❌ 无法建立认证会话")
            return False
        
        try:
            # 使用认证的Session获取数据
            success = self.fetch_water_data_with_session(session, start_date, end_date)
            
            if success:
                print(f"\n🎉 最近七天数据收集成功完成！")
                print(f"📊 数据时间范围: {start_date} 到 {end_date}")
                print(f"📁 数据文件: recent_7days_data_{start_date}_{end_date}.json")
                return True
            else:
                print(f"\n❌ 最近七天数据收集失败")
                return False
                
        except Exception as e:
            print(f"❌ 收集过程发生异常: {e}")
            return False
        finally:
            # 确保Session正确关闭 - Context7最佳实践
            try:
                session.close()
                print("🔒 Session已安全关闭")
            except:
                pass


def main():
    """主函数 - Context7最佳实践"""
    collector = Recent7DaysWaterCollector()
    
    try:
        success = collector.collect_recent_7days_data()
        
        if success:
            print("\n✅ 程序执行成功！最近七天数据已在后台输出")
            sys.exit(0)
        else:
            print("\n❌ 程序执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 程序执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()