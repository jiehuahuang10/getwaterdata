#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金山文档水务数据同步模块
将本地水务数据同步到金山文档在线Excel
"""

import os
import json
from datetime import datetime, timedelta
from kdocs_api_client import KDocsAPIClient, extract_file_id_from_url

class WaterDataKDocsSync:
    """水务数据金山文档同步器"""
    
    def __init__(self, file_url, app_id=None, app_secret=None):
        """
        初始化同步器
        
        Args:
            file_url: 金山文档URL
            app_id: 应用ID
            app_secret: 应用密钥
        """
        self.file_url = file_url
        self.file_id = extract_file_id_from_url(file_url)
        
        if not self.file_id:
            raise ValueError(f"无法从URL中提取文件ID: {file_url}")
        
        # 初始化API客户端
        self.client = KDocsAPIClient(app_id, app_secret)
        
        # 尝试加载已保存的令牌
        if not self.client.load_tokens():
            print("⚠️ 未找到有效的访问令牌，需要先进行OAuth授权")
        
        # 水表名称映射 (系统名称 -> Excel列名)
        self.meter_mapping = {
            '荔新大道DN1200流量计': '荔新大道',
            '新城大道医院DN800流量计': '新城大道',
            '三江新总表DN800（2190066）': '三江新总表',
            '宁西总表DN1200': '宁西2总表',
            '沙庄总表': '沙庄总表',
            '如丰大道600监控表': '如丰大道600监控表',
            '三棵树600监控表': '三棵树600监控表',
            '2501200108': '中山西路DN300流量计'
        }
        
        # Excel列映射 (列名 -> 列号)
        self.column_mapping = {
            '日期': 'A',
            '石滩供水服务部日供水': 'B',
            '环比差值': 'C',
            '石滩': 'D',
            '三江': 'E',
            '沙庄': 'F',
            '进水': 'G',
            '荔新大道': 'H',
            '新城大道': 'I',
            '三江新总表': 'J',
            '宁西总表': 'K',
            '宁西2总表': 'L',
            '沙庄总表': 'M',
            '如丰大道600监控表': 'N',
            '三棵树600监控表': 'O',
            '中山西路DN300流量计': 'P'
        }
    
    def check_authorization(self):
        """
        检查授权状态
        
        Returns:
            bool: 是否已授权
        """
        return self.client.check_token_validity()
    
    def get_sheet_info(self):
        """
        获取工作表信息
        
        Returns:
            dict: 工作表信息
        """
        if not self.check_authorization():
            return None
        
        file_info = self.client.get_file_info(self.file_id)
        if file_info:
            print(f"📄 文件名: {file_info.get('name')}")
            print(f"📊 文件类型: {file_info.get('type')}")
            return file_info
        return None
    
    def find_date_row(self, target_date, sheet_id='sheet1'):
        """
        查找指定日期在Excel中的行号
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD格式)
            sheet_id: 工作表ID
            
        Returns:
            int: 行号，未找到返回None
        """
        if not self.check_authorization():
            return None
        
        try:
            # 获取A列的数据 (日期列)
            data = self.client.get_sheet_data(self.file_id, sheet_id, "A:A")
            
            if not data or 'values' not in data:
                print("❌ 无法获取日期列数据")
                return None
            
            values = data['values']
            
            # 查找目标日期
            target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
            
            for i, row in enumerate(values):
                if row and len(row) > 0:
                    cell_value = row[0]
                    
                    # 尝试解析日期
                    try:
                        if isinstance(cell_value, str):
                            # 处理各种日期格式
                            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
                                try:
                                    cell_date = datetime.strptime(cell_value, fmt)
                                    if cell_date.date() == target_datetime.date():
                                        return i + 1  # Excel行号从1开始
                                    break
                                except ValueError:
                                    continue
                    except:
                        continue
            
            print(f"❌ 未找到日期 {target_date} 对应的行")
            return None
            
        except Exception as e:
            print(f"❌ 查找日期行失败: {e}")
            return None
    
    def update_water_data(self, target_date, water_data, sheet_id='sheet1'):
        """
        更新指定日期的水务数据
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD格式)
            water_data: 水务数据字典 {meter_name: value}
            sheet_id: 工作表ID
            
        Returns:
            bool: 是否更新成功
        """
        if not self.check_authorization():
            print("❌ 未授权，无法更新数据")
            return False
        
        # 查找日期行
        row_num = self.find_date_row(target_date, sheet_id)
        
        if not row_num:
            # 如果没找到日期行，尝试在末尾添加新行
            print(f"📝 未找到日期 {target_date}，尝试添加新行")
            return self.append_water_data(target_date, water_data, sheet_id)
        
        print(f"📍 找到日期 {target_date} 在第 {row_num} 行")
        
        # 准备更新数据
        updates = []
        
        for meter_name, value in water_data.items():
            # 查找对应的Excel列
            excel_column = None
            
            # 先尝试直接匹配
            if meter_name in self.column_mapping:
                excel_column = self.column_mapping[meter_name]
            else:
                # 尝试通过映射匹配
                for system_name, excel_name in self.meter_mapping.items():
                    if system_name == meter_name and excel_name in self.column_mapping:
                        excel_column = self.column_mapping[excel_name]
                        break
            
            if excel_column:
                cell_range = f"{excel_column}{row_num}"
                cell_value = value if value is not None else ""
                updates.append((cell_range, [[cell_value]]))
                print(f"📊 准备更新 {meter_name} -> {cell_range}: {cell_value}")
            else:
                print(f"⚠️ 未找到 {meter_name} 对应的Excel列")
        
        # 执行批量更新
        success_count = 0
        for cell_range, values in updates:
            if self.client.update_sheet_data(self.file_id, sheet_id, cell_range, values):
                success_count += 1
            else:
                print(f"❌ 更新失败: {cell_range}")
        
        print(f"✅ 成功更新 {success_count}/{len(updates)} 个数据点")
        return success_count > 0
    
    def append_water_data(self, target_date, water_data, sheet_id='sheet1'):
        """
        在表格末尾追加新的水务数据行
        
        Args:
            target_date: 目标日期 (YYYY-MM-DD格式)
            water_data: 水务数据字典
            sheet_id: 工作表ID
            
        Returns:
            bool: 是否追加成功
        """
        if not self.check_authorization():
            return False
        
        # 构建新行数据
        new_row = [''] * 20  # 预留足够的列
        
        # 设置日期
        new_row[0] = target_date
        
        # 填充水表数据
        for meter_name, value in water_data.items():
            excel_column = None
            
            # 查找对应列
            if meter_name in self.column_mapping:
                col_letter = self.column_mapping[meter_name]
            else:
                for system_name, excel_name in self.meter_mapping.items():
                    if system_name == meter_name and excel_name in self.column_mapping:
                        col_letter = self.column_mapping[excel_name]
                        break
                else:
                    continue
            
            # 将列字母转换为索引
            col_index = ord(col_letter) - ord('A')
            if col_index < len(new_row):
                new_row[col_index] = value if value is not None else ""
        
        # 追加数据
        if self.client.append_sheet_data(self.file_id, sheet_id, [new_row]):
            print(f"✅ 成功追加日期 {target_date} 的数据")
            return True
        else:
            print(f"❌ 追加日期 {target_date} 的数据失败")
            return False
    
    def sync_from_local_data(self, json_file_path, target_date=None):
        """
        从本地JSON数据文件同步到金山文档
        
        Args:
            json_file_path: 本地JSON数据文件路径
            target_date: 目标日期，为None时使用昨天
            
        Returns:
            bool: 是否同步成功
        """
        if not os.path.exists(json_file_path):
            print(f"❌ 数据文件不存在: {json_file_path}")
            return False
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'data' not in data or 'rows' not in data['data']:
                print("❌ 数据文件格式不正确")
                return False
            
            rows = data['data']['rows']
            
            # 确定目标日期
            if not target_date:
                yesterday = datetime.now() - timedelta(days=1)
                target_date = yesterday.strftime('%Y-%m-%d')
            
            print(f"🎯 同步目标日期: {target_date}")
            
            # 提取水表数据
            water_data = {}
            
            for meter in rows:
                meter_name = meter.get('Name', '')
                
                # 查找目标日期的数据
                date_value = meter.get(target_date)
                
                if date_value is not None:
                    water_data[meter_name] = date_value
                    print(f"📊 {meter_name}: {date_value}")
                else:
                    print(f"⚠️ {meter_name}: 无数据")
            
            if not water_data:
                print(f"❌ 没有找到 {target_date} 的数据")
                return False
            
            # 同步到金山文档
            return self.update_water_data(target_date, water_data)
            
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            return False
    
    def get_sync_status(self):
        """
        获取同步状态信息
        
        Returns:
            dict: 状态信息
        """
        status = {
            'authorized': self.check_authorization(),
            'file_id': self.file_id,
            'file_url': self.file_url,
            'client_info': None
        }
        
        if status['authorized']:
            file_info = self.get_sheet_info()
            if file_info:
                status['client_info'] = {
                    'file_name': file_info.get('name'),
                    'file_type': file_info.get('type'),
                    'last_modified': file_info.get('modified_time')
                }
        
        return status


def main():
    """主函数 - 演示同步功能"""
    import glob
    
    # 配置
    file_url = "https://www.kdocs.cn/l/ctPsso05tvI4"
    
    # 创建同步器
    try:
        sync = WaterDataKDocsSync(file_url)
        
        # 检查状态
        status = sync.get_sync_status()
        print(f"🔐 授权状态: {status['authorized']}")
        
        if not status['authorized']:
            print("❌ 请先运行 kdocs_oauth_helper.py 完成授权")
            return
        
        # 查找最新的数据文件
        data_files = glob.glob("WEB_COMPLETE_8_METERS_*.json")
        if not data_files:
            print("❌ 未找到水务数据文件")
            return
        
        latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
        print(f"📄 使用数据文件: {latest_file}")
        
        # 执行同步
        success = sync.sync_from_local_data(latest_file)
        
        if success:
            print("✅ 同步完成！")
        else:
            print("❌ 同步失败！")
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


if __name__ == "__main__":
    main()
