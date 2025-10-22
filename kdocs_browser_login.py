#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs浏览器自动登录
使用Playwright模拟浏览器登录并提取Cookie
"""

import json
import time

def login_and_extract_cookies():
    """
    使用Playwright登录并提取Cookie
    """
    print("=" * 60)
    print("KDocs浏览器自动登录")
    print("=" * 60)
    print()
    
    # 账号信息
    PHONE = "13509289726"
    PASSWORD = "1456987bcA$$"
    
    print(f"手机号: {PHONE}")
    print(f"密码: {'*' * len(PASSWORD)}")
    print()
    
    print("提示: 由于KDocs登录可能需要验证码或其他验证")
    print("建议使用更简单的Cookie复制方式")
    print()
    print("=" * 60)
    print("推荐方案: 手动复制Cookie")
    print("=" * 60)
    print()
    print("步骤:")
    print("1. 在浏览器中访问: https://www.kdocs.cn")
    print("2. 使用您的账号登录")
    print("3. 按F12打开开发者工具")
    print("4. 切换到Network标签")
    print("5. 刷新页面")
    print("6. 点击第一个请求")
    print("7. 找到Cookie并复制")
    print()
    print("然后运行: python kdocs_cookie_login.py")
    print()
    
    # 提供一个简化的Cookie提取工具
    print("=" * 60)
    print("或者使用以下JavaScript代码直接在浏览器控制台运行:")
    print("=" * 60)
    print()
    print("document.cookie")
    print()
    print("复制输出的内容，然后运行 kdocs_cookie_login.py")

if __name__ == "__main__":
    login_and_extract_cookies()

