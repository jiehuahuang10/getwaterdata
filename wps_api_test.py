#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS云文档API测试脚本
用于测试与WPS开放平台的连接和基本功能
"""

import requests
import json
import hashlib
import time
from datetime import datetime

class WPSAPIClient:
    def __init__(self, app_id, app_secret=None):
        """
        初始化WPS API客户端
        
        Args:
            app_id (str): WPS应用ID
            app_secret (str): WPS应用密钥（需要从开发者后台获取）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://openapi.wps.cn"
        self.access_token = None
        
    def get_access_token(self):
        """
        获取访问令牌
        实现WPS开放平台的应用授权流程
        """
        if not self.app_secret:
            print("警告: 缺少APP_SECRET，无法获取访问令牌")
            return None
            
        print("正在获取访问令牌...")
        
        # 使用应用授权方式获取access_token
        # 参考: https://open.wps.cn/documents/app-integration-dev/wps365/server/api-description/flow
        
        url = f"{self.base_url}/oauth2/access_token"
        
        # 构建请求参数
        timestamp = str(int(time.time()))
        
        # 构建签名字符串 (根据WPS文档的签名规则)
        sign_string = f"appid={self.app_id}&timestamp={timestamp}&appsecret={self.app_secret}"
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        
        data = {
            "appid": self.app_id,
            "timestamp": timestamp,
            "signature": signature,
            "grant_type": "client_credentials"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(url, data=data, headers=headers, timeout=10)
            print(f"Token请求状态码: {response.status_code}")
            print(f"Token响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if "access_token" in result:
                    token = result["access_token"]
                    print(f"成功获取访问令牌: {token[:20]}...")
                    return token
                else:
                    print(f"响应中未找到access_token: {result}")
                    return None
            else:
                print(f"获取访问令牌失败，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"请求访问令牌时发生错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析响应JSON时发生错误: {e}")
            return None
    
    def search_documents(self, keyword="石滩供水服务部"):
        """
        搜索云文档
        
        Args:
            keyword (str): 搜索关键词
        """
        print(f"搜索关键词: {keyword}")
        
        if not self.access_token:
            print("错误: 需要先获取访问令牌")
            return None
            
        # 使用MCP云文档搜索API
        url = f"{self.base_url}/mcp/kso-yundoc/message"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "tool": "search_yundoc",
            "parameters": {
                "keyword": keyword,
                "page_size": 10,
                "type": "excel"  # 搜索Excel文档
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print("搜索结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"搜索请求失败: {e}")
            return None
    
    def extract_document_content(self, file_id, drive_id):
        """
        提取文档内容
        
        Args:
            file_id (str): 文件ID
            drive_id (str): 驱动器ID
        """
        print(f"提取文档内容: file_id={file_id}, drive_id={drive_id}")
        
        if not self.access_token:
            print("错误: 需要先获取访问令牌")
            return None
            
        url = f"{self.base_url}/mcp/kso-yundoc/message"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "tool": "extract_yundoc_content",
            "parameters": {
                "file_id": file_id,
                "drive_id": drive_id
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print("文档内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"内容提取请求失败: {e}")
            return None
    
    def test_connection(self):
        """
        测试API连接
        """
        print("=" * 50)
        print("WPS云文档API连接测试")
        print("=" * 50)
        print(f"应用ID: {self.app_id}")
        print(f"基础URL: {self.base_url}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 获取访问令牌
        print("步骤1: 获取访问令牌")
        self.access_token = self.get_access_token()
        
        if not self.access_token:
            print("无法获取访问令牌，请检查应用配置")
            print()
            print("需要完成的配置:")
            print("1. 在WPS开发者后台获取APP_SECRET")
            print("2. 确保应用已申请必要的API权限")
            print("3. 配置应用数据权限并通过审核")
            return False
        
        print(f"访问令牌: {self.access_token[:20]}...")
        print()
        
        # 步骤2: 搜索文档
        print("步骤2: 搜索水务文档")
        search_result = self.search_documents("石滩供水服务部每日总供水情况")
        
        if search_result:
            print("搜索成功!")
            # 如果找到文档，尝试提取内容
            # 这里需要根据实际返回的数据结构来解析file_id和drive_id
            print()
            print("步骤3: 提取文档内容")
            print("注意: 需要从搜索结果中获取file_id和drive_id")
        else:
            print("搜索失败或未找到匹配文档")
        
        print()
        print("测试完成!")
        return True

def main():
    """
    主函数 - 运行API测试
    """
    # WPS应用配置
    APP_ID = "AK20251012ADRMHT"  # 您的应用ID
    APP_SECRET = "7166bd504290a908fde5a1d1af37ac00"  # 应用密钥
    
    print("WPS云文档API测试工具")
    print("用于测试水务数据自动化系统与WPS云文档的集成")
    print()
    
    if not APP_SECRET:
        print("警告: 未配置APP_SECRET")
        print("请按以下步骤获取APP_SECRET:")
        print("1. 访问 WPS开发者后台")
        print("2. 进入您的应用详情页面")
        print("3. 查找应用密钥(APP_SECRET)或类似字段")
        print("4. 将获取的密钥填入此脚本的APP_SECRET变量")
        print()
        
        # 询问用户是否要继续测试连接性
        user_input = input("是否继续进行基础连接测试? (y/n): ").lower().strip()
        if user_input != 'y':
            print("测试已取消")
            return
    
    # 创建API客户端
    client = WPSAPIClient(APP_ID, APP_SECRET)
    
    # 运行连接测试
    success = client.test_connection()
    
    if success:
        print("基础测试完成")
    else:
        print("测试失败，请检查配置")
        
    print()
    print("下一步:")
    print("1. 获取完整的应用认证信息")
    print("2. 申请必要的API权限")
    print("3. 实现完整的文档读写功能")
    print("4. 集成到水务数据自动化系统")

if __name__ == "__main__":
    main()
