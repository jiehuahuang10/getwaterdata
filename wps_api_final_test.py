#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS API最终测试
基于探索结果，测试正确的API调用方式
"""

import requests
import json
import hashlib
import time
from datetime import datetime

class WPSAPIFinalTest:
    def __init__(self, app_id, app_secret):
        """
        初始化最终测试
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        
        # 基于探索结果，使用正确的API域名
        self.api_base = "https://openapi.wps.cn"  # 真正的API域名
        self.web_base = "https://open.wps.cn"     # 网页域名
        
    def test_correct_api_domain(self):
        """
        测试正确的API域名和端点
        """
        print("=" * 60)
        print("测试正确的API域名")
        print("=" * 60)
        
        # 可能的正确API端点
        api_endpoints = [
            f"{self.api_base}/v1/3rd-app/access_token",
            f"{self.api_base}/oauth2/access_token",
            f"{self.api_base}/api/oauth2/access_token",
            f"{self.api_base}/v1/oauth2/access_token"
        ]
        
        for endpoint in api_endpoints:
            print(f"测试认证端点: {endpoint}")
            
            # 构建正确的认证请求
            timestamp = str(int(time.time()))
            
            # 尝试不同的签名和请求方式
            methods = [
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
            
            for i, method_config in enumerate(methods):
                try:
                    if method_config["method"] == "POST":
                        if "data" in method_config:
                            response = self.session.post(
                                endpoint, 
                                data=method_config["data"],
                                headers=method_config["headers"],
                                timeout=10
                            )
                        else:
                            response = self.session.post(
                                endpoint,
                                json=method_config["json"], 
                                headers=method_config["headers"],
                                timeout=10
                            )
                    else:
                        response = self.session.get(
                            endpoint,
                            params=method_config["params"],
                            timeout=10
                        )
                    
                    print(f"  方法{i+1} ({method_config['method']}) - 状态码: {response.status_code}")
                    
                    if response.status_code not in [404, 405]:
                        print(f"  响应: {response.text[:300]}...")
                        
                        if response.status_code == 200:
                            try:
                                result = response.json()
                                if "access_token" in result:
                                    print(f"  成功获取access_token: {result['access_token'][:20]}...")
                                    return result["access_token"]
                            except:
                                pass
                
                except requests.exceptions.RequestException as e:
                    print(f"  方法{i+1} - 请求失败: {e}")
            
            print()
        
        return None
    
    def test_direct_file_api(self, access_token=None):
        """
        测试直接的文件API调用
        """
        print("=" * 60)
        print("测试直接文件API调用")
        print("=" * 60)
        
        # 可能的文件API端点
        file_endpoints = [
            f"{self.api_base}/v1/files",
            f"{self.api_base}/v1/drives/files",
            f"{self.api_base}/api/v1/files",
            f"{self.api_base}/files"
        ]
        
        for endpoint in file_endpoints:
            print(f"测试文件端点: {endpoint}")
            
            # 构建请求头
            headers = {"Content-Type": "application/json"}
            
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            else:
                # 尝试直接使用应用凭证
                headers.update({
                    "X-App-Id": self.app_id,
                    "X-App-Secret": self.app_secret
                })
            
            try:
                # 尝试GET请求获取文件列表
                response = self.session.get(endpoint, headers=headers, timeout=10)
                print(f"  GET - 状态码: {response.status_code}")
                
                if response.status_code not in [404, 405]:
                    print(f"  响应: {response.text[:300]}...")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            print(f"  成功获取文件数据!")
                            return result
                        except:
                            pass
            
            except requests.exceptions.RequestException as e:
                print(f"  GET请求失败: {e}")
            
            print()
        
        return None
    
    def test_search_api(self, access_token=None):
        """
        测试搜索API
        """
        print("=" * 60)
        print("测试搜索API")
        print("=" * 60)
        
        # 搜索端点
        search_endpoints = [
            f"{self.api_base}/v1/files/search",
            f"{self.api_base}/v1/search/files",
            f"{self.api_base}/api/v1/files/search",
            f"{self.api_base}/search"
        ]
        
        for endpoint in search_endpoints:
            print(f"测试搜索端点: {endpoint}")
            
            # 构建搜索请求
            search_data = {
                "keyword": "石滩供水服务部",
                "type": "excel",
                "limit": 10
            }
            
            headers = {"Content-Type": "application/json"}
            
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            else:
                headers.update({
                    "X-App-Id": self.app_id,
                    "X-App-Secret": self.app_secret
                })
            
            # 尝试不同的请求方法
            methods = [
                ("GET", {"params": search_data}),
                ("POST", {"json": search_data})
            ]
            
            for method, kwargs in methods:
                try:
                    if method == "GET":
                        response = self.session.get(endpoint, headers=headers, **kwargs, timeout=10)
                    else:
                        response = self.session.post(endpoint, headers=headers, **kwargs, timeout=10)
                    
                    print(f"  {method} - 状态码: {response.status_code}")
                    
                    if response.status_code not in [404, 405]:
                        print(f"  响应: {response.text[:300]}...")
                        
                        if response.status_code == 200:
                            try:
                                result = response.json()
                                print(f"  搜索成功!")
                                if "files" in result or "data" in result:
                                    return result
                            except:
                                pass
                
                except requests.exceptions.RequestException as e:
                    print(f"  {method}请求失败: {e}")
            
            print()
        
        return None
    
    def run_final_test(self):
        """
        运行最终测试
        """
        print("WPS API最终测试")
        print(f"应用ID: {self.app_id}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 获取正确的access_token
        print("步骤1: 获取访问令牌")
        access_token = self.test_correct_api_domain()
        
        if access_token:
            print(f"成功获取访问令牌!")
        else:
            print("未能获取访问令牌，尝试无认证调用")
        print()
        
        # 步骤2: 测试文件API
        print("步骤2: 测试文件API")
        file_result = self.test_direct_file_api(access_token)
        
        if file_result:
            print("文件API调用成功!")
        else:
            print("文件API调用失败")
        print()
        
        # 步骤3: 测试搜索API
        print("步骤3: 测试搜索API")
        search_result = self.test_search_api(access_token)
        
        if search_result:
            print("搜索API调用成功!")
            print("找到的文档:")
            print(json.dumps(search_result, indent=2, ensure_ascii=False))
        else:
            print("搜索API调用失败")
        print()
        
        # 总结
        print("=" * 60)
        print("最终测试结果")
        print("=" * 60)
        
        if access_token:
            print(f"访问令牌: 成功获取")
        else:
            print(f"访问令牌: 获取失败")
        
        if file_result:
            print(f"文件API: 调用成功")
        else:
            print(f"文件API: 调用失败")
        
        if search_result:
            print(f"搜索API: 调用成功")
            print("下一步: 可以开始集成到水务数据系统")
        else:
            print(f"搜索API: 调用失败")
            print("建议: 检查应用权限配置和数据权限审核状态")
        
        return {
            "access_token": access_token,
            "file_api": file_result,
            "search_api": search_result
        }

def main():
    """
    主函数
    """
    APP_ID = "AK20251012ADRMHT"
    APP_SECRET = "7166bd504290a908fde5a1d1af37ac00"
    
    tester = WPSAPIFinalTest(APP_ID, APP_SECRET)
    results = tester.run_final_test()
    
    print()
    print("测试完成!")
    
    if any(results.values()):
        print("找到了可用的API端点，可以开始实际集成!")
    else:
        print("需要进一步配置应用权限或寻找正确的API文档")

if __name__ == "__main__":
    main()
