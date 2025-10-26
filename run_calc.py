#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

# 直接导入并运行
from calculate_formulas_python import calculate_water_formulas

excel_path = 'excel_exports/石滩供水服务部每日总供水情况.xlsx'
success = calculate_water_formulas(excel_path)
print(f"\n最终结果: {'成功' if success else '失败'}")

