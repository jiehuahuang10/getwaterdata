#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金山文档OAuth授权助手
帮助用户完成OAuth授权流程
"""

from flask import Flask, request, redirect, render_template_string
import webbrowser
import threading
import time
from kdocs_api_client import KDocsAPIClient

class KDocsOAuthHelper:
    """金山文档OAuth授权助手"""
    
    def __init__(self, app_id, app_secret, port=5001):
        self.app_id = app_id
        self.app_secret = app_secret
        self.port = port
        self.redirect_uri = f"http://localhost:{port}/callback"
        
        self.client = KDocsAPIClient(app_id, app_secret)
        self.flask_app = Flask(__name__)
        self.setup_routes()
        
        self.authorization_result = None
        self.server_thread = None
    
    def setup_routes(self):
        """设置Flask路由"""
        
        @self.flask_app.route('/')
        def index():
            """主页 - 显示授权链接"""
            auth_url = self.client.get_authorization_url(self.redirect_uri, state="water_data_auth")
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>金山文档授权</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 50px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .btn { 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background: #007bff; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin: 10px 0;
                    }
                    .btn:hover { background: #0056b3; }
                    .info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 金山文档API授权</h1>
                    <div class="info">
                        <h3>授权说明：</h3>
                        <p>1. 点击下方按钮跳转到金山文档授权页面</p>
                        <p>2. 使用您的WPS账号登录并授权</p>
                        <p>3. 授权成功后会自动跳转回来</p>
                        <p>4. 系统将自动保存访问令牌</p>
                    </div>
                    
                    <a href="{{ auth_url }}" class="btn" target="_blank">
                        🚀 开始授权
                    </a>
                    
                    <div class="info">
                        <h3>📋 授权链接：</h3>
                        <p><small>{{ auth_url }}</small></p>
                    </div>
                </div>
            </body>
            </html>
            """
            return render_template_string(html, auth_url=auth_url)
        
        @self.flask_app.route('/callback')
        def callback():
            """OAuth回调处理"""
            code = request.args.get('code')
            state = request.args.get('state')
            error = request.args.get('error')
            
            if error:
                self.authorization_result = {'success': False, 'error': error}
                return f"""
                <h1>❌ 授权失败</h1>
                <p>错误信息: {error}</p>
                <p>请关闭此页面并重试</p>
                """
            
            if not code:
                self.authorization_result = {'success': False, 'error': '未获取到授权码'}
                return """
                <h1>❌ 授权失败</h1>
                <p>未获取到授权码</p>
                <p>请关闭此页面并重试</p>
                """
            
            # 使用授权码获取访问令牌
            success = self.client.get_access_token(code, self.redirect_uri)
            
            if success:
                # 保存令牌
                self.client.save_tokens()
                self.authorization_result = {'success': True, 'client': self.client}
                
                return """
                <h1>✅ 授权成功！</h1>
                <p>访问令牌已获取并保存</p>
                <p>您现在可以关闭此页面</p>
                <script>
                    setTimeout(function() {
                        window.close();
                    }, 3000);
                </script>
                """
            else:
                self.authorization_result = {'success': False, 'error': '获取访问令牌失败'}
                return """
                <h1>❌ 获取令牌失败</h1>
                <p>请检查应用配置并重试</p>
                <p>您可以关闭此页面</p>
                """
    
    def start_auth_server(self):
        """启动授权服务器"""
        def run_server():
            self.flask_app.run(host='localhost', port=self.port, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 自动打开浏览器
        auth_url = f"http://localhost:{self.port}"
        print(f"🌐 正在打开授权页面: {auth_url}")
        webbrowser.open(auth_url)
    
    def wait_for_authorization(self, timeout=300):
        """
        等待用户完成授权
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            dict: 授权结果
        """
        print("⏳ 等待用户完成授权...")
        print("请在浏览器中完成授权流程")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.authorization_result:
                return self.authorization_result
            time.sleep(1)
        
        return {'success': False, 'error': '授权超时'}
    
    def authorize(self):
        """
        执行完整的授权流程
        
        Returns:
            KDocsAPIClient: 授权成功的客户端，失败返回None
        """
        print("🚀 开始金山文档OAuth授权流程...")
        
        # 启动授权服务器
        self.start_auth_server()
        
        # 等待授权完成
        result = self.wait_for_authorization()
        
        if result['success']:
            print("✅ 授权成功！")
            return result['client']
        else:
            print(f"❌ 授权失败: {result['error']}")
            return None


def main():
    """主函数 - 演示授权流程"""
    import os
    
    # 从环境变量获取应用凭证
    app_id = os.environ.get('KDOCS_APP_ID')
    app_secret = os.environ.get('KDOCS_APP_SECRET')
    
    if not app_id or not app_secret:
        print("❌ 请设置环境变量:")
        print("   KDOCS_APP_ID=你的应用ID")
        print("   KDOCS_APP_SECRET=你的应用密钥")
        return
    
    # 创建授权助手
    oauth_helper = KDocsOAuthHelper(app_id, app_secret)
    
    # 执行授权
    client = oauth_helper.authorize()
    
    if client:
        # 测试API调用
        file_url = "https://www.kdocs.cn/l/ctPsso05tvI4"
        file_id = client.extract_file_id_from_url(file_url)
        
        if file_id:
            print(f"📄 测试文件ID: {file_id}")
            file_info = client.get_file_info(file_id)
            if file_info:
                print(f"📋 文件名: {file_info.get('name')}")
                print(f"📊 文件类型: {file_info.get('type')}")
            else:
                print("❌ 无法获取文件信息，请检查文件权限")
    else:
        print("❌ 授权失败，无法继续")


if __name__ == "__main__":
    main()
