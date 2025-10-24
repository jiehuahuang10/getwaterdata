#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from specific_excel_writer import SpecificExcelWriter
from force_real_data_web import force_get_real_data_for_web
from datetime import datetime, timedelta

def update_excel_with_real_data(target_date):
    """
    获取指定日期的真实水表数据并写入Excel文件
    
    Args:
        target_date: 目标日期 (str 'YYYY-MM-DD' 或 datetime对象)
    
    Returns:
        dict: 操作结果
    """
    print(f"=== 开始更新Excel文件 ===")
    print(f"目标日期: {target_date}")
    
    try:
        # 1. 获取真实数据
        print("1. 获取真实水表数据...")
        data_result = force_get_real_data_for_web(target_date)
        
        if not data_result or not data_result.get('success'):
            print("获取数据失败")
            return {
                'success': False,
                'error': '无法获取水表数据',
                'details': data_result
            }
        
        water_data = data_result.get('data', {})
        print(f"获取到 {len(water_data)} 个水表的数据")
        
        # 2. 提取水表数据
        print("2. 提取水表数据...")
        extracted_data = {}
        
        # 数据格式：{'total': 8, 'rows': [...], 'footer': []}
        rows = water_data.get('rows', [])
        target_date_str = target_date if isinstance(target_date, str) else target_date.strftime('%Y-%m-%d')
        
        for meter_info in rows:
            if isinstance(meter_info, dict):
                meter_name = meter_info.get('Name', '')
                # 查找目标日期的数值
                value = meter_info.get(target_date_str)
                
                if meter_name:
                    # 转换为数值，如果无法转换则为None
                    try:
                        if value is not None and str(value).strip() != '':
                            extracted_data[meter_name] = float(value)
                        else:
                            extracted_data[meter_name] = None
                    except (ValueError, TypeError):
                        extracted_data[meter_name] = None
                    
                    print(f"  {meter_name}: {extracted_data[meter_name]}")
        
        if not extracted_data:
            print("未找到有效的水表数据")
            return {
                'success': False,
                'error': '未找到有效的水表数据',
                'available_dates': list(water_data.keys())
            }
        
        # 3. 写入Excel文件
        print("3. 写入Excel文件...")
        writer = SpecificExcelWriter()
        success = writer.write_water_data(target_date, extracted_data)
        
        if success:
            print("[SUCCESS] Excel文件更新成功！")
            return {
                'success': True,
                'message': f'成功更新 {len(extracted_data)} 个水表的数据到Excel文件',
                'updated_meters': len(extracted_data),
                'target_date': target_date
            }
        else:
            print("[ERROR] Excel文件更新失败")
            return {
                'success': False,
                'error': 'Excel文件更新失败'
            }
            
    except Exception as e:
        print(f"更新Excel时出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'更新Excel时出错: {str(e)}'
        }

def test_integrated_updater():
    """测试集成更新功能"""
    # 测试昨天的数据
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"测试更新日期: {yesterday}")
    
    result = update_excel_with_real_data(yesterday)
    
    print(f"\n=== 测试结果 ===")
    print(f"成功: {result.get('success')}")
    if result.get('success'):
        print(f"消息: {result.get('message')}")
        print(f"更新的水表数量: {result.get('updated_meters')}")
    else:
        print(f"错误: {result.get('error')}")
        if 'available_dates' in result:
            print(f"可用日期: {result['available_dates']}")

if __name__ == '__main__':
    test_integrated_updater()
