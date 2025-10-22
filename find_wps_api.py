#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帮助查找WPS开放平台的正确API接口
"""

import requests
import json

class WPSAPIFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def check_wps_open_platform(self):
        """
        检查WPS开放平台的主要入口
        """
        print("=" * 60)
        print("检查WPS开放平台主要入口")
        print("=" * 60)
        
        main_urls = [
            ("WPS开放平台主站", "https://open.wps.cn"),
            ("WPS开发者中心", "https://developer.wps.cn"),
            ("WPS云文档开放平台", "https://open.kdocs.cn"),
            ("金山文档开发者", "https://developer.kdocs.cn"),
            ("WPS轻文档开放平台", "https://qing.wps.cn/open"),
        ]
        
        for name, url in main_urls:
            try:
                print(f"\n{name}: {url}")
                response = self.session.get(url, timeout=10, allow_redirects=True)
                print(f"  状态码: {response.status_code}")
                print(f"  最终URL: {response.url}")
                
                if response.status_code == 200:
                    print(f"  结果: 可访问")
                    
                    # 检查是否是开放平台页面
                    content = response.text.lower()
                    keywords = ['api', '接口', '文档', 'appid', 'appsecret', '开发者']
                    found = [kw for kw in keywords if kw in content]
                    
                    if found:
                        print(f"  关键词: {', '.join(found)}")
                        
                        # 保存页面
                        filename = name.replace(' ', '_') + '.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"  已保存: {filename}")
                
            except Exception as e:
                print(f"  错误: {e}")
    
    def check_api_docs(self):
        """
        检查API文档位置
        """
        print("\n" + "=" * 60)
        print("检查API文档")
        print("=" * 60)
        
        doc_urls = [
            ("API文档入口1", "https://open.wps.cn/docs"),
            ("API文档入口2", "https://developer.wps.cn/docs"),
            ("API文档入口3", "https://open.wps.cn/document"),
            ("云文档API", "https://open.wps.cn/documents"),
            ("WebOffice API", "https://solution.wps.cn/docs"),
        ]
        
        for name, url in doc_urls:
            try:
                print(f"\n{name}: {url}")
                response = self.session.get(url, timeout=10)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  结果: 文档可访问")
                    
                    # 保存文档页面
                    filename = name.replace(' ', '_') + '_doc.html'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"  已保存: {filename}")
                
            except Exception as e:
                print(f"  错误: {e}")
    
    def check_console(self):
        """
        检查开发者控制台入口
        """
        print("\n" + "=" * 60)
        print("检查开发者控制台")
        print("=" * 60)
        
        console_urls = [
            ("控制台1", "https://open.wps.cn/console"),
            ("控制台2", "https://developer.wps.cn/console"),
            ("控制台3", "https://open.wps.cn/manage"),
            ("应用管理", "https://open.wps.cn/apps"),
        ]
        
        for name, url in console_urls:
            try:
                print(f"\n{name}: {url}")
                response = self.session.get(url, timeout=10, allow_redirects=False)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 302:
                    location = response.headers.get('Location', '')
                    print(f"  重定向到: {location}")
                    print(f"  结果: 需要登录（说明控制台存在）")
                elif response.status_code == 200:
                    print(f"  结果: 可访问")
                
            except Exception as e:
                print(f"  错误: {e}")

def print_guide():
    """
    打印访问指南
    """
    print("\n" + "=" * 60)
    print("WPS开放平台访问指南")
    print("=" * 60)
    
    print("""
1. WPS开放平台主站
   网址: https://open.wps.cn
   说明: WPS官方开放平台，提供多种产品API
   
2. 注册/登录步骤
   a) 访问 https://open.wps.cn
   b) 点击右上角"登录"或"注册"
   c) 使用手机号注册（13509289726）
   
3. 创建应用
   a) 登录后进入"控制台"
   b) 点击"创建应用"
   c) 选择"云文档"或"WebOffice"
   d) 填写应用信息
   e) 获取 AppID 和 AppSecret
   
4. 查看API文档
   主要文档地址:
   - https://open.wps.cn/docs (主文档)
   - https://solution.wps.cn/docs (解决方案文档)
   
5. 可能遇到的问题
   - 如果提示"企业认证"：个人也可以使用基础API
   - 如果找不到"云文档"：尝试"WebOffice"或"轻文档"
   - 如果没有权限：联系客服申请API权限

常见API类别:
- WebOffice API: 在线编辑文档
- 云文档 API: 文档存储和管理
- 轻文档 API: 轻量级文档协作

建议:
1. 先访问 https://open.wps.cn 了解整体架构
2. 注册开发者账号
3. 查看"快速开始"或"新手指南"
4. 根据需求选择合适的产品线
""")

def main():
    print("WPS API查找工具")
    print("=" * 60)
    
    finder = WPSAPIFinder()
    
    # 1. 检查主要入口
    finder.check_wps_open_platform()
    
    # 2. 检查API文档
    finder.check_api_docs()
    
    # 3. 检查控制台
    finder.check_console()
    
    # 4. 打印指南
    print_guide()
    
    print("\n" + "=" * 60)
    print("检查完成！")
    print("=" * 60)
    print("\n建议下一步:")
    print("1. 在浏览器中访问: https://open.wps.cn")
    print("2. 注册/登录开发者账号")
    print("3. 查看保存的HTML文件了解更多信息")
    print("4. 如果有问题，我可以继续帮您")

if __name__ == "__main__":
    main()

