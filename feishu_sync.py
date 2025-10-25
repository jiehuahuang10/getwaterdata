#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文件同步模块
将本地 Excel 文件上传到飞书云空间
"""

import os
import sys
import time
import json
import requests
from pathlib import Path


class FeishuUploader:
    """飞书文件上传器"""
    
    def __init__(self, app_id, app_secret):
        """
        初始化飞书上传器
        
        Args:
            app_id: 飞书应用 ID
            app_secret: 飞书应用 Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.base_url = "https://open.feishu.cn/open-api"
        
    def get_tenant_access_token(self):
        """
        获取 tenant_access_token
        
        Returns:
            str: access_token
        """
        print("=" * 80)
        print("[飞书] 开始获取 tenant_access_token...")
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal/"
        
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') == 0:
                self.tenant_access_token = result.get('tenant_access_token')
                print(f"[飞书] ✅ 成功获取 access_token")
                print(f"[飞书] Token 前10位: {self.tenant_access_token[:10]}...")
                return self.tenant_access_token
            else:
                error_msg = result.get('msg', '未知错误')
                print(f"[飞书] ❌ 获取 token 失败: {error_msg}")
                return None
                
        except requests.RequestException as e:
            print(f"[飞书] ❌ 请求失败: {str(e)}")
            return None
    
    def upload_file_to_feishu(self, file_path, folder_token, file_name=None):
        """
        上传文件到飞书云空间
        
        Args:
            file_path: 本地文件路径
            folder_token: 飞书文件夹 token
            file_name: 上传后的文件名（可选，默认使用原文件名）
            
        Returns:
            dict: {'success': bool, 'message': str, 'file_token': str}
        """
        print("=" * 80)
        print("[飞书] 开始上传文件到飞书云空间...")
        print(f"[飞书] 文件路径: {file_path}")
        print(f"[飞书] 目标文件夹: {folder_token}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': f'文件不存在: {file_path}'
            }
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        if file_name is None:
            file_name = os.path.basename(file_path)
        
        print(f"[飞书] 文件名: {file_name}")
        print(f"[飞书] 文件大小: {file_size / 1024:.2f} KB")
        
        # 检查文件大小（飞书限制 20MB）
        if file_size > 20 * 1024 * 1024:
            return {
                'success': False,
                'message': f'文件过大: {file_size / 1024 / 1024:.2f} MB (最大 20MB)'
            }
        
        # 确保有 access_token
        if not self.tenant_access_token:
            if not self.get_tenant_access_token():
                return {
                    'success': False,
                    'message': '无法获取 access_token'
                }
        
        # 上传文件 API
        url = f"{self.base_url}/drive/v1/files/upload_all"
        
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}"
        }
        
        # 准备表单数据
        form_data = {
            'file_name': (None, file_name),
            'parent_type': (None, 'explorer'),
            'parent_node': (None, folder_token),
            'size': (None, str(file_size))
        }
        
        # 读取文件内容
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                
                print("[飞书] 正在上传文件...")
                response = requests.post(
                    url,
                    headers=headers,
                    data=form_data,
                    files=files,
                    timeout=60
                )
                
                response.raise_for_status()
                result = response.json()
                
                print(f"[飞书] API 响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('code') == 0:
                    file_token = result.get('data', {}).get('file_token', '')
                    print(f"[飞书] ✅ 文件上传成功！")
                    print(f"[飞书] File Token: {file_token}")
                    print("=" * 80)
                    return {
                        'success': True,
                        'message': '文件上传成功',
                        'file_token': file_token
                    }
                else:
                    error_msg = result.get('msg', '未知错误')
                    print(f"[飞书] ❌ 上传失败: {error_msg}")
                    print("=" * 80)
                    return {
                        'success': False,
                        'message': f'上传失败: {error_msg}'
                    }
                    
        except requests.RequestException as e:
            print(f"[飞书] ❌ 请求失败: {str(e)}")
            print("=" * 80)
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }
        except Exception as e:
            print(f"[飞书] ❌ 上传出错: {str(e)}")
            print("=" * 80)
            return {
                'success': False,
                'message': f'上传出错: {str(e)}'
            }
    
    def delete_file(self, file_token):
        """
        删除飞书云空间中的文件
        
        Args:
            file_token: 文件 token
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        print(f"[飞书] 删除文件: {file_token}")
        
        if not self.tenant_access_token:
            if not self.get_tenant_access_token():
                return {'success': False, 'message': '无法获取 access_token'}
        
        url = f"{self.base_url}/drive/v1/files/{file_token}"
        
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}"
        }
        
        try:
            response = requests.delete(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') == 0:
                print(f"[飞书] ✅ 文件删除成功")
                return {'success': True, 'message': '文件删除成功'}
            else:
                error_msg = result.get('msg', '未知错误')
                print(f"[飞书] ❌ 删除失败: {error_msg}")
                return {'success': False, 'message': f'删除失败: {error_msg}'}
                
        except Exception as e:
            print(f"[飞书] ❌ 删除出错: {str(e)}")
            return {'success': False, 'message': f'删除出错: {str(e)}'}


def sync_excel_to_feishu(file_path, folder_token, file_name=None):
    """
    同步 Excel 文件到飞书
    
    Args:
        file_path: Excel 文件路径
        folder_token: 飞书文件夹 token
        file_name: 上传后的文件名（可选）
        
    Returns:
        dict: {'success': bool, 'message': str, 'file_token': str}
    """
    # 从环境变量获取配置
    app_id = os.environ.get('FEISHU_APP_ID')
    app_secret = os.environ.get('FEISHU_APP_SECRET')
    
    if not app_id or not app_secret:
        print("[飞书] ❌ 错误: 未配置飞书应用凭证")
        print("[飞书] 请设置环境变量:")
        print("  - FEISHU_APP_ID")
        print("  - FEISHU_APP_SECRET")
        return {
            'success': False,
            'message': '未配置飞书应用凭证'
        }
    
    print("[飞书] 飞书配置:")
    print(f"  App ID: {app_id}")
    print(f"  App Secret: {app_secret[:10]}...")
    print(f"  Folder Token: {folder_token}")
    
    # 创建上传器
    uploader = FeishuUploader(app_id, app_secret)
    
    # 上传文件（带重试机制）
    max_retries = 3
    for attempt in range(max_retries):
        if attempt > 0:
            print(f"[飞书] 重试 {attempt}/{max_retries}...")
            time.sleep(5)
        
        result = uploader.upload_file_to_feishu(file_path, folder_token, file_name)
        
        if result['success']:
            return result
    
    return {
        'success': False,
        'message': f'上传失败（已重试 {max_retries} 次）'
    }


def main():
    """主函数 - 用于测试"""
    print("飞书文件上传测试")
    print("=" * 80)
    
    # 测试配置
    test_file = "excel_exports/石滩供水服务部每日总供水情况.xlsx"
    folder_token = os.environ.get('FEISHU_FOLDER_TOKEN', 'Tc2AfAy4jlxVh5dB4lAckZRyn8d')
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        sys.exit(1)
    
    # 执行上传
    result = sync_excel_to_feishu(test_file, folder_token)
    
    if result['success']:
        print("\n✅ 测试成功！")
        print(f"文件已上传到飞书: {result['file_token']}")
        sys.exit(0)
    else:
        print(f"\n❌ 测试失败: {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()

