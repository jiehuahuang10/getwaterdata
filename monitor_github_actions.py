#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 监控脚本
定期检查工作流执行状态，发现异常时发送通知
"""

import requests
import json
from datetime import datetime, timedelta
import os

def check_github_actions_status():
    """检查GitHub Actions最近的执行状态"""
    
    # GitHub API配置
    repo_owner = "jiehuahuang10"  # 替换为您的GitHub用户名
    repo_name = "getwaterdata"    # 替换为您的仓库名
    
    # GitHub API URL
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs"
    
    try:
        # 获取最近的工作流执行记录
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        runs = data.get('workflow_runs', [])
        
        if not runs:
            print("❌ 没有找到工作流执行记录")
            return False
        
        # 检查最近3次执行
        recent_runs = runs[:3]
        success_count = 0
        
        print(f"📊 检查最近{len(recent_runs)}次执行:")
        
        for run in recent_runs:
            status = run.get('status')
            conclusion = run.get('conclusion')
            created_at = run.get('created_at')
            workflow_name = run.get('name')
            
            # 转换时间格式
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            beijing_time = created_time + timedelta(hours=8)
            
            print(f"  - {workflow_name}")
            print(f"    时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    状态: {status} / {conclusion}")
            
            if conclusion == 'success':
                success_count += 1
        
        # 判断健康状态
        if success_count >= 2:
            print("✅ GitHub Actions运行状态良好")
            return True
        else:
            print("⚠️ GitHub Actions可能存在问题，建议检查")
            return False
            
    except Exception as e:
        print(f"❌ 检查GitHub Actions状态失败: {e}")
        return False

def check_last_execution_time():
    """检查最后一次成功执行的时间"""
    try:
        if os.path.exists('last_execution_summary.json'):
            with open('last_execution_summary.json', 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            last_time = summary.get('execution_time')
            if last_time:
                last_datetime = datetime.fromisoformat(last_time)
                now = datetime.now()
                hours_diff = (now - last_datetime).total_seconds() / 3600
                
                print(f"📅 最后执行时间: {last_time}")
                print(f"⏰ 距离现在: {hours_diff:.1f} 小时")
                
                if hours_diff > 26:  # 超过26小时未执行
                    print("⚠️ 超过26小时未执行，可能需要检查")
                    return False
                else:
                    print("✅ 执行时间正常")
                    return True
        else:
            print("📝 未找到执行摘要文件")
            return False
            
    except Exception as e:
        print(f"❌ 检查执行时间失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 开始监控GitHub Actions状态...")
    print("=" * 50)
    
    # 检查GitHub Actions状态
    actions_ok = check_github_actions_status()
    print()
    
    # 检查本地执行时间
    time_ok = check_last_execution_time()
    print()
    
    # 总结
    if actions_ok and time_ok:
        print("🎉 系统运行正常！")
    else:
        print("⚠️ 发现潜在问题，建议进一步检查")
    
    print("=" * 50)
    print(f"检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
