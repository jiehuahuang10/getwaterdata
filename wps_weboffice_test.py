#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS WebOffice API测试
使用新发现的WebOffice平台认证信息
"""

import requests
import json
import hashlib
import time
from datetime import datetime

class WPSWebOfficeAPI:
    def __init__(self, app_id, app_secret):
        """
        初始化WPS WebOffice API客户端
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        
        # WebOffice API基础URL
        self.base_urls = [
            "https://solution.wps.cn",
            "https://api.solution.wps.cn", 
            "https://weboffice.wps.cn",
            "https://api.weboffice.wps.cn"
        ]
        
    def test_weboffice_endpoints(self):
        """
        测试WebOffice API端点
        """
        print("=" * 60)
        print("测试WPS WebOffice API端点")
        print("=" * 60)
        
        # 可能的WebOffice API端点
        endpoints = [
            "/api/v1/files",
            "/api/v1/files/search",
            "/api/files",
            "/api/files/search",
            "/v1/files",
            "/v1/files/search",
            "/files",
            "/files/search",
            "/weboffice/api/v1/files",
            "/weboffice/files"
        ]
        
        working_endpoints = []
        
        for base_url in self.base_urls:
            print(f"基础URL: {base_url}")
            
            # 首先测试基础URL连通性
            try:
                response = self.session.get(base_url, timeout=5)
                print(f"  基础连通性: {response.status_code}")
            except:
                print(f"  基础连通性: 失败")
                continue
            
            for endpoint in endpoints:
                full_url = base_url + endpoint
                print(f"  测试端点: {endpoint}")
                
                # 构建认证头
                headers = {"Content-Type": "application/json"}
                
                # 尝试不同的认证方式
                auth_methods = [
                    {"Authorization": f"Bearer {self.app_secret}"},
                    {"X-App-Id": self.app_id, "X-App-Secret": self.app_secret},
                    {"appid": self.app_id, "appsecret": self.app_secret},
                    {"App-Id": self.app_id, "App-Secret": self.app_secret},
                    {}  # 无认证
                ]
                
                for i, auth_headers in enumerate(auth_methods):
                    request_headers = {**headers, **auth_headers}
                    
                    try:
                        # 尝试GET请求
                        response = self.session.get(full_url, headers=request_headers, timeout=5)
                        
                        if response.status_code not in [404]:
                            print(f"    认证方式{i+1} GET - 状态码: {response.status_code}")
                            
                            if response.status_code not in [405, 500]:
                                print(f"    响应: {response.text[:200]}...")
                                
                                if response.status_code in [200, 201]:
                                    working_endpoints.append((full_url, "GET", i+1))
                                    print(f"    成功!")
                    
                    except requests.exceptions.RequestException:
                        pass
                    
                    # 如果是搜索端点，尝试POST请求
                    if "search" in endpoint:
                        try:
                            search_data = {
                                "keyword": "测试",
                                "limit": 1
                            }
                            
                            response = self.session.post(full_url, json=search_data, headers=request_headers, timeout=5)
                            
                            if response.status_code not in [404]:
                                print(f"    认证方式{i+1} POST - 状态码: {response.status_code}")
                                
                                if response.status_code not in [405, 500]:
                                    print(f"    响应: {response.text[:200]}...")
                                    
                                    if response.status_code in [200, 201]:
                                        working_endpoints.append((full_url, "POST", i+1))
                                        print(f"    搜索成功!")
                        
                        except requests.exceptions.RequestException:
                            pass
            
            print()
        
        return working_endpoints
    
    def test_oauth_endpoints(self):
        """
        测试OAuth认证端点
        """
        print("=" * 60)
        print("测试WebOffice OAuth认证")
        print("=" * 60)
        
        # OAuth端点
        oauth_endpoints = [
            "/oauth2/access_token",
            "/api/oauth2/access_token",
            "/v1/oauth2/access_token",
            "/weboffice/oauth2/access_token"
        ]
        
        working_tokens = []
        
        for base_url in self.base_urls:
            print(f"基础URL: {base_url}")
            
            for endpoint in oauth_endpoints:
                full_url = base_url + endpoint
                print(f"  测试OAuth端点: {endpoint}")
                
                # 构建OAuth请求
                timestamp = str(int(time.time()))
                
                # 不同的OAuth请求格式
                oauth_requests = [
                    {
                        "method": "POST",
                        "data": {
                            "appid": self.app_id,
                            "appsecret": self.app_secret,
                            "grant_type": "client_credentials"
                        },
                        "headers": {"Content-Type": "application/x-www-form-urlencoded"}
                    },
                    {
                        "method": "POST",
                        "json": {
                            "appid": self.app_id,
                            "appsecret": self.app_secret,
                            "grant_type": "client_credentials"
                        },
                        "headers": {"Content-Type": "application/json"}
                    },
                    {
                        "method": "GET",
                        "params": {
                            "appid": self.app_id,
                            "appsecret": self.app_secret,
                            "grant_type": "client_credentials"
                        }
                    }
                ]
                
                for i, oauth_config in enumerate(oauth_requests):
                    try:
                        if oauth_config["method"] == "POST":
                            if "data" in oauth_config:
                                response = self.session.post(
                                    full_url,
                                    data=oauth_config["data"],
                                    headers=oauth_config["headers"],
                                    timeout=10
                                )
                            else:
                                response = self.session.post(
                                    full_url,
                                    json=oauth_config["json"],
                                    headers=oauth_config["headers"],
                                    timeout=10
                                )
                        else:
                            response = self.session.get(
                                full_url,
                                params=oauth_config["params"],
                                timeout=10
                            )
                        
                        print(f"    方法{i+1} - 状态码: {response.status_code}")
                        
                        if response.status_code not in [404, 405]:
                            print(f"    响应: {response.text[:300]}...")
                            
                            if response.status_code == 200:
                                try:
                                    result = response.json()
                                    if "access_token" in result:
                                        working_tokens.append((full_url, result["access_token"]))
                                        print(f"    成功获取access_token!")
                                        return result["access_token"]
                                except:
                                    pass
                    
                    except requests.exceptions.RequestException as e:
                        print(f"    方法{i+1} - 请求失败: {e}")
            
            print()
        
        return None
    
    def run_weboffice_test(self):
        """
        运行WebOffice完整测试
        """
        print("WPS WebOffice API测试")
        print(f"AppID: {self.app_id}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 测试OAuth认证
        print("步骤1: 测试OAuth认证")
        access_token = self.test_oauth_endpoints()
        
        if access_token:
            print(f"成功获取访问令牌: {access_token[:20]}...")
        else:
            print("未获取到访问令牌，继续测试直接API调用")
        print()
        
        # 步骤2: 测试API端点
        print("步骤2: 测试API端点")
        working_endpoints = self.test_weboffice_endpoints()
        
        # 总结结果
        print("=" * 60)
        print("WebOffice测试结果")
        print("=" * 60)
        
        if access_token:
            print(f"OAuth认证: 成功")
        else:
            print(f"OAuth认证: 失败")
        
        if working_endpoints:
            print(f"可用API端点: {len(working_endpoints)} 个")
            for url, method, auth_method in working_endpoints:
                print(f"  - {method} {url} (认证方式{auth_method})")
        else:
            print("可用API端点: 无")
        
        if access_token or working_endpoints:
            print()
            print("成功! 找到了可用的WebOffice API端点!")
            print("可以开始集成到水务数据自动化系统!")
        else:
            print()
            print("需要进一步配置WebOffice应用权限")
        
        return {
            "access_token": access_token,
            "working_endpoints": working_endpoints
        }

def main():
    """
    主函数
    """
    # 使用新的WebOffice认证信息
    APP_ID = "SX20251012DLMWBV"
    APP_SECRET = "jZMlBrLzuESMUHCqEhIUUTbGavuzAsy"
    
    api = WPSWebOfficeAPI(APP_ID, APP_SECRET)
    results = api.run_weboffice_test()
    
    print()
    print("WebOffice测试完成!")

if __name__ == "__main__":
    main()
