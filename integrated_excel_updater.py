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
    # 写入调试日志文件
    import sys
    log_file = open('update_debug.log', 'w', encoding='utf-8')
    
    def log(msg):
        print(msg)
        log_file.write(msg + '\n')
        log_file.flush()
        sys.stdout.flush()
    
    log(f"=== 开始更新Excel文件 ===")
    log(f"目标日期: {target_date}")
    
    try:
        # 1. 获取真实数据
        log("1. 获取真实水表数据...")
        data_result = force_get_real_data_for_web(target_date)
        
        if not data_result or not data_result.get('success'):
            log("获取数据失败")
            log_file.close()
            return {
                'success': False,
                'error': '无法获取水表数据',
                'details': data_result
            }
        
        water_data = data_result.get('data', {})
        rows = water_data.get('rows', [])
        log(f"[INFO] 获取到 {len(rows)} 个水表的数据")
        
        # 2. 提取水表数据
        log("2. 提取水表数据...")
        extracted_data = {}
        
        # 数据格式：{'total': 8, 'rows': [...], 'footer': []}
        target_date_str = target_date if isinstance(target_date, str) else target_date.strftime('%Y-%m-%d')
        log(f"[INFO] 目标日期字符串: {target_date_str}")
        
        for meter_info in rows:
            if isinstance(meter_info, dict):
                meter_name = meter_info.get('Name', '')
                # 查找目标日期的数值
                value = meter_info.get(target_date_str)
                
                log(f"[DEBUG] 水表: {meter_name}, 原始值: {value}, 类型: {type(value)}")
                
                if meter_name:
                    # 转换为数值，如果无法转换则为None
                    try:
                        if value is not None and str(value).strip() != '':
                            extracted_data[meter_name] = float(value)
                            log(f"  [OK] {meter_name}: {extracted_data[meter_name]}")
                        else:
                            extracted_data[meter_name] = None
                            log(f"  [EMPTY] {meter_name}: 无数据")
                    except (ValueError, TypeError) as e:
                        extracted_data[meter_name] = None
                        log(f"  [ERROR] {meter_name}: 转换失败 - {e}")
        
        if not extracted_data:
            log("未找到有效的水表数据")
            log_file.close()
            return {
                'success': False,
                'error': '未找到有效的水表数据',
                'available_dates': list(water_data.keys())
            }
        
        # 3. 写入Excel文件
        log("3. 写入Excel文件...")
        writer = SpecificExcelWriter()
        success = writer.write_water_data(target_date, extracted_data)
        
        if success:
            log("[SUCCESS] Excel文件更新成功！")
            log_file.close()
            return {
                'success': True,
                'message': f'成功更新 {len(extracted_data)} 个水表的数据到Excel文件',
                'updated_meters': len(extracted_data),
                'target_date': target_date
            }
        else:
            log("[ERROR] Excel文件更新失败")
            log_file.close()
            return {
                'success': False,
                'error': 'Excel文件更新失败'
            }
            
    except Exception as e:
        log(f"更新Excel时出错: {e}")
        import traceback
        traceback.print_exc()
        log_file.close()
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
