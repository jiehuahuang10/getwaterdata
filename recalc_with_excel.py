#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 xlwings 调用真实的 Excel 来计算所有公式
需要系统安装了 Excel 或 WPS
"""
import xlwings as xw
import os
import time

EXCEL_PATH = "excel_exports/石滩供水服务部每日总供水情况.xlsx"

print("=" * 80)
print("使用 Excel 重新计算所有公式")
print("=" * 80)

if not os.path.exists(EXCEL_PATH):
    print(f"错误: 文件不存在: {EXCEL_PATH}")
    exit(1)

# 转换为绝对路径
abs_path = os.path.abspath(EXCEL_PATH)
print(f"\n文件路径: {abs_path}")

try:
    print(f"\n[>>] 正在启动 Excel...")
    # 创建 Excel 应用实例（不可见）
    app = xw.App(visible=False, add_book=False)
    app.display_alerts = False
    app.screen_updating = False
    
    print(f"[OK] Excel 已启动")
    
    print(f"\n[>>] 正在打开工作簿...")
    wb = app.books.open(abs_path)
    print(f"[OK] 工作簿已打开")
    
    print(f"\n[>>] 正在计算所有公式...")
    # 强制重新计算所有公式
    app.calculation = 'automatic'
    wb.api.Application.CalculateFull()
    print(f"[OK] 公式计算完成")
    
    print(f"\n[>>] 正在保存工作簿...")
    wb.save()
    print(f"[OK] 工作簿已保存")
    
    # 读取第一行2025年数据验证
    ws = wb.sheets[0]
    print(f"\n[>>] 验证数据（查找2025年第一行）...")
    
    # 查找2025年数据的行
    for row in range(5, min(100, ws.used_range.last_cell.row + 1)):
        date_val = ws.range(f'A{row}').value
        if date_val and '2025' in str(date_val):
            print(f"\n找到2025年数据（第{row}行）:")
            # 读取前10列
            for col in range(1, 11):
                cell_val = ws.range(row, col).value
                if cell_val is not None:
                    print(f"  列{col}: {cell_val}")
            break
    
    print(f"\n[>>] 正在关闭 Excel...")
    wb.close()
    app.quit()
    print(f"[OK] Excel 已关闭")
    
    print("\n" + "=" * 80)
    print("[OK] 完成！所有公式已重新计算并保存")
    print("[OK] 请刷新网页查看效果")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] 发生错误: {e}")
    print(f"\n可能的原因:")
    print(f"  1. 系统未安装 Excel 或 WPS")
    print(f"  2. Excel 文件被其他程序占用")
    print(f"  3. xlwings 无法连接到 Excel")
    
    try:
        app.quit()
    except:
        pass
    
    exit(1)

