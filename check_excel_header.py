#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl

excel_path = "excel_exports/石滩供水服务部每日总供水情况.xlsx"
wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

print("=" * 80)
print("检查 Excel 文件表头")
print("=" * 80)

# 读取前 3 行
rows = []
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i >= 3:
        break
    rows.append(list(row))

print(f"\n第1行（总共 {len(rows[0])} 列）:")
for i, cell in enumerate(rows[0]):
    if cell:
        print(f"  列{i}: '{cell}'")
    else:
        print(f"  列{i}: (空)")

print(f"\n第2行（总共 {len(rows[1])} 列）:")
for i, cell in enumerate(rows[1]):
    if cell:
        print(f"  列{i}: '{cell}'")
    else:
        print(f"  列{i}: (空)")

print(f"\n第3行（总共 {len(rows[2])} 列）:")
for i, cell in enumerate(rows[2]):
    if i < 20:  # 显示前20列
        print(f"  列{i}: '{cell}'")

wb.close()
print("\n" + "=" * 80)

