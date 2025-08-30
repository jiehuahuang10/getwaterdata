#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的保活脚本 - 定期访问自己的网站防止休眠
可以部署到GitHub Actions或其他免费cron服务
"""

import requests
import time
from datetime import datetime

def ping_website(url):
    """访问网站保持活跃"""
    try:
        response = requests.get(url, timeout=30)
        print(f"[{datetime.now()}] 访问成功: {response.status_code}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] 访问失败: {e}")
        return False

if __name__ == "__main__":
    # 替换为您的Render网站URL
    WEBSITE_URL = "https://您的项目名.onrender.com"
    
    # 每10分钟访问一次
    while True:
        ping_website(WEBSITE_URL)
        time.sleep(600)  # 10分钟
