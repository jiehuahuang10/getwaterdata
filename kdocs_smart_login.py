#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs智能登录
先获取ssid，然后登录
"""

import requests
import json
import time
import hashlib

class KDocsSmartLogin:
    def __init__(self):
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://www.kdocs.cn',
            'Referer': 'https://www.kdocs.cn/'
        })
        
        self.link_id = "cqagXO1NDs4P"
        self.file_id = "456521205074"
        self.ssid = None
    
    def get_ssid(self):
        """
        获取ssid（会话ID）
        """
        print("获取ssid...")
        
        # 访问登录页面获取ssid
        urls = [
            "https://account.kdocs.cn/api/v3/ssid",
            "https://www.kdocs.cn/api/v3/ssid",
            "https://account.kdocs.cn/",
            "https://www.kdocs.cn/"
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                print(f"访问 {url}: {response.status_code}")
                
                if response.status_code == 200:
                    # 尝试从响应中提取ssid
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        data = response.json()
                        if 'ssid' in data:
                            self.ssid = data['ssid']
                            print(f"从JSON获取ssid: {self.ssid}")
                            return self.ssid
                    
                    # 尝试从Cookie中获取ssid
                    if 'ssid' in self.session.cookies:
                        self.ssid = self.session.cookies.get('ssid')
                        print(f"从Cookie获取ssid: {self.ssid}")
                        return self.ssid
                    
                    # 尝试从HTML中提取ssid
                    content = response.text
                    if 'ssid' in content:
                        # 简单的正则提取
                        import re
                        match = re.search(r'"ssid"\s*:\s*"([^"]+)"', content)
                        if match:
                            self.ssid = match.group(1)
                            print(f"从HTML获取ssid: {self.ssid}")
                            return self.ssid
            
            except Exception as e:
                print(f"获取ssid出错: {e}")
        
        # 如果无法获取ssid，生成一个
        self.ssid = f"temp_ssid_{int(time.time())}"
        print(f"生成临时ssid: {self.ssid}")
        return self.ssid
    
    def login_with_password(self, phone, password):
        """
        使用密码登录
        """
        print(f"\n开始登录...")
        print(f"手机号: {phone}")
        
        # 确保有ssid
        if not self.ssid:
            self.get_ssid()
        
        # 登录API
        login_url = "https://account.kdocs.cn/api/v3/login"
        
        # 登录数据
        login_data = {
            "ssid": self.ssid,
            "account": phone,
            "password": password,
            "type": "phone",
            "remember": True
        }
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=10)
            print(f"登录响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"登录响应: {result}")
                
                if result.get('result') == 'ok' or result.get('code') == 0:
                    print("登录成功!")
                    self.save_cookies()
                    return True
                else:
                    error_msg = result.get('msg', '未知错误')
                    print(f"登录失败: {error_msg}")
                    return False
            else:
                print(f"登录请求失败: {response.text}")
                return False
        
        except Exception as e:
            print(f"登录出错: {e}")
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
                print(f"登录状态: {result}")
                
                if result.get('result') == 'ok' or result.get('isLogin'):
                    print("已登录!")
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
        
        print("Cookie已保存")

def main():
    PHONE = "13509289726"
    PASSWORD = "1456987bcA$$"
    
    print("=" * 60)
    print("KDocs智能登录")
    print("=" * 60)
    
    client = KDocsSmartLogin()
    
    # 获取ssid
    client.get_ssid()
    
    # 登录
    if client.login_with_password(PHONE, PASSWORD):
        # 验证登录
        if client.check_login():
            print("\n" + "=" * 60)
            print("登录验证成功!")
            print("=" * 60)
            
            # 测试文档访问
            doc_info = client.get_document_info()
            
            if doc_info:
                print("\n" + "=" * 60)
                print("完美! 所有功能正常!")
                print("=" * 60)
            else:
                print("\n文档访问需要进一步配置")
        else:
            print("\n登录验证失败，但Cookie已保存")
            print("可能需要手动验证（短信验证码等）")
    else:
        print("\n登录失败")
        print("\n建议使用浏览器Cookie方式:")
        print("1. 在浏览器中登录 https://www.kdocs.cn")
        print("2. 运行: python kdocs_cookie_login.py")
        print("3. 粘贴浏览器的Cookie")

if __name__ == "__main__":
    main()

