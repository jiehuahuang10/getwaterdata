#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Cookie有效期
用于GitHub Actions自动检查
"""

import sys
from kdocs_cookie_refresher import KDocsCookieRefresher

def main():
    try:
        refresher = KDocsCookieRefresher()
        
        # 加载Cookie
        if not refresher.load_cookies():
            print("错误: 无法加载Cookie文件")
            sys.exit(1)
        
        # 检查过期时间
        need_refresh, reason = refresher.check_cookie_expiry()
        print(f"过期检查: {reason}")
        
        # 检查有效性
        is_valid, msg = refresher.check_cookie_valid()
        print(f"有效性检查: {msg}")
        
        # 如果需要刷新或已失效
        if need_refresh or not is_valid:
            print("\n结论: 需要更新Cookie")
            sys.exit(1)
        else:
            print("\n结论: Cookie状态良好")
            sys.exit(0)
    
    except Exception as e:
        print(f"检查出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

