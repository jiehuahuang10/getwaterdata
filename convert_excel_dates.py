#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

# Excel日期序列号（从1900年1月1日开始）
dates = [45778, 45809, 45748, 45689, 45717]

print("=== Excel日期序列号转换 ===\n")

for date_num in dates:
    # Excel的日期起点是1900年1月1日，但实际上Excel有个bug，把1900当闰年了
    # 所以需要减去2天
    excel_start = datetime(1899, 12, 30)
    actual_date = excel_start + timedelta(days=date_num)
    year_month = f"{actual_date.year}年{actual_date.month}月"
    print(f"{date_num} -> {actual_date.strftime('%Y年%m月%d日')} -> 月份: {year_month}")

