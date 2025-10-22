#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs直接登录
使用账号密码自动登录
"""

import requests
import json
import hashlib
import time

class KDocsDirectLogin:
    def __init__(self):
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://www.kdocs.cn',
            'Referer': 'https://www.kdocs.cn/'
        })
        
        self.link_id = "cqagXO1NDs4P"
        self.file_id = "456521205074"
    
    def login(self, phone, password):
        """
        使用手机号和密码登录
        """
        print("开始登录KDocs...")
        print(f"手机号: {phone}")
        
        # 尝试多个可能的登录API
        login_endpoints = [
            "https://account.kdocs.cn/api/v3/signIn",
            "https://account.kdocs.cn/api/v3/signin",
            "https://account.kdocs.cn/api/v3/login",
            "https://www.kdocs.cn/api/v3/signin"
        ]
        
        # 尝试不同的登录数据格式
        login_data_formats = [
            {
                "account": phone,
                "password": password,
                "type": "phone"
            },
            {
                "phone": phone,
                "password": password
            },
            {
                "username": phone,
                "password": password,
                "login_type": "phone"
            },
            {
                "mobile": phone,
                "pwd": password
            }
        ]
        
        for endpoint in login_endpoints:
            print(f"\n尝试登录端点: {endpoint}")
            
            for i, data in enumerate(login_data_formats):
                print(f"  尝试数据格式 {i+1}...")
                
                try:
                    response = self.session.post(endpoint, json=data, timeout=10)
                    print(f"  状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  响应: {result}")
                        
                        # 检查是否登录成功
                        if (result.get('result') == 'ok' or 
                            result.get('code') == 0 or 
                            result.get('success') == True or
                            'token' in result or
                            'user' in result):
                            
                            print("\n登录成功!")
                            
                            # 保存Cookie
                            self.save_cookies()
                            
                            # 验证登录
                            if self.check_login():
                                return True
                        else:
                            error_msg = result.get('msg') or result.get('message') or result.get('errmsg')
                            if error_msg:
                                print(f"  错误: {error_msg}")
                    
                    elif response.status_code == 404:
                        print(f"  端点不存在")
                        break  # 跳过这个端点的其他格式
                    
                    else:
                        print(f"  失败: {response.text[:100]}")
                
                except Exception as e:
                    print(f"  异常: {e}")
        
        print("\n所有登录尝试都失败了")
        return False
    
    def check_login(self):
        """
        检查登录状态
        """
        print("\n检查登录状态...")
        
        url = "https://account.kdocs.cn/api/v3/islogin"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"登录检查响应: {result}")
                
                if result.get('result') == 'ok' or result.get('isLogin'):
                    print("确认已登录!")
                    return True
                else:
                    print("未登录")
                    return False
            else:
                print(f"检查失败: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"检查出错: {e}")
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
    
    def save_cookies(self):
        """
        保存Cookie
        """
        cookies = self.session.cookies.get_dict()
        
        with open('kdocs_cookies.json', 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        print("Cookie已保存到 kdocs_cookies.json")

def main():
    # 账号信息
    PHONE = "13509289726"
    PASSWORD = "1456987bcA$$"
    
    print("=" * 60)
    print("KDocs自动登录")
    print("=" * 60)
    
    client = KDocsDirectLogin()
    
    # 尝试登录
    if client.login(PHONE, PASSWORD):
        print("\n" + "=" * 60)
        print("登录成功! 测试文档访问...")
        print("=" * 60)
        
        # 测试文档访问
        doc_info = client.get_document_info()
        
        if doc_info:
            print("\n" + "=" * 60)
            print("成功! 可以开始自动化操作!")
            print("=" * 60)
        else:
            print("\n文档访问失败，但Cookie已保存")
    else:
        print("\n登录失败")

if __name__ == "__main__":
    main()

