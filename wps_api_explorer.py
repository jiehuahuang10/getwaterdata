#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS API探索器
测试不同的API端点和认证方式，找到正确的集成方法
"""

import requests
import json
import hashlib
import time
from datetime import datetime

class WPSAPIExplorer:
    def __init__(self, app_id, app_secret):
        """
        初始化WPS API探索器
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        
        # 可能的API基础URL
        self.base_urls = [
            "https://openapi.wps.cn",
            "https://open.wps.cn",
            "https://api.wps.cn",
            "https://www.wps.cn/api"
        ]
        
        # 可能的认证端点
        self.auth_endpoints = [
            "/oauth2/access_token",
            "/oauth/access_token", 
            "/api/oauth2/access_token",
            "/v1/oauth2/access_token",
            "/auth/access_token"
        ]
        
        # 可能的MCP端点
        self.mcp_endpoints = [
            "/mcp/kso-yundoc/message",
            "/api/mcp/kso-yundoc/message",
            "/v1/mcp/kso-yundoc/message"
        ]
    
    def test_base_urls(self):
        """
        测试不同的基础URL
        """
        print("=" * 60)
        print("测试基础URL连通性")
        print("=" * 60)
        
        working_urls = []
        
        for base_url in self.base_urls:
            print(f"测试: {base_url}")
            try:
                response = self.session.get(base_url, timeout=5)
                print(f"  状态码: {response.status_code}")
                print(f"  响应长度: {len(response.text)} 字符")
                
                if response.status_code in [200, 301, 302, 403]:  # 403可能表示需要认证
                    working_urls.append(base_url)
                    print(f"  可访问")
                else:
                    print(f"  不可访问")
                    
            except requests.exceptions.RequestException as e:
                print(f"  连接失败: {e}")
            
            print()
        
        return working_urls
    
    def test_auth_endpoints(self, base_urls):
        """
        测试不同的认证端点
        """
        print("=" * 60)
        print("测试认证端点")
        print("=" * 60)
        
        working_auth = []
        
        for base_url in base_urls:
            print(f"基础URL: {base_url}")
            
            for auth_endpoint in self.auth_endpoints:
                full_url = base_url + auth_endpoint
                print(f"  测试认证端点: {auth_endpoint}")
                
                # 构建认证请求
                timestamp = str(int(time.time()))
                
                # 尝试不同的签名方式
                sign_methods = [
                    f"appid={self.app_id}&timestamp={timestamp}&appsecret={self.app_secret}",
                    f"{self.app_id}{timestamp}{self.app_secret}",
                    f"appid={self.app_id}&appsecret={self.app_secret}&timestamp={timestamp}"
                ]
                
                for i, sign_string in enumerate(sign_methods):
                    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
                    
                    data = {
                        "appid": self.app_id,
                        "timestamp": timestamp,
                        "signature": signature,
                        "grant_type": "client_credentials"
                    }
                    
                    try:
                        response = self.session.post(full_url, data=data, timeout=5)
                        print(f"    签名方式{i+1} - 状态码: {response.status_code}")
                        
                        if response.status_code != 404:
                            print(f"    响应: {response.text[:200]}...")
                            
                            if response.status_code == 200:
                                try:
                                    result = response.json()
                                    if "access_token" in result:
                                        working_auth.append((full_url, i+1, result["access_token"]))
                                        print(f"    成功获取token!")
                                except:
                                    pass
                        
                    except requests.exceptions.RequestException as e:
                        print(f"    签名方式{i+1} - 请求失败: {e}")
                
                print()
        
        return working_auth
    
    def test_mcp_endpoints(self, base_urls, access_token=None):
        """
        测试MCP云文档端点
        """
        print("=" * 60)
        print("测试MCP云文档端点")
        print("=" * 60)
        
        working_mcp = []
        
        for base_url in base_urls:
            print(f"基础URL: {base_url}")
            
            for mcp_endpoint in self.mcp_endpoints:
                full_url = base_url + mcp_endpoint
                print(f"  测试MCP端点: {mcp_endpoint}")
                
                # 构建MCP请求
                payload = {
                    "tool": "search_yundoc",
                    "parameters": {
                        "keyword": "测试",
                        "page_size": 1
                    }
                }
                
                # 尝试不同的认证方式
                auth_methods = []
                
                if access_token:
                    auth_methods.append({"Authorization": f"Bearer {access_token}"})
                
                auth_methods.extend([
                    {"X-App-Id": self.app_id, "X-App-Secret": self.app_secret},
                    {"appid": self.app_id, "appsecret": self.app_secret},
                    {}  # 无认证
                ])
                
                for i, headers in enumerate(auth_methods):
                    headers.update({"Content-Type": "application/json"})
                    
                    try:
                        response = self.session.post(full_url, json=payload, headers=headers, timeout=5)
                        print(f"    认证方式{i+1} - 状态码: {response.status_code}")
                        
                        if response.status_code != 404:
                            print(f"    响应: {response.text[:200]}...")
                            
                            if response.status_code in [200, 201]:
                                working_mcp.append((full_url, i+1))
                                print(f"    MCP端点可用!")
                        
                    except requests.exceptions.RequestException as e:
                        print(f"    认证方式{i+1} - 请求失败: {e}")
                
                print()
        
        return working_mcp
    
    def test_direct_api_endpoints(self, base_urls, access_token=None):
        """
        测试直接的云文档API端点
        """
        print("=" * 60)
        print("测试直接云文档API端点")
        print("=" * 60)
        
        # 可能的云文档API端点
        api_endpoints = [
            "/v1/files/search",
            "/api/v1/files/search", 
            "/files/search",
            "/drive/files/search",
            "/yundoc/search",
            "/kso/files/search"
        ]
        
        working_apis = []
        
        for base_url in base_urls:
            print(f"基础URL: {base_url}")
            
            for api_endpoint in api_endpoints:
                full_url = base_url + api_endpoint
                print(f"  测试API端点: {api_endpoint}")
                
                # 构建搜索请求
                params = {
                    "keyword": "测试",
                    "limit": 1
                }
                
                # 尝试不同的认证方式
                auth_methods = []
                
                if access_token:
                    auth_methods.append({"Authorization": f"Bearer {access_token}"})
                
                auth_methods.extend([
                    {"X-App-Id": self.app_id, "X-App-Secret": self.app_secret},
                    {"appid": self.app_id, "appsecret": self.app_secret},
                    {}  # 无认证
                ])
                
                for i, headers in enumerate(auth_methods):
                    try:
                        response = self.session.get(full_url, params=params, headers=headers, timeout=5)
                        print(f"    认证方式{i+1} - 状态码: {response.status_code}")
                        
                        if response.status_code != 404:
                            print(f"    响应: {response.text[:200]}...")
                            
                            if response.status_code in [200, 201]:
                                working_apis.append((full_url, i+1))
                                print(f"    API端点可用!")
                        
                    except requests.exceptions.RequestException as e:
                        print(f"    认证方式{i+1} - 请求失败: {e}")
                
                print()
        
        return working_apis
    
    def run_full_exploration(self):
        """
        运行完整的API探索
        """
        print("WPS API探索器")
        print(f"应用ID: {self.app_id}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 测试基础URL
        working_urls = self.test_base_urls()
        
        if not working_urls:
            print("没有找到可用的基础URL")
            return
        
        print(f"找到 {len(working_urls)} 个可用的基础URL")
        print()
        
        # 步骤2: 测试认证端点
        working_auth = self.test_auth_endpoints(working_urls)
        
        access_token = None
        if working_auth:
            print(f"找到 {len(working_auth)} 个可用的认证端点")
            access_token = working_auth[0][2]  # 使用第一个可用的token
        else:
            print("没有找到可用的认证端点，将尝试无认证访问")
        print()
        
        # 步骤3: 测试MCP端点
        working_mcp = self.test_mcp_endpoints(working_urls, access_token)
        
        if working_mcp:
            print(f"找到 {len(working_mcp)} 个可用的MCP端点")
        else:
            print("没有找到可用的MCP端点")
        print()
        
        # 步骤4: 测试直接API端点
        working_apis = self.test_direct_api_endpoints(working_urls, access_token)
        
        if working_apis:
            print(f"找到 {len(working_apis)} 个可用的API端点")
        else:
            print("没有找到可用的直接API端点")
        print()
        
        # 总结
        print("=" * 60)
        print("探索结果总结")
        print("=" * 60)
        
        if working_auth:
            print("可用的认证端点:")
            for url, method, token in working_auth:
                print(f"  - {url} (签名方式{method})")
        
        if working_mcp:
            print("可用的MCP端点:")
            for url, method in working_mcp:
                print(f"  - {url} (认证方式{method})")
        
        if working_apis:
            print("可用的API端点:")
            for url, method in working_apis:
                print(f"  - {url} (认证方式{method})")
        
        if not (working_auth or working_mcp or working_apis):
            print("没有找到任何可用的API端点")
            print()
            print("可能的原因:")
            print("1. 应用权限未审核通过")
            print("2. 需要配置数据权限")
            print("3. API端点已变更")
            print("4. 需要不同的认证方式")
        
        return {
            "base_urls": working_urls,
            "auth_endpoints": working_auth,
            "mcp_endpoints": working_mcp,
            "api_endpoints": working_apis
        }

def main():
    """
    主函数
    """
    APP_ID = "AK20251012ADRMHT"
    APP_SECRET = "7166bd504290a908fde5a1d1af37ac00"
    
    explorer = WPSAPIExplorer(APP_ID, APP_SECRET)
    results = explorer.run_full_exploration()
    
    print()
    print("探索完成！")
    print("基于结果，我们可以确定正确的集成方式。")

if __name__ == "__main__":
    main()
