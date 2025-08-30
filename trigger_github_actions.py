#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动触发GitHub Actions工作流
"""

import requests
import json
import os
from datetime import datetime

def trigger_workflow():
    """手动触发GitHub Actions工作流"""
    
    # GitHub API配置
    repo_owner = "jiehuahuang10"
    repo_name = "getwaterdata"
    workflow_id = "daily-water-data.yml"
    
    # 需要GitHub Personal Access Token
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ 错误: 需要设置GITHUB_TOKEN环境变量")
        print("💡 请创建GitHub Personal Access Token并设置为环境变量")
        return False
    
    # API URL
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
    
    # 请求头
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    # 请求体
    data = {
        'ref': 'main',
        'inputs': {
            'manual_trigger': 'true',
            'trigger_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    try:
        print("🚀 正在触发GitHub Actions工作流...")
        print(f"📅 触发时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 204:
            print("✅ 成功触发GitHub Actions工作流！")
            print("📋 工作流已开始执行")
            print("🔍 查看执行状态: https://github.com/jiehuahuang10/getwaterdata/actions")
            return True
        else:
            print(f"❌ 触发失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def check_workflow_status():
    """检查工作流状态"""
    print("\n" + "=" * 50)
    print("📊 工作流状态检查")
    print("=" * 50)
    
    # 运行状态检查脚本
    try:
        import subprocess
        result = subprocess.run(['python', 'check_github_actions.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
    except Exception as e:
        print(f"❌ 状态检查失败: {str(e)}")

def main():
    """主函数"""
    print("🌊 水务数据系统 - 手动触发GitHub Actions")
    print("=" * 60)
    
    # 触发工作流
    if trigger_workflow():
        print("\n⏳ 等待5秒后检查状态...")
        import time
        time.sleep(5)
        
        # 检查状态
        check_workflow_status()
    else:
        print("\n💡 手动触发指南:")
        print("1. 访问: https://github.com/jiehuahuang10/getwaterdata/actions")
        print("2. 点击 '每日水务数据自动更新'")
        print("3. 点击 'Run workflow' 按钮")
        print("4. 选择分支 'main'")
        print("5. 点击 'Run workflow' 确认")

if __name__ == '__main__':
    main()
