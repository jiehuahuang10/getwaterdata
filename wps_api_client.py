#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS开放平台API客户端
使用您的AppID和AppSecret进行认证
"""

import requests
import json
import time
from datetime import datetime

class WPSAPIClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WaterDataAutomation/1.0',
            'Content-Type': 'application/json'
        })
    
    def get_access_token(self):
        """
        获取访问令牌（Access Token）
        Token有效期通常为2小时，会自动刷新
        """
        # 如果token还在有效期内，直接返回
        if self.access_token and time.time() < self.token_expires_at:
            print(f"使用缓存的token（剩余{int(self.token_expires_at - time.time())}秒）")
            return self.access_token
        
        print("正在获取新的access_token...")
        
        # WPS开放平台的token获取端点
        url = "https://open.wps.cn/api/v3/auth/token"
        
        # 请求参数
        data = {
            "grant_type": "client_credentials",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            
            print(f"Token请求状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if 'access_token' in result:
                    self.access_token = result['access_token']
                    expires_in = result.get('expires_in', 7200)  # 默认2小时
                    self.token_expires_at = time.time() + expires_in - 60  # 提前1分钟刷新
                    
                    print(f"Token获取成功！")
                    print(f"有效期: {expires_in}秒 ({expires_in//3600}小时)")
                    print(f"Token: {self.access_token[:20]}...")
                    
                    return self.access_token
                else:
                    print(f"错误: {result}")
                    return None
            else:
                print(f"请求失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"获取token出错: {e}")
            return None
    
    def test_connection(self):
        """
        测试API连接
        """
        print("=" * 60)
        print("测试WPS API连接")
        print("=" * 60)
        
        token = self.get_access_token()
        
        if token:
            print("\n连接测试成功！")
            print(f"AppID: {self.app_id}")
            print(f"Token: {token[:30]}...")
            print("\n您可以开始使用WPS API了！")
            return True
        else:
            print("\n连接测试失败！")
            print("请检查:")
            print("1. AppID是否正确")
            print("2. AppSecret是否正确")
            print("3. 网络连接是否正常")
            return False
    
    def get_file_list(self):
        """
        获取文件列表（示例）
        """
        token = self.get_access_token()
        
        if not token:
            return None
        
        # 这是示例端点，实际API请查看官方文档
        url = "https://open.wps.cn/api/v3/files"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取文件列表失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def get_spreadsheet_data(self, file_id, sheet_range):
        """
        读取表格数据（示例）
        
        参数:
            file_id: 文件ID
            sheet_range: 单元格范围，如 "Sheet1!A1:B10"
        """
        token = self.get_access_token()
        
        if not token:
            return None
        
        # 这是示例端点，实际API请查看官方文档
        url = f"https://open.wps.cn/api/v3/spreadsheet/{file_id}/values"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "range": sheet_range
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"读取表格失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def write_spreadsheet_data(self, file_id, sheet_range, values):
        """
        写入表格数据（示例）
        
        参数:
            file_id: 文件ID
            sheet_range: 单元格范围，如 "Sheet1!A1:B10"
            values: 二维数组，如 [["日期", "用水量"], ["2025-01-10", "1000"]]
        """
        token = self.get_access_token()
        
        if not token:
            return None
        
        # 这是示例端点，实际API请查看官方文档
        url = f"https://open.wps.cn/api/v3/spreadsheet/{file_id}/values"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        data = {
            "range": sheet_range,
            "values": values
        }
        
        try:
            response = self.session.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"写入表格失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None


def main():
    """
    测试脚本
    """
    print("=" * 60)
    print("WPS API客户端测试")
    print("=" * 60)
    
    # 从配置文件加载
    try:
        with open('wps_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        app_id = config['app_id']
        app_secret = config['app_secret']
        
        print(f"AppID: {app_id}")
        print(f"AppSecret: {'*' * len(app_secret)}")
        print()
        
    except FileNotFoundError:
        print("错误: 找不到 wps_config.json 文件")
        print("\n请按以下步骤创建配置文件:")
        print("1. 复制 wps_config.json.example 为 wps_config.json")
        print("2. 在WPS开放平台获取AppSecret")
        print("3. 将AppSecret填入 wps_config.json")
        return
    
    # 创建客户端
    client = WPSAPIClient(app_id, app_secret)
    
    # 测试连接
    if client.test_connection():
        print("\n" + "=" * 60)
        print("测试成功！现在可以使用WPS API了！")
        print("=" * 60)
        
        # 可以继续测试其他API
        # files = client.get_file_list()
        # print(f"文件列表: {files}")
    else:
        print("\n" + "=" * 60)
        print("测试失败！请检查配置")
        print("=" * 60)


if __name__ == "__main__":
    main()

