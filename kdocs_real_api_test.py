#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDocs API端点分析和测试
基于浏览器网络请求发现的真实API端点
"""

import requests
import json
import time
from datetime import datetime

class KDocsRealAPI:
    def __init__(self):
        """
        初始化KDocs真实API客户端
        基于浏览器网络请求分析
        """
        self.session = requests.Session()
        
        # 从网络请求中发现的关键API端点
        self.discovered_apis = {
            # 文件操作API
            "file_open": "https://www.kdocs.cn/api/v3/office/file/{file_id}/open/et",
            "file_session": "https://www.kdocs.cn/api/v3/office/session/{file_id}/et",
            "file_privilege": "https://www.kdocs.cn/api/v3/office/file/{file_id}/privilege_list",
            "file_fonts": "https://www.kdocs.cn/api/v3/office/file/{file_id}/fonts_config/type/wps",
            "file_copy_ticket": "https://www.kdocs.cn/api/v3/office/file/{file_id}/copy/ticket",
            "file_features": "https://www.kdocs.cn/api/v3/office/file/{file_id}/features",
            "file_comments": "https://www.kdocs.cn/api/v3/office/file/{file_id}/comments/all",
            "file_custom_attr": "https://www.kdocs.cn/api/v3/office/file/{file_id}/custom/attribute",
            
            # 用户和认证API
            "user_login_check": "https://account.kdocs.cn/api/v3/islogin",
            "user_info": "https://drive.kdocs.cn/api/v3/userinfo",
            "user_vip_info": "https://www.kdocs.cn/api/kdocs/vipinfo",
            
            # 文档链接API
            "link_info": "https://drive.kdocs.cn/api/v5/links/{link_id}",
            "link_collaborator": "https://www.kdocs.cn/kfc/miniprovider/v1/links/{link_id}/collaborator_switch",
            "link_watermark": "https://www.kdocs.cn/kfc/miniprovider/v1/doc/watermark",
            
            # 标签和文件管理API
            "file_tags": "https://www.kdocs.cn/api/kdocs/tags/1/files",
            
            # AI和特权API
            "ai_privilege": "https://www.kdocs.cn/api/v3/kai/feature/available_privilege",
            "personal_ai": "https://personal-ai-bus.kdocs.cn/privilege_auth/v2/can_use"
        }
        
        # 目标文档信息（从您的KDocs链接提取）
        self.target_file_id = "407757026333"  # 从网络请求中发现的真实文件ID
        self.target_link_id = "ctPsso05tvI4"  # 链接ID
        
        # 设置通用请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.kdocs.cn/l/ctPsso05tvI4'
        })
    
    def test_file_apis(self):
        """
        测试文件相关API
        """
        print("=" * 60)
        print("测试KDocs文件API")
        print("=" * 60)
        
        file_id = self.target_file_id
        
        # 测试各个文件API
        test_cases = [
            ("文件打开", self.discovered_apis["file_open"].format(file_id=file_id)),
            ("文件会话", self.discovered_apis["file_session"].format(file_id=file_id) + "?first"),
            ("文件权限", self.discovered_apis["file_privilege"].format(file_id=file_id)),
            ("文件字体配置", self.discovered_apis["file_fonts"].format(file_id=file_id)),
            ("文件复制票据", self.discovered_apis["file_copy_ticket"].format(file_id=file_id)),
            ("文件特性", self.discovered_apis["file_features"].format(file_id=file_id) + "?includes=file_access"),
            ("文件评论", self.discovered_apis["file_comments"].format(file_id=file_id) + "?review_status=1,2"),
            ("文件自定义属性", self.discovered_apis["file_custom_attr"].format(file_id=file_id) + "?keys=ETHasShowDataAnalysisTips&namespace=user")
        ]
        
        for name, url in test_cases:
            print(f"测试 {name}:")
            try:
                response = self.session.get(url, timeout=10)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  成功! 数据类型: {type(data)}")
                        if isinstance(data, dict):
                            print(f"  键: {list(data.keys())[:5]}...")
                        elif isinstance(data, list):
                            print(f"  列表长度: {len(data)}")
                        print(f"  响应片段: {str(data)[:200]}...")
                    except:
                        print(f"  成功! 响应长度: {len(response.text)}")
                        print(f"  响应片段: {response.text[:200]}...")
                elif response.status_code == 401:
                    print(f"  需要认证")
                elif response.status_code == 403:
                    print(f"  权限不足")
                else:
                    print(f"  其他状态: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  请求失败: {e}")
            print()
    
    def test_user_apis(self):
        """
        测试用户相关API
        """
        print("=" * 60)
        print("测试KDocs用户API")
        print("=" * 60)
        
        test_cases = [
            ("登录检查", self.discovered_apis["user_login_check"]),
            ("用户信息", self.discovered_apis["user_info"]),
            ("VIP信息", self.discovered_apis["user_vip_info"])
        ]
        
        for name, url in test_cases:
            print(f"测试 {name}:")
            try:
                response = self.session.get(url, timeout=10)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  成功! 数据: {data}")
                    except:
                        print(f"  成功! 响应: {response.text[:200]}...")
                else:
                    print(f"  状态: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  请求失败: {e}")
            print()
    
    def test_link_apis(self):
        """
        测试链接相关API
        """
        print("=" * 60)
        print("测试KDocs链接API")
        print("=" * 60)
        
        link_id = self.target_link_id
        file_id = self.target_file_id
        
        test_cases = [
            ("链接信息", self.discovered_apis["link_info"].format(link_id=link_id)),
            ("协作者切换", self.discovered_apis["link_collaborator"].format(link_id=link_id)),
            ("水印信息", self.discovered_apis["link_watermark"] + f"?fid={file_id}&cid={link_id}&publish_id=&scene=0")
        ]
        
        for name, url in test_cases:
            print(f"测试 {name}:")
            try:
                response = self.session.get(url, timeout=10)
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  成功! 数据: {data}")
                    except:
                        print(f"  成功! 响应: {response.text[:200]}...")
                else:
                    print(f"  状态: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"  请求失败: {e}")
            print()
    
    def test_write_operations(self):
        """
        测试可能的写入操作
        """
        print("=" * 60)
        print("测试KDocs写入操作")
        print("=" * 60)
        
        file_id = self.target_file_id
        
        # 尝试POST到会话API（这可能是写入数据的方式）
        session_url = self.discovered_apis["file_session"].format(file_id=file_id)
        
        print(f"测试文件会话POST:")
        try:
            # 尝试发送一个简单的数据更新请求
            test_data = {
                "action": "test",
                "data": "测试数据写入"
            }
            
            response = self.session.post(session_url, json=test_data, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"  写入可能成功! 响应: {response.text[:200]}...")
            elif response.status_code == 401:
                print(f"  需要认证")
            elif response.status_code == 403:
                print(f"  权限不足")
            else:
                print(f"  响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  请求失败: {e}")
        print()
        
        # 测试自定义属性写入
        custom_attr_url = self.discovered_apis["file_custom_attr"].format(file_id=file_id)
        
        print(f"测试自定义属性写入:")
        try:
            test_attr_data = {
                "keys": "test_water_data",
                "namespace": "user",
                "value": "测试水务数据"
            }
            
            response = self.session.post(custom_attr_url, json=test_attr_data, timeout=10)
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  请求失败: {e}")
        print()
    
    def run_full_analysis(self):
        """
        运行完整的KDocs API分析
        """
        print("KDocs真实API分析工具")
        print(f"目标文件ID: {self.target_file_id}")
        print(f"目标链接ID: {self.target_link_id}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 测试用户API
        self.test_user_apis()
        
        # 步骤2: 测试文件API
        self.test_file_apis()
        
        # 步骤3: 测试链接API
        self.test_link_apis()
        
        # 步骤4: 测试写入操作
        self.test_write_operations()
        
        print("=" * 60)
        print("KDocs API分析完成")
        print("=" * 60)
        print("基于真实网络请求的API端点测试完成!")
        print("如果发现可用的写入API，可以集成到水务数据自动化系统!")

def main():
    """
    主函数
    """
    analyzer = KDocsRealAPI()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
