#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新Excel并重新计算公式的完整流程
适用于本地环境（有Excel）
"""

import sys
import os
from datetime import datetime, timedelta

def auto_update_and_calculate(target_date=None):
    """
    自动更新Excel数据并重新计算公式
    
    Args:
        target_date: 目标日期，默认为昨天
    
    Returns:
        dict: 操作结果
    """
    # 如果没有指定日期，使用昨天
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("=" * 80)
    print(f"自动更新Excel数据并重新计算公式")
    print(f"目标日期: {target_date}")
    print("=" * 80)
    
    # 步骤1：更新数据
    print("\n[步骤1] 更新Excel数据...")
    try:
        from integrated_excel_updater import update_excel_with_real_data
        result = update_excel_with_real_data(target_date)
        
        if not result.get('success'):
            print(f"[ERROR] 数据更新失败: {result.get('message')}")
            return result
        
        print(f"[SUCCESS] 数据更新成功: {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] 数据更新异常: {e}")
        return {'success': False, 'message': f'数据更新异常: {str(e)}'}
    
    # 步骤2：重新计算公式
    print("\n[步骤2] 重新计算Excel公式...")
    try:
        import xlwings as xw
        excel_path = os.path.abspath('excel_exports/石滩供水服务部每日总供水情况.xlsx')
        
        print(f"[INFO] Excel文件路径: {excel_path}")
        
        # 打开Excel应用（不可见）
        print("[INFO] 启动Excel应用...")
        app = xw.App(visible=False)
        
        # 打开工作簿
        print("[INFO] 打开工作簿...")
        wb = app.books.open(excel_path)
        
        # 强制重新计算所有公式
        print("[INFO] 计算公式...")
        wb.app.calculate()
        
        # 保存并关闭
        print("[INFO] 保存工作簿...")
        wb.save()
        wb.close()
        app.quit()
        
        print("[SUCCESS] 公式计算完成并已保存")
        result['formula_calculated'] = True
        
    except ImportError:
        print("[WARNING] xlwings未安装，跳过公式计算")
        print("[INFO] 公式将在Excel中打开时自动计算")
        result['formula_calculated'] = False
        result['note'] = 'xlwings未安装，公式未计算'
        
    except Exception as e:
        print(f"[WARNING] 公式计算失败: {e}")
        result['formula_calculated'] = False
        result['calc_error'] = str(e)
    
    # 步骤3：提交到Git
    print("\n[步骤3] 提交到Git...")
    try:
        import subprocess
        
        # 添加文件
        print("[INFO] 添加文件到Git...")
        subprocess.run(['git', 'add', 'excel_exports/'], check=True)
        
        # 提交
        commit_msg = f"Auto update: {target_date} data with calculated formulas"
        print(f"[INFO] 提交: {commit_msg}")
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # 推送
        print("[INFO] 推送到GitHub...")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("[SUCCESS] 已推送到GitHub")
        result['git_pushed'] = True
        
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Git操作失败: {e}")
        result['git_pushed'] = False
        result['git_error'] = str(e)
    except Exception as e:
        print(f"[WARNING] Git操作异常: {e}")
        result['git_pushed'] = False
        result['git_error'] = str(e)
    
    print("\n" + "=" * 80)
    print("自动更新流程完成")
    print("=" * 80)
    
    return result

if __name__ == '__main__':
    # 从命令行参数获取日期，或使用昨天
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = None
    
    result = auto_update_and_calculate(target_date)
    
    if result.get('success'):
        print("\n✅ 全部完成！")
    else:
        print(f"\n❌ 失败: {result.get('message')}")
        sys.exit(1)

