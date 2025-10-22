#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金山文档API客户端
用于自动更新在线Excel文档
"""

import requests
import json
import time
from datetime import datetime
import os
from urllib.parse import urlencode

class KDocsAPIClient:
    """金山文档API客户端"""
    
    def __init__(self, app_id=None, app_secret=None):
        """
        初始化API客户端
        
        Args:
            app_id: 应用ID
            app_secret: 应用密钥
        """
        self.app_id = app_id or os.environ.get('KDOCS_APP_ID')
        self.app_secret = app_secret or os.environ.get('KDOCS_APP_SECRET')
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # API基础URL
        self.base_url = "https://developer.kdocs.cn"
        self.api_base = f"{self.base_url}/api/v3"
        
        # 会话对象
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WaterDataAutomation/1.0',
            'Content-Type': 'application/json'
        })
    
    def get_authorization_url(self, redirect_uri, state=None):
        """
        获取OAuth授权URL
        
        Args:
            redirect_uri: 回调地址
            state: 状态参数
            
        Returns:
            str: 授权URL
        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'read write'
        }
        
        if state:
            params['state'] = state
            
        auth_url = f"{self.base_url}/oauth2/authorize?" + urlencode(params)
        return auth_url
    
    def get_access_token(self, code, redirect_uri):
        """
        通过授权码获取访问令牌
        
        Args:
            code: 授权码
            redirect_uri: 回调地址
            
        Returns:
            bool: 是否成功获取令牌
        """
        try:
            url = f"{self.api_base}/oauth2/token"
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            if token_data.get('code') == 0:
                result = token_data.get('result', {})
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                
                # 计算过期时间 (24小时)
                expires_in = result.get('expires_in', 86400)
                self.token_expires_at = time.time() + expires_in
                
                # 更新请求头
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                
                print(f"成功获取访问令牌，有效期至: {datetime.fromtimestamp(self.token_expires_at)}")
                return True
            else:
                print(f"获取访问令牌失败: {token_data.get('msg')}")
                return False
                
        except Exception as e:
            print(f"获取访问令牌异常: {e}")
            return False
    
    def refresh_access_token(self):
        """
        刷新访问令牌
        
        Returns:
            bool: 是否成功刷新
        """
        if not self.refresh_token:
            print("没有refresh_token，无法刷新")
            return False
            
        try:
            url = f"{self.api_base}/oauth2/token"
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            if token_data.get('code') == 0:
                result = token_data.get('result', {})
                self.access_token = result.get('access_token')
                
                # 更新过期时间
                expires_in = result.get('expires_in', 86400)
                self.token_expires_at = time.time() + expires_in
                
                # 更新请求头
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                
                print(f"成功刷新访问令牌，有效期至: {datetime.fromtimestamp(self.token_expires_at)}")
                return True
            else:
                print(f"刷新访问令牌失败: {token_data.get('msg')}")
                return False
                
        except Exception as e:
            print(f"刷新访问令牌异常: {e}")
            return False
    
    def check_token_validity(self):
        """
        检查令牌是否有效，如需要则自动刷新
        
        Returns:
            bool: 令牌是否有效
        """
        if not self.access_token:
            print("没有访问令牌")
            return False
            
        # 提前5分钟刷新令牌
        if self.token_expires_at and time.time() > (self.token_expires_at - 300):
            print("访问令牌即将过期，尝试刷新...")
            return self.refresh_access_token()
            
        return True
    
    def get_file_info(self, file_id):
        """
        获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            dict: 文件信息
        """
        if not self.check_token_validity():
            return None
            
        try:
            url = f"{self.api_base}/files/{file_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                return result.get('result')
            else:
                print(f"获取文件信息失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"获取文件信息异常: {e}")
            return None
    
    def get_sheet_data(self, file_id, sheet_id=None, range_str=None):
        """
        获取表格数据
        
        Args:
            file_id: 文件ID
            sheet_id: 工作表ID (可选)
            range_str: 数据范围，如 "A1:Z100" (可选)
            
        Returns:
            dict: 表格数据
        """
        if not self.check_token_validity():
            return None
            
        try:
            url = f"{self.api_base}/files/{file_id}/sheets"
            if sheet_id:
                url += f"/{sheet_id}"
            url += "/values"
            
            params = {}
            if range_str:
                params['range'] = range_str
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                return result.get('result')
            else:
                print(f"获取表格数据失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"获取表格数据异常: {e}")
            return None
    
    def update_sheet_data(self, file_id, sheet_id, range_str, values):
        """
        更新表格数据
        
        Args:
            file_id: 文件ID
            sheet_id: 工作表ID
            range_str: 数据范围，如 "A1:Z100"
            values: 要更新的数据 (二维数组)
            
        Returns:
            bool: 是否更新成功
        """
        if not self.check_token_validity():
            return False
            
        try:
            url = f"{self.api_base}/files/{file_id}/sheets/{sheet_id}/values"
            
            data = {
                'range': range_str,
                'values': values,
                'valueInputOption': 'RAW'  # 原始值输入
            }
            
            response = self.session.put(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                print(f"成功更新表格数据: {range_str}")
                return True
            else:
                print(f"更新表格数据失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            print(f"更新表格数据异常: {e}")
            return False
    
    def append_sheet_data(self, file_id, sheet_id, values):
        """
        在表格末尾追加数据
        
        Args:
            file_id: 文件ID
            sheet_id: 工作表ID
            values: 要追加的数据 (二维数组)
            
        Returns:
            bool: 是否追加成功
        """
        if not self.check_token_validity():
            return False
            
        try:
            url = f"{self.api_base}/files/{file_id}/sheets/{sheet_id}/values:append"
            
            data = {
                'values': values,
                'valueInputOption': 'RAW'
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                print(f"成功追加表格数据")
                return True
            else:
                print(f"追加表格数据失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            print(f"追加表格数据异常: {e}")
            return False
    
    def save_tokens(self, file_path='kdocs_tokens.json'):
        """
        保存令牌到文件
        
        Args:
            file_path: 保存文件路径
        """
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at,
            'saved_at': time.time()
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, indent=2)
            print(f"令牌已保存到: {file_path}")
        except Exception as e:
            print(f"保存令牌失败: {e}")
    
    def load_tokens(self, file_path='kdocs_tokens.json'):
        """
        从文件加载令牌
        
        Args:
            file_path: 令牌文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            if not os.path.exists(file_path):
                print(f"令牌文件不存在: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.token_expires_at = token_data.get('expires_at')
            
            if self.access_token:
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                print(f"成功加载令牌，有效期至: {datetime.fromtimestamp(self.token_expires_at)}")
                return True
            else:
                print("令牌文件中没有有效的访问令牌")
                return False
                
        except Exception as e:
            print(f"加载令牌失败: {e}")
            return False


def extract_file_id_from_url(url):
    """
    从金山文档URL中提取文件ID
    
    Args:
        url: 金山文档URL，如 https://www.kdocs.cn/l/ctPsso05tvI4
        
    Returns:
        str: 文件ID
    """
    if '/l/' in url:
        return url.split('/l/')[-1].split('?')[0]
    return None


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = KDocsAPIClient()
    
    # 从URL提取文件ID
    file_url = "https://www.kdocs.cn/l/ctPsso05tvI4"
    file_id = extract_file_id_from_url(file_url)
    print(f"文件ID: {file_id}")
    
    # 加载已保存的令牌
    if client.load_tokens():
        # 获取文件信息
        file_info = client.get_file_info(file_id)
        if file_info:
            print(f"文件名: {file_info.get('name')}")
            print(f"文件类型: {file_info.get('type')}")
    else:
        print("需要先进行OAuth授权获取访问令牌")
        print("授权URL:", client.get_authorization_url("http://localhost:5000/callback"))
