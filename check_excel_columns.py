#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl

excel_path = "excel_exports/石滩供水服务部每日总供水情况.xlsx"
wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
ws = wb.active

print("=" * 80)
print("检查 Excel 列数和表头")
print("=" * 80)

all_rows = list(ws.iter_rows(values_only=True))

# 第4行是表头（索引3）
header = all_rows[3]

print(f"\n总列数: {len(header)}")
print(f"\n完整表头（共 {len(header)} 列）:")
for i, col_name in enumerate(header):
    if col_name:
        print(f"  列{i}: {repr(col_name)}")
    else:
        print(f"  列{i}: (空)")

# 检查第5行的数据
print(f"\n第5行数据样例（前15列）:")
if len(all_rows) > 4:
    row5 = all_rows[4]
    for i in range(min(15, len(row5))):
        print(f"  列{i}: {repr(row5[i])}")

wb.close()
print("\n" + "=" * 80)

