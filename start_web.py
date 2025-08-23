#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据获取Web界面启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket

def check_port_available(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def install_dependencies():
    """安装必需的依赖"""
    print("🔧 检查并安装依赖...")
    
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError:
        print("📦 正在安装 Flask...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask==3.0.0'], check=True)
        print("✅ Flask 安装完成")
    
    # 检查其他必需模块
    required_modules = ['requests', 'beautifulsoup4']
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"✅ {module} 已安装")
        except ImportError:
            print(f"📦 正在安装 {module}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', module], check=True)

def main():
    """主函数"""
    print("="*60)
    print("🌐 水务数据获取系统 - Web界面启动器")
    print("="*60)
    
    # 检查依赖
    install_dependencies()
    
    # 检查端口
    port = 5000
    if not check_port_available(port):
        print(f"⚠️  端口 {port} 已被占用，尝试使用端口 5001")
        port = 5001
        if not check_port_available(port):
            print("❌ 端口 5000 和 5001 都被占用，请手动指定端口")
            return False
    
    print(f"\n🚀 启动Web服务器...")
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"🌐 外网地址: http://0.0.0.0:{port}")
    print(f"⏹️  按 Ctrl+C 停止服务")
    
    # 设置环境变量
    os.environ['FLASK_APP'] = 'web_app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # 延迟打开浏览器
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask应用
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 服务已停止")
        return True
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 如果遇到问题，请检查:")
        print("   1. Python环境是否正确")
        print("   2. 依赖包是否安装完整")
        print("   3. 端口是否被其他程序占用")
        print("   4. 防火墙设置是否允许访问")
        
        input("\n按回车键退出...")
    
    sys.exit(0 if success else 1)
