#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查WPS开放平台的API文档
找到正确的API端点
"""

import requests

def check_api_endpoints():
    """
    尝试不同的API端点
    """
    app_id = "AK20251012ADRMHT"
    app_secret = "7166bd504290a908fde5a1d1af37ac00"
    
    # 可能的API端点
    endpoints = [
        # 标准OAuth端点
        ("OAuth标准", "https://open.wps.cn/oauth/token", {
            "grant_type": "client_credentials",
            "client_id": app_id,
            "client_secret": app_secret
        }),
        
        # API v3端点
        ("API v3", "https://open.wps.cn/api/v3/auth/token", {
            "grant_type": "client_credentials",
            "appid": app_id,
            "secret": app_secret
        }),
        
        # WebOffice端点
        ("WebOffice", "https://solution.wps.cn/api/oauth2/access_token", {
            "grant_type": "client_credentials",
            "appid": app_id,
            "secret": app_secret
        }),
        
        # 可能的v2端点
        ("API v2", "https://open.wps.cn/api/v2/auth/token", {
            "grant_type": "client_credentials",
            "appid": app_id,
            "secret": app_secret
        }),
        
        # 轻文档端点
        ("轻文档", "https://qing.wps.cn/api/oauth2/token", {
            "grant_type": "client_credentials",
            "appid": app_id,
            "secret": app_secret
        }),
    ]
    
    print("=" * 60)
    print("测试不同的API端点")
    print("=" * 60)
    
    for name, url, data in endpoints:
        print(f"\n测试: {name}")
        print(f"URL: {url}")
        
        try:
            # POST请求
            response = requests.post(url, json=data, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"成功！")
                print(f"响应: {result}")
                
                if 'access_token' in result:
                    print(f"\n找到了！这是正确的端点！")
                    print(f"Access Token: {result['access_token'][:30]}...")
                    return url, data
            else:
                print(f"失败: {response.text[:200]}")
        
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n" + "=" * 60)
    print("未找到可用的端点")
    print("=" * 60)
    
    # 检查是否需要先在后台配置权限
    print("\n建议:")
    print("1. 访问WPS开放平台后台")
    print("2. 查看'应用能力'或'权限管理'")
    print("3. 确保已开通所需的API权限")
    print("4. 查看API文档获取正确的端点")
    
    return None, None

def check_api_docs():
    """
    访问API文档页面
    """
    print("\n" + "=" * 60)
    print("查看API文档")
    print("=" * 60)
    
    doc_urls = [
        "https://open.wps.cn/docs",
        "https://solution.wps.cn/docs",
    ]
    
    for url in doc_urls:
        print(f"\n文档地址: {url}")
        print("请在浏览器中打开此地址查看具体的API调用方式")

if __name__ == "__main__":
    url, data = check_api_endpoints()
    
    if not url:
        check_api_docs()
        
        print("\n" + "=" * 60)
        print("下一步操作")
        print("=" * 60)
        print("\n请在WPS开放平台后台:")
        print("1. 点击左侧'应用能力'菜单")
        print("2. 查看您的应用可以使用哪些API")
        print("3. 点击'API调用说明'或'文档中心'")
        print("4. 找到正确的API端点和调用方式")
        print("\n然后将正确的信息告诉我！")

