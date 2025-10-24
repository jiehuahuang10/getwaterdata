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

# ==================== 辅助函数 ====================

def calculate_recent_7days():
    """计算最近7天的日期范围"""
    today = datetime.now()
    end_date = today - timedelta(days=1)  # 昨天
    start_date = end_date - timedelta(days=7)  # 昨天往前推7天
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def sync_excel_to_github(file_path, commit_message):
    """
    将 Excel 文件同步到 GitHub
    
    参数:
        file_path: 文件路径
        commit_message: 提交信息
    
    返回:
        dict: {'success': bool, 'message': str}
    """
    import subprocess
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {'success': False, 'message': f'文件不存在: {file_path}'}
        
        # 获取 GitHub Token
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            return {'success': False, 'message': '未配置 GITHUB_TOKEN 环境变量'}
        
        # 配置 Git 用户信息
        subprocess.run(['git', 'config', 'user.email', 'render-bot@getwaterdata.com'], check=False)
        subprocess.run(['git', 'config', 'user.name', 'Render Auto Sync'], check=False)
        
        # 配置 Git 使用 token 认证
        repo_url = f'https://{github_token}@github.com/jiehuahuang10/getwaterdata.git'
        subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url], check=False)
        
        # Git 操作
        subprocess.run(['git', 'add', file_path], check=True)
        
        result = subprocess.run(
            ['git', 'commit', '-m', commit_message],
            capture_output=True,
            text=True
        )
        
        # 如果没有变化，返回成功（没有需要提交的内容）
        if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
            return {'success': True, 'message': '文件无变化，无需同步'}
        
        # 推送到 GitHub
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if push_result.returncode != 0:
            return {
                'success': False,
                'message': f'推送失败: {push_result.stderr}'
            }
        
        return {
            'success': True,
            'message': '成功同步到 GitHub'
        }
        
    except subprocess.TimeoutExpired:
        return {'success': False, 'message': 'Git 操作超时'}
    except Exception as e:
        return {'success': False, 'message': f'同步失败: {str(e)}'}

# ==================== 首页：功能选择 ====================

@app.route('/')
def index():
    """首页 - 显示三个功能入口"""
    print("=" * 50)
    print("ROOT ROUTE CALLED - RETURNING index_unified.html")
    print("=" * 50)
    # 强制返回主页模板，添加多层缓存控制
    response = app.make_response(render_template('index_unified.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/test')
def test():
    """测试路由 - 验证部署"""
    return jsonify({
        'status': 'ok',
        'message': '新版本已部署！主页应该显示三个功能卡片。',
        'version': '2.0',
        'routes': ['/', '/summary', '/data', '/auto_update']
    })

# ==================== 功能1：月度统计表添加 ====================

@app.route('/summary')
def summary_page():
    """月度统计表页面"""
    return render_template('add_summary.html')

@app.route('/auto_update')
def auto_update_page():
    """自动更新Excel数据页面"""
    return render_template('auto_update.html')

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
        
        # 如果成功，自动同步到 GitHub
        if result.get('success'):
            result['download_url'] = '/download_excel/石滩区分区计量.xlsx'
            
            # 尝试自动同步到 GitHub
            sync_result = sync_excel_to_github(
                'excel_exports/石滩区分区计量.xlsx',
                f"自动更新: 添加{result.get('month', '月度')}统计表"
            )
            
            if sync_result['success']:
                result['message'] += ' | ✅ 已自动同步到GitHub'
                result['github_synced'] = True
            else:
                result['message'] += f" | ⚠️ GitHub同步失败: {sync_result['message']}"
                result['github_synced'] = False
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加统计表失败: {str(e)}'
        })

@app.route('/download_excel/<filename>')
def download_excel(filename):
    """下载 Excel 文件"""
    try:
        from flask import send_file
        file_path = f'excel_exports/{filename}'
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': f'文件不存在: {filename}'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        }), 500

# ==================== 功能2：水务数据获取 ====================

@app.route('/data')
def data_page():
    """水务数据获取页面 - 使用原有的完整界面"""
    # 计算日期范围
    start_date, end_date = calculate_recent_7days()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('index.html', 
                         current_time=current_time,
                         start_date=start_date,
                         end_date=end_date)

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
            
            # 前端逻辑分析:
            # 1. 第1610行: if (result.success && result.data) displayData(result.data)
            # 2. 第1147行: if (!data.data || !data.data.rows)
            # 
            # 数据流: result.data 传给 displayData, 然后访问 data.data.rows
            # 所以需要: result.data.data.rows 存在
            # 即: result = {success: true, data: {data: {rows: [...]}}}
            #
            # JSON文件是: {success: true, data: {rows: [...]}}
            # 所以需要包装一层
            # 调试：打印返回的数据结构
            result = {
                'success': True,
                'data': file_data  # 包含整个JSON,这样result.data.data.rows就能访问到
            }
            print(f"DEBUG: 返回数据有success? {'success' in result}")
            print(f"DEBUG: success值: {result.get('success')}")
            print(f"DEBUG: 有data? {'data' in result}")
            print(f"DEBUG: data有data? {'data' in result.get('data', {})}")
            return jsonify(result)
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
    """执行数据获取任务 - 从水务系统获取真实数据"""
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
        
        # 导入必要的库
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
        task_status['message'] = f'❌ 获取失败: {str(e)}'
    finally:
        task_status['running'] = False
        task_status['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

# ==================== 功能3：自动更新Excel ====================

@app.route('/execute_auto_update', methods=['POST'])
def execute_auto_update():
    """执行自动更新Excel任务"""
    try:
        data = request.get_json()
        target_date = data.get('date')
        
        if not target_date:
            return jsonify({'success': False, 'message': '请提供目标日期'})
        
        # 导入更新模块
        from integrated_excel_updater import update_excel_with_real_data
        
        # 执行更新
        result = update_excel_with_real_data(target_date)
        
        return jsonify(result)
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'message': f'缺少必要的模块: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        })

# ==================== 启动应用 ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

