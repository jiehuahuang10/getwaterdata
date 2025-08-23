#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据获取Web界面
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import sys
import json
import os
import glob
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

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

def calculate_recent_7days():
    """计算最近7天的日期范围"""
    today = datetime.now()
    end_date = today - timedelta(days=1)  # 昨天
    start_date = end_date - timedelta(days=7)  # 昨天往前推7天
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def run_water_data_scraper():
    """后台运行水务数据获取脚本"""
    global task_status
    
    try:
        task_status['running'] = True
        task_status['progress'] = 0
        task_status['message'] = '开始获取数据...'
        task_status['error'] = None
        task_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task_status['data'] = None
        
        # 更新进度
        task_status['progress'] = 10
        task_status['message'] = '正在登录系统...'
        time.sleep(1)
        
        # 使用更安全的方式运行脚本
        import os
        
        # 设置环境变量确保UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 运行完整版脚本
        result = subprocess.run([
            sys.executable, 'complete_8_meters_getter.py'
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', 
           env=env, timeout=300, shell=True)  # 5分钟超时
        
        task_status['progress'] = 80
        task_status['message'] = '数据获取完成，正在处理...'
        
        # 无论返回码如何，都尝试查找数据文件
        data_files = glob.glob("COMPLETE_8_METERS_*.json")
        if data_files:
            latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
            
            # 检查文件是否是最近创建的（5分钟内）
            file_time = os.path.getmtime(latest_file)
            current_time = time.time()
            
            if current_time - file_time < 300:  # 5分钟内创建的文件
                try:
                    # 读取数据
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    task_status['data'] = data
                    task_status['progress'] = 100
                    task_status['message'] = f'数据获取成功！共获取{len(data.get("data", {}).get("rows", []))}个水表数据'
                except Exception as read_error:
                    task_status['error'] = f'读取数据文件失败: {str(read_error)}'
                    task_status['message'] = '数据文件读取失败'
            else:
                task_status['error'] = '未找到新的数据文件'
                task_status['message'] = '数据获取可能失败'
        else:
            # 如果没有找到数据文件，显示脚本输出信息
            if result.stderr:
                task_status['error'] = f'脚本执行错误: {result.stderr[:500]}'
            else:
                task_status['error'] = '未找到生成的数据文件，可能是脚本执行失败'
            task_status['message'] = '数据获取失败'
            
    except subprocess.TimeoutExpired:
        task_status['error'] = '操作超时（5分钟）'
        task_status['message'] = '数据获取超时'
    except Exception as e:
        task_status['error'] = str(e)
        task_status['message'] = f'发生错误: {str(e)}'
    finally:
        task_status['running'] = False
        task_status['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    """主页面"""
    start_date, end_date = calculate_recent_7days()
    return render_template('index.html', 
                         start_date=start_date, 
                         end_date=end_date,
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/start_task', methods=['POST'])
def start_task():
    """开始数据获取任务"""
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
    
    # 启动后台线程
    thread = threading.Thread(target=run_water_data_scraper)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': '数据获取任务已启动'})

@app.route('/task_status')
def get_task_status():
    """获取任务状态"""
    return jsonify(task_status)

@app.route('/get_data')
def get_data():
    """获取最新数据"""
    if task_status['data']:
        return jsonify({
            'success': True,
            'data': task_status['data']
        })
    else:
        # 尝试读取最新的数据文件
        try:
            data_files = glob.glob("COMPLETE_8_METERS_*.json")
            if data_files:
                latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify({'success': True, 'data': data})
        except Exception as e:
            pass
    
    return jsonify({'success': False, 'message': '暂无数据'})

@app.route('/history')
def history():
    """历史数据页面"""
    try:
        # 获取所有数据文件
        data_files = glob.glob("COMPLETE_8_METERS_*.json") + glob.glob("REAL_water_*.json")
        
        history_data = []
        for file in data_files:
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(file))
                file_size = os.path.getsize(file)
                
                # 尝试读取基本信息
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                meter_count = len(data.get('data', {}).get('rows', []))
                date_range = data.get('date_range', {})
                
                history_data.append({
                    'filename': file,
                    'timestamp': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                    'size': file_size,
                    'meter_count': meter_count,
                    'date_range': f"{date_range.get('start', '')} 至 {date_range.get('end', '')}"
                })
            except:
                continue
        
        # 按时间排序
        history_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return render_template('history.html', history_data=history_data)
    except Exception as e:
        return render_template('history.html', history_data=[], error=str(e))

if __name__ == '__main__':
    print("🌐 启动水务数据获取Web界面...")
    print("📱 访问地址: http://localhost:5000")
    print("🔄 按 Ctrl+C 停止服务")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
