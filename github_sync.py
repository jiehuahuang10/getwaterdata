#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 文件同步工具
用于将 Render 上修改的 Excel 文件自动提交回 GitHub
"""

import os
import subprocess
import datetime
from pathlib import Path

def sync_excel_to_github(excel_file_path, commit_message=None):
    """
    将 Excel 文件同步回 GitHub
    
    参数:
        excel_file_path: Excel 文件的相对路径
        commit_message: 提交信息，如果为None则自动生成
    
    返回:
        dict: {'success': bool, 'message': str}
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(excel_file_path):
            return {
                'success': False,
                'message': f'文件不存在: {excel_file_path}'
            }
        
        # 检查是否在 Git 仓库中
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'message': '当前目录不是 Git 仓库'
            }
        
        # 生成提交信息
        if commit_message is None:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = f'自动更新: {os.path.basename(excel_file_path)} - {timestamp}'
        
        # Git 操作
        commands = [
            ['git', 'config', 'user.email', 'auto-sync@getwaterdata.com'],
            ['git', 'config', 'user.name', 'Auto Sync Bot'],
            ['git', 'add', excel_file_path],
            ['git', 'commit', '-m', commit_message],
        ]
        
        for cmd in commands:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # commit 时如果没有变化，会返回非0，这是正常的
            if result.returncode != 0 and 'nothing to commit' not in result.stdout:
                if 'git commit' in ' '.join(cmd):
                    # 没有变化，跳过
                    continue
                return {
                    'success': False,
                    'message': f'命令执行失败: {" ".join(cmd)}\n{result.stderr}'
                }
        
        # 尝试推送（在 Render 环境中可能需要配置认证）
        push_result = subprocess.run(
            ['git', 'push'],
            capture_output=True,
            text=True
        )
        
        if push_result.returncode != 0:
            return {
                'success': False,
                'message': f'推送失败: {push_result.stderr}\n提示: 需要配置 GitHub 认证'
            }
        
        return {
            'success': True,
            'message': f'成功同步文件到 GitHub: {excel_file_path}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'同步失败: {str(e)}'
        }


def setup_github_credentials(github_token):
    """
    配置 GitHub 认证（使用 Personal Access Token）
    
    参数:
        github_token: GitHub Personal Access Token
    """
    try:
        # 配置 Git 使用 token
        repo_url = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if repo_url.startswith('https://'):
            # 将 https://github.com/user/repo.git 转换为
            # https://token@github.com/user/repo.git
            new_url = repo_url.replace('https://', f'https://{github_token}@')
            subprocess.run(['git', 'remote', 'set-url', 'origin', new_url])
            
            return {
                'success': True,
                'message': 'GitHub 认证配置成功'
            }
        else:
            return {
                'success': False,
                'message': '当前不是 HTTPS 远程仓库'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'配置认证失败: {str(e)}'
        }


if __name__ == '__main__':
    # 测试同步
    excel_files = [
        'excel_exports/石滩供水服务部每日总供水情况.xlsx',
        'excel_exports/石滩区分区计量.xlsx'
    ]
    
    for file_path in excel_files:
        if os.path.exists(file_path):
            print(f'同步文件: {file_path}')
            result = sync_excel_to_github(file_path)
            print(f'结果: {result}')
        else:
            print(f'文件不存在: {file_path}')

