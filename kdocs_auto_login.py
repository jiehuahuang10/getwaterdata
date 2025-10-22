#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs自动登录和文档编辑
实现完整的登录流程和数据写入
"""

import requests
import json
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KDocsAutoLogin:
    def __init__(self):
        """
        初始化KDocs自动登录客户端
        """
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Origin': 'https://www.kdocs.cn',
            'Referer': 'https://www.kdocs.cn/'
        })
        
        # 目标文档信息（新文档）
        self.target_link_id = "cqagXO1NDs4P"
        self.target_file_id = "456521205074"  # 从网络请求中获取的真实文件ID
        
        # 登录状态
        self.is_logged_in = False
        self.user_info = None
    
    def login_with_phone(self, phone, password):
        """
        使用手机号和密码登录KDocs
        """
        logger.info("开始登录KDocs...")
        logger.info(f"手机号: {phone}")
        
        # KDocs登录API端点
        login_url = "https://account.kdocs.cn/api/v3/signIn"
        
        # 构建登录请求
        login_data = {
            "account": phone,
            "password": password,
            "type": "phone"  # 手机号登录
        }
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=10)
            logger.info(f"登录响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"登录响应: {result}")
                
                if result.get('result') == 'ok' or result.get('code') == 0:
                    logger.info("登录成功!")
                    self.is_logged_in = True
                    self.user_info = result.get('data', {})
                    
                    # 保存Cookie
                    self.save_cookies()
                    
                    return {'success': True, 'user_info': self.user_info}
                else:
                    error_msg = result.get('msg', '未知错误')
                    logger.error(f"登录失败: {error_msg}")
                    return {'success': False, 'error': error_msg}
            else:
                logger.error(f"登录请求失败: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"登录时出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def login_with_wechat_scan(self):
        """
        使用微信扫码登录（需要用户扫描二维码）
        """
        logger.info("准备微信扫码登录...")
        
        # 获取二维码
        qr_url = "https://account.kdocs.cn/api/v3/wechat/qrcode"
        
        try:
            response = self.session.get(qr_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                qr_code_url = result.get('qrcode_url')
                ticket = result.get('ticket')
                
                logger.info(f"请使用微信扫描以下二维码登录:")
                logger.info(f"二维码URL: {qr_code_url}")
                logger.info(f"或访问: {qr_code_url}")
                
                # 轮询检查登录状态
                check_url = f"https://account.kdocs.cn/api/v3/wechat/check?ticket={ticket}"
                
                for i in range(60):  # 最多等待60秒
                    time.sleep(1)
                    check_response = self.session.get(check_url, timeout=5)
                    
                    if check_response.status_code == 200:
                        check_result = check_response.json()
                        
                        if check_result.get('status') == 'success':
                            logger.info("微信扫码登录成功!")
                            self.is_logged_in = True
                            self.user_info = check_result.get('data', {})
                            self.save_cookies()
                            return {'success': True, 'user_info': self.user_info}
                        elif check_result.get('status') == 'scanned':
                            logger.info("二维码已扫描，等待确认...")
                    
                    if i % 10 == 0:
                        logger.info(f"等待扫码... ({i}/60秒)")
                
                logger.error("扫码超时")
                return {'success': False, 'error': '扫码超时'}
                
        except Exception as e:
            logger.error(f"微信扫码登录出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_login_status(self):
        """
        检查当前登录状态
        """
        logger.info("检查登录状态...")
        
        check_url = "https://account.kdocs.cn/api/v3/islogin"
        
        try:
            response = self.session.get(check_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') == 'ok' or result.get('isLogin'):
                    logger.info("已登录")
                    self.is_logged_in = True
                    return {'success': True, 'logged_in': True}
                else:
                    logger.info("未登录")
                    self.is_logged_in = False
                    return {'success': True, 'logged_in': False}
            else:
                logger.warning(f"检查登录状态失败: {response.status_code}")
                return {'success': False, 'error': '无法检查登录状态'}
                
        except Exception as e:
            logger.error(f"检查登录状态出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def save_cookies(self):
        """
        保存Cookie到文件
        """
        try:
            cookies = self.session.cookies.get_dict()
            
            with open('kdocs_cookies.json', 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            logger.info("Cookie已保存到 kdocs_cookies.json")
            
        except Exception as e:
            logger.error(f"保存Cookie失败: {e}")
    
    def load_cookies(self):
        """
        从文件加载Cookie
        """
        try:
            with open('kdocs_cookies.json', 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            logger.info("Cookie已从文件加载")
            
            # 检查登录状态
            status = self.check_login_status()
            return status
            
        except FileNotFoundError:
            logger.warning("Cookie文件不存在")
            return {'success': False, 'error': 'Cookie文件不存在'}
        except Exception as e:
            logger.error(f"加载Cookie失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_document_info(self):
        """
        获取文档信息（测试登录是否有效）
        """
        logger.info("获取文档信息...")
        
        url = f"https://drive.kdocs.cn/api/v5/links/{self.target_link_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info("成功获取文档信息!")
                logger.info(f"文档名称: {data.get('fileinfo', {}).get('fname')}")
                logger.info(f"用户权限: {data.get('user_permission')}")
                logger.info(f"可写入: {data.get('user_acl', {}).get('update')}")
                
                return {'success': True, 'data': data}
            else:
                logger.error(f"获取文档信息失败: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"获取文档信息出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def write_water_data(self, water_data, target_date=None):
        """
        写入水务数据到KDocs文档
        
        Args:
            water_data: dict, 水表数据 {"1": 1234.56, "2": 2345.67, ...}
            target_date: str, 目标日期 "YYYY-MM-DD"
        """
        if not self.is_logged_in:
            logger.error("未登录，无法写入数据")
            return {'success': False, 'error': '未登录'}
        
        logger.info("开始写入水务数据...")
        
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"目标日期: {target_date}")
        logger.info(f"水表数据: {water_data}")
        
        # 使用会话API写入数据
        session_url = f"https://www.kdocs.cn/api/v3/office/session/{self.target_link_id}/et"
        
        # 构建写入请求
        # 注意：这里需要根据KDocs的实际API格式调整
        write_data = {
            "action": "update_cells",
            "date": target_date,
            "data": water_data
        }
        
        try:
            response = self.session.post(session_url, json=write_data, timeout=10)
            
            logger.info(f"写入响应状态码: {response.status_code}")
            logger.info(f"写入响应: {response.text[:200]}...")
            
            if response.status_code in [200, 201]:
                logger.info("数据写入成功!")
                return {'success': True}
            else:
                logger.error(f"数据写入失败: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"写入数据时出错: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """
    主函数 - 演示登录流程
    """
    print("=" * 60)
    print("KDocs自动登录和文档编辑工具")
    print("=" * 60)
    print()
    
    client = KDocsAutoLogin()
    
    # 方法1: 尝试从文件加载Cookie
    print("方法1: 尝试加载已保存的Cookie...")
    result = client.load_cookies()
    
    if result.get('success') and result.get('logged_in'):
        print("使用已保存的Cookie登录成功!")
    else:
        print("Cookie无效或不存在，需要重新登录")
        print()
        
        # 方法2: 提供登录选项
        print("请选择登录方式:")
        print("1. 手机号+密码登录")
        print("2. 微信扫码登录")
        print("3. 手动提供Cookie")
        print()
        
        choice = input("请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            phone = input("请输入手机号: ").strip()
            password = input("请输入密码: ").strip()
            
            result = client.login_with_phone(phone, password)
            
            if result.get('success'):
                print("登录成功!")
            else:
                print(f"登录失败: {result.get('error')}")
                return
        
        elif choice == "2":
            result = client.login_with_wechat_scan()
            
            if result.get('success'):
                print("登录成功!")
            else:
                print(f"登录失败: {result.get('error')}")
                return
        
        elif choice == "3":
            print()
            print("请按以下步骤操作:")
            print("1. 在浏览器中登录 https://www.kdocs.cn")
            print("2. 打开浏览器开发者工具 (F12)")
            print("3. 切换到 Network 标签")
            print("4. 刷新页面")
            print("5. 找到任意请求，复制 Cookie 请求头的值")
            print()
            
            cookie_string = input("请粘贴Cookie字符串: ").strip()
            
            # 解析Cookie字符串
            cookies = {}
            for item in cookie_string.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies[name] = value
                    client.session.cookies.set(name, value)
            
            # 保存Cookie
            client.save_cookies()
            
            # 检查登录状态
            result = client.check_login_status()
            
            if result.get('logged_in'):
                print("Cookie设置成功，已登录!")
            else:
                print("Cookie无效，请重试")
                return
        
        else:
            print("无效的选择")
            return
    
    print()
    print("=" * 60)
    print("测试文档访问权限")
    print("=" * 60)
    
    # 测试获取文档信息
    doc_result = client.get_document_info()
    
    if doc_result.get('success'):
        print("文档访问测试成功!")
        
        # 测试写入数据
        print()
        print("=" * 60)
        print("测试数据写入")
        print("=" * 60)
        
        test_data = {
            "1": 1234.56,
            "2": 2345.67,
            "3": 3456.78,
            "4": 4567.89,
            "5": 5678.90,
            "6": 6789.01,
            "7": 7890.12,
            "8": 8901.23
        }
        
        write_result = client.write_water_data(test_data)
        
        if write_result.get('success'):
            print("数据写入测试成功!")
        else:
            print(f"数据写入测试失败: {write_result.get('error')}")
    else:
        print(f"文档访问测试失败: {doc_result.get('error')}")
    
    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

