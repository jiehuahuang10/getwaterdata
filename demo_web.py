#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面演示脚本
"""

import subprocess
import sys
import time
import webbrowser
import threading

def start_demo():
    """启动演示"""
    print("🎬 水务数据获取系统 - Web界面演示")
    print("="*50)
    
    print("🔧 检查系统状态...")
    
    # 检查Flask
    try:
        import flask
        print("✅ Flask 已就绪")
    except ImportError:
        print("❌ Flask 未安装，请运行: pip install flask==3.0.0")
        return False
    
    # 检查模板文件
    import os
    if os.path.exists('templates/index.html'):
        print("✅ 模板文件已就绪")
    else:
        print("❌ 模板文件缺失")
        return False
    
    # 检查主脚本
    if os.path.exists('complete_8_meters_getter.py'):
        print("✅ 数据获取脚本已就绪")
    else:
        print("❌ 数据获取脚本缺失")
        return False
    
    print("\n🚀 启动Web服务器...")
    print("📱 界面地址: http://localhost:5000")
    print("🎯 功能特点:")
    print("   • 一键获取最近7天水务数据")
    print("   • 实时显示获取进度")
    print("   • 美观的数据展示界面")
    print("   • 历史数据查看功能")
    print("   • 响应式设计，支持手机访问")
    
    print("\n⏳ 3秒后自动打开浏览器...")
    
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
        print("🌐 浏览器已打开")
    
    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("🔄 按 Ctrl+C 停止演示")
    print("-" * 50)
    
    try:
        # 启动Web应用
        from web_app import app
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 演示结束")
        return True
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    success = start_demo()
    
    if success:
        print("\n🎉 演示完成！")
        print("\n💡 使用提示:")
        print("   1. 点击 '🚀 获取最近7天数据' 按钮开始")
        print("   2. 观察进度条显示获取进度")
        print("   3. 查看获取到的8个水表数据")
        print("   4. 访问 '📊 历史数据' 页面查看历史记录")
    else:
        print("\n❌ 演示失败")
        print("💡 请检查依赖和文件是否完整")
    
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
