#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl

excel_path = "excel_exports/石滩供水服务部每日总供水情况.xlsx"

print("=" * 80)
print("分析 Excel 数据分布")
print("=" * 80)

wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

rows = list(ws.iter_rows(values_only=True))

# 第4行是表头（索引3）
header = rows[3]
print(f"\n表头（第4行，共{len(header)}列）:")
for i, col_name in enumerate(header):
    if col_name:
        print(f"  [{i:2d}] {col_name}")

# 检查第5行数据（索引4，2017-12-01）
print(f"\n第5行数据（第一条数据）:")
if len(rows) > 4:
    data_row = rows[4]
    print(f"总列数: {len(data_row)}")
    print(f"\n有数据的列:")
    for i, value in enumerate(data_row):
        if value is not None and value != '':
            col_name = header[i] if i < len(header) else f"列{i}"
            print(f"  [{i:2d}] {col_name}: {value}")
    
    print(f"\n空的列:")
    empty_cols = []
    for i, value in enumerate(data_row):
        if value is None or value == '':
            col_name = header[i] if i < len(header) else f"列{i}"
            empty_cols.append(f"[{i}]{col_name}")
    print(f"  {', '.join(empty_cols)}")

wb.close()
print("\n" + "=" * 80)

