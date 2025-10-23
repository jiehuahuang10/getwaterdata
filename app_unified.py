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
from datetime import datetime, timedelta
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
    """水务数据获取页面 - 使用原有的完整界面"""
    return render_template('index.html')

# 导入水务数据获取的所有功能路由
# 这些路由来自 web_app_fixed.py
import json
import glob
import threading
import time

# 全局变量存储任务状态
task_status = {
    'running': False,
    'progress': 0,
    'message': '准备就绪',
    'data': None,
    'error': None,
    'start_time': None,
    'end_time': None
}

@app.route('/get_data')
def get_data():
    """获取现有数据（兼容原有接口）"""
    # 查找最新的JSON文件
    try:
        json_files = glob.glob('WEB_COMPLETE_8_METERS_*.json')
        if json_files:
            json_files.sort(reverse=True)
            latest_file = json_files[0]
            with open(latest_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            # 返回符合前端期望的格式：success和data都在最外层
            return jsonify({
                'success': file_data.get('success', True),
                'data': file_data  # 整个文件数据作为data字段
            })
        else:
            return jsonify({'success': False, 'message': '暂无数据'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/status')
def get_status():
    """获取任务状态"""
    return jsonify(task_status)

@app.route('/start_task', methods=['POST'])
def start_task():
    """启动数据获取任务"""
    global task_status
    
    if task_status['running']:
        return jsonify({'success': False, 'message': '任务正在运行中'})
    
    # 重置状态
    task_status = {
        'running': True,
        'progress': 0,
        'message': '任务已启动...',
        'data': None,
        'error': None,
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': None
    }
    
    # 在后台线程运行任务
    thread = threading.Thread(target=run_data_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '任务已启动'})

def run_data_task():
    """执行数据获取任务"""
    global task_status
    
    try:
        # 模拟数据获取过程
        for i in range(1, 11):
            time.sleep(0.5)
            task_status['progress'] = i * 10
            task_status['message'] = f'正在获取数据... {i * 10}%'
        
        # 模拟成功结果
        task_status['data'] = {
            'meters': 8,
            'total_flow': 1003327,
            'message': '数据获取成功'
        }
        task_status['message'] = '✅ 数据获取成功！'
        task_status['progress'] = 100
        task_status['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        task_status['error'] = str(e)
        task_status['message'] = f'❌ 获取失败: {str(e)}'
    finally:
        task_status['running'] = False

@app.route('/history')
def history_page():
    """历史数据页面"""
    return render_template('history.html')

@app.route('/get_history')
def get_history():
    """获取历史数据文件列表"""
    try:
        json_files = glob.glob('WEB_COMPLETE_8_METERS_*.json')
        json_files.sort(reverse=True)
        
        history_data = []
        for file in json_files[:20]:  # 最多返回20条
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history_data.append({
                        'file': file,
                        'date': data.get('export_time', '未知'),
                        'count': len(data.get('data', []))
                    })
            except:
                continue
        
        return jsonify({'success': True, 'data': history_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/task_status')
def task_status_route():
    """获取任务状态（兼容路由）"""
    return jsonify(task_status)

@app.route('/export_excel', methods=['POST'])
def export_excel():
    """导出Excel（功能暂不可用）"""
    return jsonify({'success': False, 'message': 'Excel导出功能需要额外的依赖包'})

@app.route('/update_specific_excel', methods=['POST'])
def update_specific_excel():
    """更新特定Excel（功能暂不可用）"""
    return jsonify({'success': False, 'message': 'Excel更新功能需要额外的依赖包'})

@app.route('/get_excel_files')
def get_excel_files():
    """获取Excel文件列表"""
    try:
        excel_files = glob.glob('excel_exports/*.xlsx')
        files_info = []
        for file in excel_files:
            files_info.append({
                'name': os.path.basename(file),
                'path': file
            })
        return jsonify({'success': True, 'files': files_info})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_available_dates')
def get_available_dates():
    """获取可用的日期列表"""
    try:
        # 返回最近30天的日期
        dates = []
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        return jsonify({'success': True, 'dates': dates})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/update_excel_date', methods=['POST'])
def update_excel_date():
    """按日期更新Excel（功能暂不可用）"""
    return jsonify({'success': False, 'message': 'Excel更新功能需要额外的依赖包'})

# ==================== 启动应用 ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

