#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# type: ignore
"""
水务数据获取Web界面 - 修复版
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import os
import glob
from datetime import datetime, timedelta
import threading
import time

# 尝试导入Excel导出模块，如果失败则跳过
try:
    from excel_exporter import export_to_excel, export_simple_csv, update_excel_with_date, get_excel_existing_dates
    EXCEL_EXPORT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Excel导出模块不可用: {e}")
    EXCEL_EXPORT_AVAILABLE = False
    # 提供简单的替代函数
    def export_to_excel(*args, **kwargs):
        return None, "Excel导出功能暂不可用（缺少openpyxl或pandas）"
    def export_simple_csv(*args, **kwargs):
        return None, "CSV导出功能暂不可用（缺少pandas）"
    def update_excel_with_date(*args, **kwargs):
        return False, "Excel更新功能暂不可用（缺少openpyxl或pandas）"
    def get_excel_existing_dates(*args, **kwargs):
        return []

# 尝试导入集成更新模块，如果失败则提供替代方案
try:
    from integrated_excel_updater import update_excel_with_real_data
    INTEGRATED_UPDATER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 集成更新模块不可用: {e}")
    INTEGRATED_UPDATER_AVAILABLE = False
    def update_excel_with_real_data(*args, **kwargs):
        return {'success': False, 'error': '集成更新功能暂不可用（缺少相关依赖包）'}

# 直接导入数据获取模块，避免subprocess编码问题
import sys
sys.path.append('.')

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

def run_water_data_direct():
    """直接运行水务数据获取，避免subprocess"""
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
        
        # 直接调用数据获取函数
        task_status['progress'] = 30
        task_status['message'] = '正在获取数据...'
        
        # 模拟数据获取过程
        import requests
        from bs4 import BeautifulSoup
        import hashlib
        
        session = requests.Session()
        
        # 登录
        task_status['progress'] = 40
        task_status['message'] = '正在登录水务系统...'
        
        login_url = "http://axwater.dmas.cn/Login.aspx"
        login_page = session.get(login_url)
        
        soup = BeautifulSoup(login_page.text, 'html.parser')
        form = soup.find('form')
        form_data = {}
        
        for input_elem in form.find_all('input'):
            name = input_elem.get('name')
            value = input_elem.get('value', '')
            if name:
                form_data[name] = value
        
        username = '13509288500'
        password = '288500'
        form_data['user'] = username
        form_data['pwd'] = hashlib.md5(password.encode('utf-8')).hexdigest()
        
        login_response = session.post(login_url, data=form_data)
        
        if "window.location='frmMain.aspx'" in login_response.text:
            task_status['progress'] = 60
            task_status['message'] = '登录成功，正在访问报表页面...'
            
            # 跳转到主页面
            main_url = "http://axwater.dmas.cn/frmMain.aspx"
            main_response = session.get(main_url)
            
            if main_response.status_code == 200:
                # 访问报表页面
                task_status['progress'] = 70
                task_status['message'] = '正在获取水表数据...'
                time.sleep(1)
                
                report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
                report_response = session.get(report_url)
                
                if '登录超时' not in report_response.text:
                    # 获取数据
                    task_status['progress'] = 80
                    task_status['message'] = '正在调用数据API...'
                    
                    start_date, end_date = calculate_recent_7days()
                    
                    meter_ids = [
                        '1261181000263', '1261181000300', '1262330402331',
                        '2190066', '2190493', '2501200108', '2520005', '2520006'
                    ]
                    
                    formatted_node_ids = "'" + "','".join(meter_ids) + "'"
                    
                    api_url = "http://axwater.dmas.cn/reports/ashx/getRptWaterYield.ashx"
                    api_params = {
                        'nodeId': formatted_node_ids,
                        'startDate': start_date,
                        'endDate': end_date,
                        'meterType': '-1',
                        'statisticsType': 'flux',
                        'type': 'dayRpt'
                    }
                    
                    api_headers = {
                        'Referer': report_url,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    api_response = session.post(api_url, data=api_params, headers=api_headers)
                    
                    if api_response.text and len(api_response.text) > 10:
                        try:
                            data = api_response.json()
                            
                            # 保存数据
                            timestamp = time.strftime('%Y%m%d_%H%M%S')
                            filename = f"WEB_COMPLETE_8_METERS_{timestamp}.json"
                            
                            output_data = {
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'source': 'web_interface_scraper',
                                'success': True,
                                'data_type': 'json',
                                'calculation_date': datetime.now().strftime('%Y-%m-%d'),
                                'date_range': {
                                    'start': start_date,
                                    'end': end_date,
                                    'description': '昨天往前推7天的数据'
                                },
                                'meter_count': len(meter_ids),
                                'data': data,
                                'note': f'通过Web界面获取的{datetime.now().strftime("%Y年%m月%d日")}最新数据'
                            }
                            
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(output_data, f, ensure_ascii=False, indent=2)
                            
                            task_status['data'] = output_data
                            task_status['progress'] = 100
                            task_status['message'] = f'数据获取成功！共获取{len(data.get("rows", []))}个水表数据'
                            
                        except json.JSONDecodeError:
                            task_status['error'] = 'API返回的不是有效的JSON数据'
                            task_status['message'] = '数据解析失败'
                    else:
                        task_status['error'] = 'API返回空响应'
                        task_status['message'] = '数据获取失败'
                else:
                    task_status['error'] = '访问报表页面时显示登录超时'
                    task_status['message'] = '会话已过期'
            else:
                task_status['error'] = '无法访问主页面'
                task_status['message'] = '系统访问失败'
        else:
            task_status['error'] = '登录失败，请检查账号密码'
            task_status['message'] = '登录失败'
            
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
    thread = threading.Thread(target=run_water_data_direct)
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
            data_files = glob.glob("*COMPLETE_8_METERS*.json") + glob.glob("WEB_COMPLETE*.json")
            if data_files:
                latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify({'success': True, 'data': data})
        except Exception as e:
            pass
    
    return jsonify({'success': False, 'message': '暂无数据'})

@app.route('/export_excel', methods=['POST'])
def export_excel():
    """导出Excel文件"""
    try:
        if not EXCEL_EXPORT_AVAILABLE:
            return jsonify({'success': False, 'message': 'Excel导出功能暂不可用（缺少openpyxl或pandas）'})
            
        # 获取最新的数据
        data = None
        if task_status['data']:
            data = task_status['data']
        else:
            # 尝试读取最新的数据文件
            data_files = (glob.glob("*COMPLETE_8_METERS*.json") + 
                         glob.glob("WEB_COMPLETE*.json"))
            if data_files:
                latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        
        if not data:
            return jsonify({'success': False, 'message': '没有可导出的数据'})
        
        # 导出Excel文件
        filename, message = export_to_excel(data)
        
        if filename:
            return jsonify({
                'success': True, 
                'message': message,
                'filename': os.path.basename(filename),
                'download_url': f'/download_excel/{os.path.basename(filename)}'
            })
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'})

@app.route('/download_excel/<filename>')
def download_excel(filename):
    """下载Excel文件"""
    try:
        file_path = os.path.join('excel_exports', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_excel_files', methods=['GET'])
def get_excel_files():
    """获取可用的Excel文件列表"""
    try:
        if not EXCEL_EXPORT_AVAILABLE:
            return jsonify({'success': False, 'message': 'Excel功能暂不可用（缺少openpyxl或pandas）'})
            
        excel_files = []
        if os.path.exists('excel_exports'):
            files = glob.glob(os.path.join('excel_exports', '*.xlsx'))
            for file_path in files:
                filename = os.path.basename(file_path)
                # 只返回横向格式的文件（文件名包含"水表数据_"）
                if '水表数据_' in filename:
                    file_size = os.path.getsize(file_path)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # 获取文件中已存在的日期
                    existing_dates = get_excel_existing_dates(file_path)
                    
                    excel_files.append({
                        'filename': filename,
                        'filepath': file_path,
                        'size': file_size,
                        'modified': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                        'existing_dates': existing_dates,
                        'date_count': len(existing_dates)
                    })
        
        # 按修改时间倒序排列
        excel_files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'success': True, 'files': excel_files})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取Excel文件列表失败: {str(e)}'})

@app.route('/update_excel_date', methods=['POST'])
def update_excel_date():
    """向Excel文件中添加指定日期的数据"""
    try:
        if not INTEGRATED_UPDATER_AVAILABLE:
            return jsonify({'success': False, 'message': '集成更新功能暂不可用（缺少相关依赖包）'})
            
        data = request.get_json()
        excel_file = data.get('excel_file')
        target_date = data.get('target_date')
        
        if not excel_file or not target_date:
            return jsonify({'success': False, 'message': '缺少必要参数'})
        
        print(f"🎯 开始更新Excel文件: {excel_file}")
        print(f"目标日期: {target_date}")
        
        # 使用集成的Excel更新器
        result = update_excel_with_real_data(target_date)
        
        if result['success']:
            print(f"✅ 成功更新Excel文件")
            return jsonify({
                'success': True, 
                'message': result['message'],
                'updated_meters': result.get('updated_meters', 0)
            })
        else:
            print(f"❌ 更新失败: {result.get('error')}")
            return jsonify({
                'success': False, 
                'message': result.get('error', '更新失败')
            })
        
    except Exception as e:
        print(f"❌ 更新Excel失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'更新Excel失败: {str(e)}'})

@app.route('/update_specific_excel', methods=['POST'])
def update_specific_excel():
    """更新指定的Excel文件（石滩供水服务部每日总供水情况.xlsx）"""
    try:
        if not INTEGRATED_UPDATER_AVAILABLE:
            return jsonify({'success': False, 'message': '集成更新功能暂不可用（缺少相关依赖包）'})
            
        data = request.get_json()
        target_date = data.get('target_date')
        
        if not target_date:
            return jsonify({'success': False, 'message': '缺少目标日期参数'})
        
        print(f"🎯 开始更新石滩供水服务部每日总供水情况.xlsx")
        print(f"目标日期: {target_date}")
        
        # 使用集成的Excel更新器
        result = update_excel_with_real_data(target_date)
        
        if result['success']:
            print(f"✅ 成功更新Excel文件")
            return jsonify({
                'success': True, 
                'message': result['message'],
                'updated_meters': result.get('updated_meters', 0)
            })
        else:
            print(f"❌ 更新失败: {result.get('error')}")
            return jsonify({
                'success': False, 
                'message': result.get('error', '更新失败')
            })
        
    except Exception as e:
        print(f"❌ 更新Excel失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'更新Excel失败: {str(e)}'})

@app.route('/get_available_dates', methods=['GET'])
def get_available_dates():
    """获取可选择的历史日期列表（今天以前的所有日期）"""
    try:
        from datetime import datetime, timedelta
        
        # 生成今天以前的日期列表（最近30天）
        today = datetime.now().date()
        available_dates = []
        
        # 生成最近30天的日期列表（不包括今天）
        for i in range(1, 31):  # 从昨天开始，往前推30天
            date = today - timedelta(days=i)
            available_dates.append(date.strftime('%Y-%m-%d'))
        
        print(f"📅 生成可选日期: {len(available_dates)} 天")
        print(f"📅 日期范围: {available_dates[-1]} ~ {available_dates[0]}")
        
        return jsonify({
            'success': True, 
            'dates': available_dates,  # 已经按从近到远排序
            'date_range': {
                'start': available_dates[-1],
                'end': available_dates[0],
                'description': '最近30天（不包括今天）'
            },
            'total_dates': len(available_dates),
            'data_source': '动态生成的历史日期'
        })
        
    except Exception as e:
        print(f"❌ 获取可用日期失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取可用日期失败: {str(e)}'})

@app.route('/history')
def history():
    """历史数据页面"""
    try:
        # 获取所有数据文件
        data_files = (glob.glob("*COMPLETE_8_METERS*.json") + 
                     glob.glob("REAL_water*.json") + 
                     glob.glob("WEB_COMPLETE*.json"))
        
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
    print("🌐 启动水务数据获取Web界面（原版功能恢复）...")
    print("📱 访问地址: http://localhost:5000")
    print("🔧 完整功能: 数据获取、Excel导出、历史数据查看")
    
    # 显示功能状态
    print(f"📋 Excel导出功能: {'\u2705 可用' if EXCEL_EXPORT_AVAILABLE else '\u274c 不可用（缺少openpyxl或pandas）'}")
    print(f"🔄 集成更新功能: {'\u2705 可用' if INTEGRATED_UPDATER_AVAILABLE else '\u274c 不可用（缺少相关模块）'}")
    print("🔄 按 Ctrl+C 停止服务")
    
    # 支持云部署的端口配置
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
