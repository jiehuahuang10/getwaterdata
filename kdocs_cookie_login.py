#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs Cookie登录 - 简化版
直接使用浏览器Cookie进行登录
"""

import requests
import json
from datetime import datetime

class KDocsClient:
    def __init__(self, cookie_string=None):
        """
        初始化KDocs客户端
        
        Args:
            cookie_string: 从浏览器复制的Cookie字符串
        """
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.kdocs.cn/'
        })
        
        # 目标文档
        self.link_id = "cqagXO1NDs4P"
        self.file_id = "456521205074"
        
        # 如果提供了Cookie，设置它
        if cookie_string:
            self.set_cookie(cookie_string)
    
    def set_cookie(self, cookie_string):
        """
        设置Cookie
        """
        print("设置Cookie...")
        
        # 解析Cookie字符串
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                name, value = item.split('=', 1)
                self.session.cookies.set(name.strip(), value.strip())
        
        print(f"已设置 {len(self.session.cookies)} 个Cookie")
    
    def check_login(self):
        """
        检查登录状态
        """
        print("\n检查登录状态...")
        
        url = "https://account.kdocs.cn/api/v3/islogin"
        
        try:
            response = self.session.get(url, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {data}")
                
                if data.get('result') == 'ok' or data.get('isLogin'):
                    print("登录状态: 已登录")
                    return True
                else:
                    print("登录状态: 未登录")
                    return False
            else:
                print(f"检查失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"出错: {e}")
            return False
    
    def get_document_info(self):
        """
        获取文档信息
        """
        print("\n获取文档信息...")
        
        url = f"https://drive.kdocs.cn/api/v5/links/{self.link_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                fileinfo = data.get('fileinfo', {})
                print(f"文档名称: {fileinfo.get('fname')}")
                print(f"文件ID: {fileinfo.get('id')}")
                print(f"用户权限: {data.get('user_permission')}")
                print(f"可写入: {data.get('user_acl', {}).get('update')}")
                
                return data
            else:
                print(f"获取失败: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"出错: {e}")
            return None
    
    def test_session_api(self):
        """
        测试会话API
        """
        print("\n测试会话API...")
        
        url = f"https://www.kdocs.cn/api/v3/office/session/{self.link_id}/et"
        
        try:
            # 尝试GET请求
            response = self.session.get(url, timeout=10)
            print(f"GET 状态码: {response.status_code}")
            print(f"GET 响应: {response.text[:200]}")
            
            # 尝试POST请求
            test_data = {"action": "test"}
            response = self.session.post(url, json=test_data, timeout=10)
            print(f"POST 状态码: {response.status_code}")
            print(f"POST 响应: {response.text[:200]}")
            
        except Exception as e:
            print(f"出错: {e}")
    
    def save_cookies(self):
        """
        保存Cookie到文件
        """
        cookies = self.session.cookies.get_dict()
        
        with open('kdocs_cookies.json', 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print("\nCookie已保存到 kdocs_cookies.json")
    
    def load_cookies(self):
        """
        从文件加载Cookie
        """
        try:
            with open('kdocs_cookies.json', 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            print(f"已加载 {len(cookies)} 个Cookie")
            return True
            
        except FileNotFoundError:
            print("Cookie文件不存在")
            return False
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return False

def main():
    """
    主函数
    """
    print("=" * 60)
    print("KDocs Cookie登录工具")
    print("=" * 60)
    print()
    
    # 尝试加载已保存的Cookie
    client = KDocsClient()
    
    if client.load_cookies():
        print("\n使用已保存的Cookie")
        
        if client.check_login():
            print("\nCookie有效!")
        else:
            print("\nCookie已失效，需要重新获取")
            client = None
    else:
        client = None
    
    # 如果没有有效的Cookie，提示用户输入
    if client is None:
        print("\n请按以下步骤获取Cookie:")
        print("1. 在浏览器中打开 https://www.kdocs.cn 并登录")
        print("2. 按 F12 打开开发者工具")
        print("3. 切换到 Network (网络) 标签")
        print("4. 刷新页面")
        print("5. 点击任意请求，在右侧找到 Request Headers")
        print("6. 找到 Cookie 行，复制整行的值")
        print()
        print("示例格式:")
        print("wps_sid=xxx; sensorsdata2015jssdkcross=xxx; ...")
        print()
        
        cookie_input = input("请粘贴Cookie (或按Enter跳过): ").strip()
        
        if cookie_input:
            client = KDocsClient(cookie_input)
            
            # 检查登录
            if client.check_login():
                print("\nCookie有效!")
                
                # 保存Cookie
                client.save_cookies()
            else:
                print("\nCookie无效，请检查是否正确复制")
                return
        else:
            print("\n未提供Cookie，退出")
            return
    
    # 测试文档访问
    print("\n" + "=" * 60)
    print("测试文档访问")
    print("=" * 60)
    
    doc_info = client.get_document_info()
    
    if doc_info:
        print("\n文档访问成功!")
        
        # 测试会话API
        client.test_session_api()
    else:
        print("\n文档访问失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n提示: Cookie已保存，下次运行时会自动加载")

if __name__ == "__main__":
    main()

