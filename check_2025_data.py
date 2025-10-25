#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl
from datetime import datetime

excel_path = "excel_exports/石滩供水服务部每日总供水情况.xlsx"

print("=" * 80)
print("检查 2025 年数据")
print("=" * 80)

wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
header = rows[3]

# 查找2025年的数据
print(f"\n正在查找2025年的数据...")
found_2025 = False
for i, row in enumerate(rows[4:], start=5):  # 从第5行开始
    date_value = row[0]
    if date_value:
        # 检查是否是2025年
        if isinstance(date_value, datetime) and date_value.year == 2025:
            if not found_2025:
                print(f"\n找到2025年数据！从第{i}行开始")
                found_2025 = True
                
                # 显示这一行的数据
                print(f"\n第{i}行数据（{date_value.strftime('%Y-%m-%d')}）:")
                non_empty_count = 0
                for j, value in enumerate(row):
                    if value is not None and value != '':
                        col_name = header[j] if j < len(header) else f"列{j}"
                        print(f"  [{j:2d}] {col_name}: {value}")
                        non_empty_count += 1
                
                print(f"\n统计: 共 {non_empty_count}/{len(row)} 列有数据")
                break

if not found_2025:
    print("\n未找到2025年的数据！")

wb.close()
print("\n" + "=" * 80)

