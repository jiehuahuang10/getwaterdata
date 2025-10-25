#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl
from datetime import datetime

excel_path = "excel_exports/石滩供水服务部每日总供水情况.xlsx"

wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

all_rows = list(ws.iter_rows(values_only=True))
data_rows = all_rows[4:]

print("=" * 80)
print("检查日期格式")
print("=" * 80)

# 检查前20行数据的日期
for idx, row in enumerate(data_rows[:20]):
    date_val = row[0]
    print(f"行{idx+5}: 类型={type(date_val).__name__}, 值={repr(date_val)}")
    
    if isinstance(date_val, datetime):
        print(f"  -> datetime对象: {date_val.year}年{date_val.month}月{date_val.day}日")

print("\n查找2025年数据...")
found_2025 = False
for idx, row in enumerate(data_rows):
    date_val = row[0]
    if isinstance(date_val, datetime) and date_val.year == 2025:
        if not found_2025:
            print(f"\n找到2025年数据！从行{idx+5}开始")
            print(f"日期: {date_val}")
            print(f"数据: {row[:10]}")
            found_2025 = True
            break

wb.close()
print("\n" + "=" * 80)

