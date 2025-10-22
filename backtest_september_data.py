#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
回测9月数据：对比提取的数据和表格中的真实数据
"""

import openpyxl
from extract_water_data import extract_monthly_data

def main():
    print("="*100)
    print("[Backtest] September 2025 Data Validation")
    print("="*100)
    
    # 步骤1：从数据源提取9月数据
    print("\n[Step 1] Extract data from source file...")
    extracted_data = extract_monthly_data(2025, 9)
    
    # 步骤2：读取石滩区分区计量表中的9月数据
    print(f"\n{'='*100}")
    print("[Step 2] Read existing data from target table...")
    print(f"{'='*100}")
    
    target_file = "excel_exports/石滩区分区计量.xlsx"
    wb = openpyxl.load_workbook(target_file, data_only=True)
    ws = wb["石滩区"]
    
    # 9月数据在第58行开始
    september_start_row = 58
    
    print(f"\n[September Data in Table]")
    print(f"  Start Row: {september_start_row}")
    
    # 读取9月的3行数据
    table_data = {
        "row1": {},  # 第61行：总表
        "row2": {},  # 第62行：总表
        "row3": {},  # 第63行：分表
    }
    
    data_row_mapping = {
        "row1": september_start_row + 3,  # 第61行
        "row2": september_start_row + 4,  # 第62行
        "row3": september_start_row + 5,  # 第63行
    }
    
    column_mapping = {
        "B": 2,  # 荔新大道
        "C": 3,  # 宁西总表
        "D": 4,  # 如丰大道
        "E": 5,  # 新城大道医院NB
        "F": 6,  # 三棵竹
    }
    
    for row_name, row_num in data_row_mapping.items():
        print(f"\n  {row_name} (Row {row_num}):")
        for col_name, col_num in column_mapping.items():
            val = ws.cell(row_num, col_num).value
            table_data[row_name][col_name] = val
            print(f"    Col {col_name}: {val:>15,.0f}" if val else f"    Col {col_name}: {val}")
    
    # 步骤3：对比数据
    print(f"\n{'='*100}")
    print("[Step 3] Data Comparison")
    print(f"{'='*100}")
    
    # 映射关系（根据9月真实数据的分布）
    comparison_mapping = {
        "荔新大道": ("row1", "B"),
        "宁西2总表": ("row1", "C"),
        "如丰大道600监控表": ("row2", "D"),  # 第2行
        "新城大道医院NB": ("row2", "E"),
        "三棵树600监控表": ("row3", "F"),  # 第3行
    }
    
    print(f"\n{'监控点名称':<25s} | {'提取的数据':>15s} | {'表格中的数据':>15s} | {'差异':>15s} | {'状态':<10s}")
    print("-" * 100)
    
    all_match = True
    for name, (row_name, col_name) in comparison_mapping.items():
        extracted_val = extracted_data['totals'][name]
        table_val = table_data[row_name][col_name]
        
        if table_val is None:
            table_val = 0
        
        diff = extracted_val - table_val
        
        # 处理浮点数精度问题
        is_match = abs(diff) < 0.01
        match_status = "[OK] MATCH" if is_match else "[ERR] DIFF"
        
        if not is_match:
            all_match = False
        
        print(f"{name:<25s} | {extracted_val:>15,.0f} | {table_val:>15,.0f} | {diff:>15,.0f} | {match_status:<10s}")
    
    # 步骤4：总结
    print(f"\n{'='*100}")
    print("[Result]")
    print(f"{'='*100}")
    
    if all_match:
        print("\n[OK] SUCCESS! All data matches perfectly!")
        print("  The extraction logic is correct.")
    else:
        print("\n[WARNING] Some data doesn't match.")
        print("  Please check the column mapping or date range.")
    
    print(f"\n{'='*100}")
    print("[Backtest Complete]")
    print(f"{'='*100}")

if __name__ == "__main__":
    main()

