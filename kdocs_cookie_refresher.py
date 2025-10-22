#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs Cookie自动刷新器
定期检查Cookie有效性并自动刷新
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os

class KDocsCookieRefresher:
    def __init__(self):
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.kdocs.cn/'
        })
        
        self.cookie_file = 'kdocs_cookies.json'
        self.cookie_meta_file = 'kdocs_cookie_meta.json'
        self.link_id = "cqagXO1NDs4P"
    
    def load_cookies(self):
        """
        加载Cookie
        """
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            return True
        except:
            return False
    
    def save_cookies(self):
        """
        保存Cookie和元数据
        """
        cookies = self.session.cookies.get_dict()
        
        # 保存Cookie
        with open(self.cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        
        # 保存元数据（更新时间）
        meta = {
            'last_updated': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        with open(self.cookie_meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        print(f"Cookie已更新，有效期至: {meta['expires_at']}")
    
    def get_cookie_meta(self):
        """
        获取Cookie元数据
        """
        try:
            with open(self.cookie_meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def check_cookie_expiry(self):
        """
        检查Cookie是否即将过期
        """
        meta = self.get_cookie_meta()
        
        if not meta:
            return True, "无元数据"
        
        expires_at = datetime.fromisoformat(meta['expires_at'])
        now = datetime.now()
        days_left = (expires_at - now).days
        
        print(f"Cookie剩余有效期: {days_left} 天")
        
        # 如果少于3天，需要刷新
        if days_left < 3:
            return True, f"即将过期（剩余{days_left}天）"
        
        return False, f"有效（剩余{days_left}天）"
    
    def check_cookie_valid(self):
        """
        检查Cookie是否有效
        """
        url = "https://account.kdocs.cn/api/v3/islogin"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') == 'ok' or result.get('isLogin'):
                    return True, "Cookie有效"
                else:
                    return False, "Cookie已失效"
            else:
                return False, f"检查失败: {response.status_code}"
        
        except Exception as e:
            return False, f"检查出错: {e}"
    
    def refresh_cookie(self):
        """
        刷新Cookie（通过访问页面）
        """
        print("尝试刷新Cookie...")
        
        # 访问主页和文档页面来刷新Cookie
        urls = [
            "https://www.kdocs.cn/",
            f"https://www.kdocs.cn/l/{self.link_id}",
            "https://drive.kdocs.cn/api/v3/userinfo"
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                print(f"访问 {url}: {response.status_code}")
                
                if response.status_code == 200:
                    # 保存更新后的Cookie
                    self.save_cookies()
                    return True
            
            except Exception as e:
                print(f"访问失败: {e}")
        
        return False
    
    def auto_refresh_if_needed(self):
        """
        自动检查并刷新Cookie
        """
        print("=" * 60)
        print("KDocs Cookie自动刷新检查")
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 加载Cookie
        if not self.load_cookies():
            print("错误: 无法加载Cookie")
            print("请先运行 python kdocs_cookie_login.py 设置Cookie")
            return False
        
        # 检查过期时间
        need_refresh, reason = self.check_cookie_expiry()
        print(f"过期检查: {reason}")
        
        # 检查有效性
        is_valid, msg = self.check_cookie_valid()
        print(f"有效性检查: {msg}")
        
        # 如果即将过期或已失效，尝试刷新
        if need_refresh or not is_valid:
            print("\n需要刷新Cookie")
            
            if self.refresh_cookie():
                print("Cookie刷新成功!")
                
                # 再次验证
                is_valid, msg = self.check_cookie_valid()
                print(f"验证结果: {msg}")
                
                return is_valid
            else:
                print("Cookie刷新失败")
                print("\n建议:")
                print("1. 在浏览器中重新登录 https://www.kdocs.cn")
                print("2. 运行 python kdocs_cookie_login.py")
                print("3. 粘贴新的Cookie")
                return False
        else:
            print("\nCookie状态良好，无需刷新")
            return True

def main():
    refresher = KDocsCookieRefresher()
    
    # 自动检查并刷新
    result = refresher.auto_refresh_if_needed()
    
    print("\n" + "=" * 60)
    if result:
        print("状态: 正常")
    else:
        print("状态: 需要手动更新")
    print("=" * 60)

if __name__ == "__main__":
    main()

