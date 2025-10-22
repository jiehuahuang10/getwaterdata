#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找9月在哪里
"""

import openpyxl

excel_path = "excel_exports/石滩区分区计量.xlsx"

wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb["石滩区"]

print("查找第50-65行的所有内容:")

for row in range(50, 66):
    row_data = []
    for col in range(1, 15):
        val = ws.cell(row, col).value
        if val:
            row_data.append(f"列{col}:{val}")
    
    if row_data:
        print(f"第{row}行: {' | '.join(row_data[:8])}")

wb.close()

