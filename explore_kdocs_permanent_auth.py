#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索KDocs的长期认证方案
1. 检查是否有开放平台API
2. 检查是否支持OAuth
3. 检查是否有企业API
"""

import requests
import json

class KDocsAuthExplorer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
    
    def check_oauth_support(self):
        """
        检查是否支持OAuth认证
        """
        print("=" * 60)
        print("检查OAuth支持")
        print("=" * 60)
        
        oauth_endpoints = [
            "https://account.kdocs.cn/oauth/authorize",
            "https://account.kdocs.cn/api/oauth/authorize",
            "https://open.kdocs.cn/oauth/authorize",
            "https://www.kdocs.cn/oauth/authorize",
        ]
        
        for url in oauth_endpoints:
            try:
                response = self.session.get(url, timeout=5, allow_redirects=False)
                print(f"{url}")
                print(f"  状态码: {response.status_code}")
                
                if response.status_code in [200, 302, 401]:
                    print(f"  结果: 可能支持OAuth")
                    return url
                else:
                    print(f"  结果: 不支持")
            
            except Exception as e:
                print(f"  错误: {e}")
        
        return None
    
    def check_open_platform(self):
        """
        检查是否有开放平台
        """
        print("\n" + "=" * 60)
        print("检查开放平台")
        print("=" * 60)
        
        open_platform_urls = [
            "https://open.kdocs.cn",
            "https://open.kdocs.cn/api",
            "https://developer.kdocs.cn",
            "https://api.kdocs.cn",
            "https://www.kdocs.cn/developers",
            "https://www.kdocs.cn/open",
        ]
        
        for url in open_platform_urls:
            try:
                response = self.session.get(url, timeout=5)
                print(f"{url}")
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # 检查关键词
                    keywords = ['api', 'token', 'oauth', 'developer', '开发者', '开放平台']
                    found_keywords = [kw for kw in keywords if kw in content]
                    
                    if found_keywords:
                        print(f"  发现关键词: {', '.join(found_keywords)}")
                        print(f"  结果: 可能是开放平台")
                        
                        # 保存页面内容
                        filename = url.replace('https://', '').replace('/', '_') + '.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"  已保存到: {filename}")
                        
                        return url
                    else:
                        print(f"  结果: 普通页面")
                else:
                    print(f"  结果: 不可访问")
            
            except Exception as e:
                print(f"  错误: {e}")
        
        return None
    
    def check_api_token_settings(self):
        """
        检查账户设置中是否有API Token功能
        """
        print("\n" + "=" * 60)
        print("检查API Token设置")
        print("=" * 60)
        
        settings_urls = [
            "https://www.kdocs.cn/settings/api",
            "https://www.kdocs.cn/settings/developer",
            "https://www.kdocs.cn/settings/token",
            "https://account.kdocs.cn/settings/api",
            "https://account.kdocs.cn/settings/developer",
        ]
        
        for url in settings_urls:
            try:
                response = self.session.get(url, timeout=5)
                print(f"{url}")
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  结果: 页面存在（需要登录后访问）")
                elif response.status_code == 401:
                    print(f"  结果: 需要认证（说明页面存在）")
                elif response.status_code == 403:
                    print(f"  结果: 禁止访问（可能需要特定权限）")
                elif response.status_code == 404:
                    print(f"  结果: 不存在")
                else:
                    print(f"  结果: {response.status_code}")
            
            except Exception as e:
                print(f"  错误: {e}")
    
    def check_wps_integration(self):
        """
        检查与WPS的关系（KDocs是WPS旗下产品）
        """
        print("\n" + "=" * 60)
        print("检查WPS集成")
        print("=" * 60)
        
        # WPS开放平台
        wps_urls = [
            "https://open.wps.cn",
            "https://developer.wps.cn",
            "https://qing.wps.cn/open",
        ]
        
        print("KDocs是WPS旗下产品，检查WPS开放平台...")
        
        for url in wps_urls:
            try:
                response = self.session.get(url, timeout=5)
                print(f"{url}")
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # 检查是否提到KDocs或云文档
                    if 'kdocs' in content or '云文档' in content or '轻文档' in content:
                        print(f"  结果: 提到了云文档功能")
                        
                        filename = url.replace('https://', '').replace('/', '_') + '.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"  已保存到: {filename}")
                        
                        return url
            
            except Exception as e:
                print(f"  错误: {e}")
        
        return None

def main():
    print("探索KDocs长期认证方案")
    print("=" * 60)
    
    explorer = KDocsAuthExplorer()
    
    # 1. 检查OAuth支持
    oauth_url = explorer.check_oauth_support()
    
    # 2. 检查开放平台
    open_platform_url = explorer.check_open_platform()
    
    # 3. 检查API Token设置
    explorer.check_api_token_settings()
    
    # 4. 检查WPS集成
    wps_url = explorer.check_wps_integration()
    
    # 总结
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    
    if oauth_url:
        print(f"发现OAuth端点: {oauth_url}")
        print("  建议: 尝试OAuth认证流程")
    
    if open_platform_url:
        print(f"发现开放平台: {open_platform_url}")
        print("  建议: 查看开放平台文档")
    
    if wps_url:
        print(f"发现WPS平台: {wps_url}")
        print("  建议: 通过WPS开放平台API访问KDocs")
    
    if not any([oauth_url, open_platform_url, wps_url]):
        print("未发现官方长期认证方案")
        print("\n替代方案:")
        print("1. 使用自动刷新Cookie（推荐）")
        print("2. 联系KDocs客服申请企业API")
        print("3. 使用WPS开放平台（如果适用）")
        print("4. 考虑使用Excel本地文件代替云文档")

if __name__ == "__main__":
    main()

