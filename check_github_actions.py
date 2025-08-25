#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 状态检查脚本
用于检查定时任务的执行状态和历史记录
"""

import requests
import json
from datetime import datetime, timedelta
import os

def check_github_actions_status():
    """检查GitHub Actions状态"""
    
    # GitHub API配置
    repo_owner = "jiehuahuang10"
    repo_name = "getwaterdata"
    workflow_name = "每日水务数据自动更新"
    
    # 如果没有设置token，使用公开API（有限制）
    token = os.getenv('GITHUB_TOKEN')
    
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    try:
        # 获取工作流运行历史
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/daily-water-data.yml/runs"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            runs = response.json()['workflow_runs']
            
            print("=" * 60)
            print("🔍 GitHub Actions 执行状态检查")
            print("=" * 60)
            
            if runs:
                latest_run = runs[0]
                print(f"📅 最新执行时间: {latest_run['created_at']}")
                print(f"🔄 执行状态: {latest_run['status']}")
                print(f"✅ 结论: {latest_run['conclusion']}")
                print(f"🎯 触发方式: {latest_run['event']}")
                
                # 检查最近7天的执行情况
                print("\n📊 最近7天执行情况:")
                print("-" * 40)
                
                today = datetime.now()
                for i in range(7):
                    check_date = today - timedelta(days=i)
                    date_str = check_date.strftime('%Y-%m-%d')
                    
                    # 查找该日期的执行记录
                    daily_runs = [run for run in runs if run['created_at'].startswith(date_str)]
                    
                    if daily_runs:
                        run = daily_runs[0]
                        status_emoji = "✅" if run['conclusion'] == 'success' else "❌"
                        print(f"{date_str}: {status_emoji} {run['conclusion']} ({run['created_at'][11:16]})")
                    else:
                        print(f"{date_str}: ⚪ 无执行记录")
                
                # 统计信息
                success_count = len([run for run in runs[:10] if run['conclusion'] == 'success'])
                total_count = min(10, len(runs))
                success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
                
                print(f"\n📈 最近10次执行成功率: {success_rate:.1f}% ({success_count}/{total_count})")
                
                # 检查是否有定时执行
                scheduled_runs = [run for run in runs[:10] if run['event'] == 'schedule']
                if scheduled_runs:
                    print(f"⏰ 定时执行次数: {len(scheduled_runs)}")
                else:
                    print("⚠️ 警告: 最近没有检测到定时执行")
                
            else:
                print("❌ 没有找到执行记录")
                
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")

def check_local_execution_status():
    """检查本地执行状态文件"""
    print("\n" + "=" * 60)
    print("📁 本地执行状态检查")
    print("=" * 60)
    
    # 检查执行摘要文件
    if os.path.exists('last_execution_summary.json'):
        try:
            with open('last_execution_summary.json', 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            print(f"📅 最后执行时间: {summary.get('execution_time', '未知')}")
            print(f"🎯 目标日期: {summary.get('target_date', '未知')}")
            print(f"✅ 执行结果: {'成功' if summary.get('success') else '失败'}")
            
            if 'result' in summary:
                result = summary['result']
                if 'updated_meters' in result:
                    print(f"📊 更新水表数量: {result['updated_meters']}")
                if 'message' in result:
                    print(f"💬 执行消息: {result['message']}")
                    
        except Exception as e:
            print(f"❌ 读取执行摘要失败: {str(e)}")
    else:
        print("⚠️ 没有找到本地执行摘要文件")
    
    # 检查Excel文件
    excel_file = 'excel_exports/石滩供水服务部每日总供水情况.xlsx'
    if os.path.exists(excel_file):
        file_size = os.path.getsize(excel_file)
        mod_time = datetime.fromtimestamp(os.path.getmtime(excel_file))
        print(f"📁 Excel文件大小: {file_size:,} 字节")
        print(f"📅 Excel文件修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("⚠️ Excel文件不存在")

def check_github_secrets():
    """检查GitHub Secrets配置"""
    print("\n" + "=" * 60)
    print("🔐 GitHub Secrets 配置检查")
    print("=" * 60)
    
    required_secrets = ['LOGIN_URL', 'USERNAME', 'PASSWORD', 'REPORT_URL']
    
    print("必需的环境变量:")
    for secret in required_secrets:
        if os.getenv(secret):
            print(f"✅ {secret}: 已配置")
        else:
            print(f"❌ {secret}: 未配置")
    
    print("\n💡 提示:")
    print("- 这些变量需要在GitHub仓库的Settings > Secrets中配置")
    print("- 本地测试时可以在config.env文件中配置")

def main():
    """主函数"""
    print("🌊 水务数据系统 - GitHub Actions 状态检查")
    print("=" * 60)
    
    # 检查GitHub Actions状态
    check_github_actions_status()
    
    # 检查本地执行状态
    check_local_execution_status()
    
    # 检查Secrets配置
    check_github_secrets()
    
    print("\n" + "=" * 60)
    print("📋 检查完成")
    print("=" * 60)
    
    print("\n💡 使用建议:")
    print("1. 如果定时执行没有运行，检查仓库活跃度")
    print("2. 如果执行失败，查看GitHub Actions日志")
    print("3. 确保所有必需的Secrets都已配置")
    print("4. 定期运行 keep_alive.py 保持仓库活跃")

if __name__ == '__main__':
    main()
