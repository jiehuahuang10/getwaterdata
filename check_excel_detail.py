#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl

excel_path = "excel_exports/石滩供水服务部每日总供水情况.xlsx"
wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

print("=" * 80)
print("检查 Excel 文件详细结构")
print("=" * 80)

# 读取前 10 行
for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
    if row_idx >= 10:
        break
    print(f"\n第{row_idx + 1}行:")
    # 只显示非空的单元格
    non_empty = [(i, cell) for i, cell in enumerate(row) if cell]
    if non_empty:
        for col_idx, cell in non_empty[:15]:  # 最多显示15个非空单元格
            print(f"  列{col_idx}: {repr(cell)}")
    else:
        print("  (全部为空)")

wb.close()
print("\n" + "=" * 80)

