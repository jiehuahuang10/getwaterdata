#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs文档操作测试
尝试使用WPS WebOffice认证信息操作KDocs在线文档
"""

import requests
import json
import time
from datetime import datetime

class KDocsAPITest:
    def __init__(self, app_id, app_secret):
        """
        初始化KDocs API测试客户端
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.session = requests.Session()
        
        # 目标KDocs文档信息
        self.kdocs_url = "https://www.kdocs.cn/l/ctPsso05tvI4"
        self.doc_id = "ctPsso05tvI4"  # 从URL提取的文档ID
        
        # 可能的API基础URL
        self.api_bases = [
            "https://api.kdocs.cn",
            "https://open.kdocs.cn", 
            "https://kdocs.cn/api",
            "https://www.kdocs.cn/api",
            "https://solution.wps.cn/api/kdocs",
            "https://api.wps.cn/kdocs"
        ]
        
    def test_document_access(self):
        """
        测试文档访问的各种方式
        """
        print("=" * 60)
        print("测试KDocs文档访问")
        print("=" * 60)
        
        # 方法1: 直接访问文档URL
        print("方法1: 直接访问文档URL")
        try:
            response = self.session.get(self.kdocs_url, timeout=10)
            print(f"  状态码: {response.status_code}")
            print(f"  内容长度: {len(response.text)}")
            
            # 查找可能的API端点信息
            content = response.text.lower()
            if "api" in content:
                print("  发现API相关信息")
            if "token" in content:
                print("  发现token相关信息")
                
        except Exception as e:
            print(f"  访问失败: {e}")
        
        print()
        
        # 方法2: 尝试提取文档元数据
        print("方法2: 尝试提取文档元数据")
        metadata_urls = [
            f"https://www.kdocs.cn/api/v1/docs/{self.doc_id}",
            f"https://api.kdocs.cn/v1/docs/{self.doc_id}",
            f"https://kdocs.cn/api/docs/{self.doc_id}/info"
        ]
        
        for url in metadata_urls:
            try:
                # 尝试不同的认证方式
                headers_list = [
                    {"Authorization": f"Bearer {self.app_secret}"},
                    {"X-App-Id": self.app_id, "X-App-Secret": self.app_secret},
                    {"appid": self.app_id, "appsecret": self.app_secret}
                ]
                
                for i, headers in enumerate(headers_list):
                    response = self.session.get(url, headers=headers, timeout=5)
                    if response.status_code != 404:
                        print(f"  {url} (认证{i+1}) - 状态码: {response.status_code}")
                        if response.status_code == 200:
                            print(f"    响应: {response.text[:200]}...")
                            
            except:
                pass
        
        print()
        
    def test_api_endpoints(self):
        """
        测试可能的API端点
        """
        print("=" * 60)
        print("测试KDocs API端点")
        print("=" * 60)
        
        # 常见的API端点
        endpoints = [
            "/v1/docs",
            "/v1/docs/search", 
            "/api/v1/docs",
            "/api/v1/files",
            "/docs",
            "/files",
            "/search"
        ]
        
        for base_url in self.api_bases:
            print(f"基础URL: {base_url}")
            
            # 测试基础连通性
            try:
                response = self.session.get(base_url, timeout=5)
                print(f"  基础连通性: {response.status_code}")
            except:
                print(f"  基础连通性: 失败")
                continue
            
            # 测试各个端点
            for endpoint in endpoints:
                full_url = base_url + endpoint
                
                # 尝试不同的HTTP方法和认证
                methods = ["GET", "POST"]
                auth_headers_list = [
                    {"Authorization": f"Bearer {self.app_secret}"},
                    {"X-App-Id": self.app_id, "X-App-Secret": self.app_secret},
                    {"appid": self.app_id, "appsecret": self.app_secret},
                    {}  # 无认证
                ]
                
                for method in methods:
                    for i, auth_headers in enumerate(auth_headers_list):
                        try:
                            headers = {"Content-Type": "application/json", **auth_headers}
                            
                            if method == "GET":
                                response = self.session.get(full_url, headers=headers, timeout=5)
                            else:
                                # POST请求，尝试搜索
                                data = {"keyword": "石滩供水", "limit": 1}
                                response = self.session.post(full_url, json=data, headers=headers, timeout=5)
                            
                            if response.status_code not in [404, 405]:
                                print(f"  {endpoint} ({method}, 认证{i+1}) - 状态码: {response.status_code}")
                                
                                if response.status_code in [200, 201]:
                                    print(f"    成功响应: {response.text[:200]}...")
                                elif response.status_code in [401, 403]:
                                    print(f"    认证问题: {response.text[:100]}...")
                                else:
                                    print(f"    其他响应: {response.text[:100]}...")
                        
                        except:
                            pass
            
            print()
    
    def test_document_operations(self):
        """
        测试文档操作API
        """
        print("=" * 60)
        print("测试文档操作API")
        print("=" * 60)
        
        # 可能的文档操作端点
        doc_operations = [
            f"/v1/docs/{self.doc_id}",
            f"/v1/docs/{self.doc_id}/content",
            f"/v1/docs/{self.doc_id}/sheets",
            f"/api/docs/{self.doc_id}",
            f"/api/docs/{self.doc_id}/data",
            f"/docs/{self.doc_id}/read",
            f"/docs/{self.doc_id}/write"
        ]
        
        for base_url in self.api_bases:
            print(f"基础URL: {base_url}")
            
            for operation in doc_operations:
                full_url = base_url + operation
                
                # 尝试读取操作
                auth_headers_list = [
                    {"Authorization": f"Bearer {self.app_secret}"},
                    {"X-App-Id": self.app_id, "X-App-Secret": self.app_secret},
                    {"appid": self.app_id, "appsecret": self.app_secret}
                ]
                
                for i, auth_headers in enumerate(auth_headers_list):
                    try:
                        headers = {"Content-Type": "application/json", **auth_headers}
                        response = self.session.get(full_url, headers=headers, timeout=5)
                        
                        if response.status_code not in [404]:
                            print(f"  {operation} (认证{i+1}) - 状态码: {response.status_code}")
                            
                            if response.status_code == 200:
                                print(f"    成功! 响应: {response.text[:200]}...")
                            elif response.status_code in [401, 403]:
                                print(f"    需要认证: {response.text[:100]}...")
                            else:
                                print(f"    响应: {response.text[:100]}...")
                    
                    except:
                        pass
            
            print()
    
    def run_full_test(self):
        """
        运行完整的KDocs API测试
        """
        print("KDocs API测试工具")
        print(f"目标文档: {self.kdocs_url}")
        print(f"文档ID: {self.doc_id}")
        print(f"AppID: {self.app_id}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 测试文档访问
        self.test_document_access()
        
        # 步骤2: 测试API端点
        self.test_api_endpoints()
        
        # 步骤3: 测试文档操作
        self.test_document_operations()
        
        print("=" * 60)
        print("KDocs API测试完成")
        print("=" * 60)
        print("如果找到可用的API端点，可以开始集成到水务数据自动化系统!")

def main():
    """
    主函数
    """
    # 使用WebOffice认证信息
    APP_ID = "SX20251012DLMWBV"
    APP_SECRET = "jZMlBrLzuESMUHCqEhIUUTbGavuzAsy"
    
    tester = KDocsAPITest(APP_ID, APP_SECRET)
    tester.run_full_test()

if __name__ == "__main__":
    main()
