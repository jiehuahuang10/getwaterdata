#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书文档API客户端
用于自动更新飞书表格中的水务数据
"""

import requests
import json
import time
from datetime import datetime, timedelta

class FeishuAPIClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.token_expires_at = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json; charset=utf-8'
        })
    
    def get_tenant_access_token(self):
        """
        获取tenant_access_token
        有效期2小时，自动刷新
        """
        # 如果token还在有效期内，直接返回
        if self.tenant_access_token and time.time() < self.token_expires_at:
            remaining = int(self.token_expires_at - time.time())
            print(f"使用缓存的token（剩余{remaining}秒）")
            return self.tenant_access_token
        
        print("正在获取新的tenant_access_token...")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0:
                    self.tenant_access_token = result['tenant_access_token']
                    expires_in = result.get('expire', 7200)  # 默认2小时
                    self.token_expires_at = time.time() + expires_in - 60  # 提前1分钟刷新
                    
                    print(f"Token获取成功！")
                    print(f"有效期: {expires_in}秒 ({expires_in//3600}小时)")
                    
                    return self.tenant_access_token
                else:
                    print(f"错误: {result.get('msg')}")
                    return None
            else:
                print(f"请求失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"获取token出错: {e}")
            return None
    
    def get_spreadsheet_info(self, spreadsheet_token):
        """
        获取表格基本信息
        """
        token = self.get_tenant_access_token()
        if not token:
            return None
        
        url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/metainfo"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0:
                    return result['data']
                else:
                    print(f"获取表格信息失败: {result.get('msg')}")
                    return None
            else:
                print(f"请求失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def read_spreadsheet_data(self, spreadsheet_token, sheet_id, range_notation):
        """
        读取表格数据
        
        参数:
            spreadsheet_token: 表格token（从URL获取）
            sheet_id: 工作表ID
            range_notation: 范围，如 "A1:I100"
        """
        token = self.get_tenant_access_token()
        if not token:
            return None
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_notation}"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "valueRenderOption": "ToString",
            "dateTimeRenderOption": "FormattedString"
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0:
                    return result['data']
                else:
                    print(f"读取失败: {result.get('msg')}")
                    return None
            else:
                print(f"请求失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def write_spreadsheet_data(self, spreadsheet_token, sheet_id, range_notation, values):
        """
        写入表格数据
        
        参数:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID
            range_notation: 范围，如 "A2:I2"
            values: 二维数组，如 [["2025-01-10", "1000", "2000", ...]]
        """
        token = self.get_tenant_access_token()
        if not token:
            return None
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        data = {
            "valueRange": {
                "range": f"{sheet_id}!{range_notation}",
                "values": values
            }
        }
        
        try:
            response = self.session.put(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0:
                    print(f"写入成功！")
                    return result['data']
                else:
                    print(f"写入失败: {result.get('msg')}")
                    return None
            else:
                print(f"请求失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def append_spreadsheet_data(self, spreadsheet_token, sheet_id, values):
        """
        追加数据到表格末尾
        """
        token = self.get_tenant_access_token()
        if not token:
            return None
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        data = {
            "valueRange": {
                "range": f"{sheet_id}!A:I",  # 自动找到末尾追加
                "values": values
            }
        }
        
        try:
            response = self.session.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 0:
                    print(f"追加成功！")
                    return result['data']
                else:
                    print(f"追加失败: {result.get('msg')}")
                    return None
            else:
                print(f"请求失败: {response.text}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def test_connection(self):
        """
        测试API连接
        """
        print("=" * 60)
        print("测试飞书API连接")
        print("=" * 60)
        
        token = self.get_tenant_access_token()
        
        if token:
            print("\n连接测试成功！")
            print(f"App ID: {self.app_id}")
            print(f"Token: {token[:30]}...")
            print("\n您可以开始使用飞书API了！")
            return True
        else:
            print("\n连接测试失败！")
            print("请检查:")
            print("1. App ID是否正确")
            print("2. App Secret是否正确")
            print("3. 网络连接是否正常")
            return False


def main():
    """
    测试脚本
    """
    print("=" * 60)
    print("飞书API客户端测试")
    print("=" * 60)
    
    # 从配置文件加载
    try:
        with open('feishu_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        app_id = config['app_id']
        app_secret = config['app_secret']
        spreadsheet_token = config.get('spreadsheet_token', '')
        
        print(f"App ID: {app_id}")
        print(f"App Secret: {'*' * len(app_secret)}")
        if spreadsheet_token:
            print(f"Spreadsheet Token: {spreadsheet_token}")
        print()
        
    except FileNotFoundError:
        print("错误: 找不到 feishu_config.json 文件")
        print("\n请按以下步骤创建配置文件:")
        print("1. 在飞书开放平台创建应用")
        print("2. 获取App ID和App Secret")
        print("3. 创建 feishu_config.json 文件")
        print("4. 填入配置信息")
        return
    
    # 创建客户端
    client = FeishuAPIClient(app_id, app_secret)
    
    # 测试连接
    if client.test_connection():
        print("\n" + "=" * 60)
        print("测试成功！现在可以使用飞书API了！")
        print("=" * 60)
        
        # 如果有spreadsheet_token，测试表格操作
        if spreadsheet_token:
            print("\n正在测试表格访问...")
            info = client.get_spreadsheet_info(spreadsheet_token)
            if info:
                print(f"表格名称: {info['properties']['title']}")
                print(f"工作表数量: {len(info['sheets'])}")
                print("表格访问成功！")
    else:
        print("\n" + "=" * 60)
        print("测试失败！请检查配置")
        print("=" * 60)


if __name__ == "__main__":
    main()

