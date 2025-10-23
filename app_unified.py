#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据管理系统 - 统一版
包含两个功能：
1. 月度统计表添加
2. 水务数据获取
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
import copy
from datetime import datetime
import os
import re

app = Flask(__name__)

# Excel文件路径
EXCEL_PATH = "excel_exports/石滩区分区计量.xlsx"
DATA_SOURCE_PATH = "excel_exports/石滩供水服务部每日总供水情况.xlsx"

# ==================== 首页：功能选择 ====================

@app.route('/')
def index():
    """首页 - 显示两个功能入口"""
    return render_template('index_unified.html')

# ==================== 功能1：月度统计表添加 ====================

@app.route('/summary')
def summary_page():
    """月度统计表页面"""
    return render_template('add_summary.html')

@app.route('/get_info')
def get_info():
    """获取Excel文件信息"""
    try:
        if not os.path.exists(EXCEL_PATH):
            return jsonify({
                'success': False,
                'message': f'Excel文件不存在: {EXCEL_PATH}'
            })
        
        wb = openpyxl.load_workbook(EXCEL_PATH)
        
        if "石滩区" not in wb.sheetnames:
            return jsonify({
                'success': False,
                'message': '工作表"石滩区"不存在'
            })
        
        ws = wb["石滩区"]
        
        # 查找最后一个月份
        last_month = None
        for row in range(ws.max_row, max(0, ws.max_row - 30), -1):
            for col in range(1, 10):
                cell_value = ws.cell(row, col).value
                if cell_value:
                    # 尝试匹配文本格式的月份
                    if isinstance(cell_value, str):
                        match = re.search(r'(\d{4})年(\d{1,2})月', cell_value)
                        if match:
                            last_month = cell_value
                            break
                    # 尝试匹配Excel日期格式
                    elif isinstance(cell_value, (int, float)):
                        try:
                            from datetime import datetime, timedelta
                            excel_date = datetime(1899, 12, 30) + timedelta(days=int(cell_value))
                            last_month = f"{excel_date.year}年{excel_date.month}月"
                            break
                        except:
                            pass
            if last_month:
                break
        
        wb.close()
        
        return jsonify({
            'success': True,
            'excel_path': os.path.basename(EXCEL_PATH),
            'total_rows': ws.max_row,
            'last_month': last_month
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'读取Excel文件失败: {str(e)}'
        })

@app.route('/add_summary', methods=['POST'])
def add_summary():
    """添加月度统计表"""
    try:
        data = request.get_json()
        month_offset = data.get('month_offset', 1)
        sale_values = data.get('sale_values', [])
        
        # 导入添加函数
        from add_summary_web import add_monthly_summary_to_main
        
        result = add_monthly_summary_to_main(
            month_offset=month_offset,
            use_real_data=True,
            sale_values=sale_values
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加统计表失败: {str(e)}'
        })

# ==================== 功能2：水务数据获取 ====================

@app.route('/data')
def data_page():
    """水务数据获取页面"""
    return render_template('water_data.html')

@app.route('/get_water_data')
def get_water_data():
    """获取水务数据"""
    try:
        # 这里可以添加获取水务数据的逻辑
        return jsonify({
            'success': True,
            'message': '水务数据获取功能开发中...'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })

# ==================== 启动应用 ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

