#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查新KDocs文档权限
"""

import requests
import json

def check_kdocs_permission(link_id):
    """
    检查KDocs文档权限
    """
    print(f"检查KDocs文档权限: {link_id}")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': f'https://www.kdocs.cn/l/{link_id}'
    })
    
    # 测试链接信息API
    url = f"https://drive.kdocs.cn/api/v5/links/{link_id}"
    
    try:
        response = session.get(url, timeout=10)
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 文档信息
            fileinfo = data.get('fileinfo', {})
            print(f"文档名称: {fileinfo.get('fname', 'unknown')}")
            print(f"文件ID: {fileinfo.get('id', 'unknown')}")
            print(f"文件大小: {fileinfo.get('fsize', 0)} 字节")
            print(f"版本: {fileinfo.get('fver', 0)}")
            print()
            
            # 链接信息
            linkinfo = data.get('linkinfo', {})
            print(f"链接ID: {linkinfo.get('sid', 'unknown')}")
            print(f"链接权限: {linkinfo.get('link_permission', 'unknown')}")
            print(f"状态: {linkinfo.get('status', 'unknown')}")
            print()
            
            # 用户权限
            user_permission = data.get('user_permission', 'unknown')
            user_acl = data.get('user_acl', {})
            
            print(f"用户权限: {user_permission}")
            print("用户ACL:")
            print(f"  可读 (read): {user_acl.get('read', 0)}")
            print(f"  可写 (update): {user_acl.get('update', 0)}")
            print(f"  可下载 (download): {user_acl.get('download', 0)}")
            print(f"  可删除 (delete): {user_acl.get('delete', 0)}")
            print(f"  可分享 (share): {user_acl.get('share', 0)}")
            print(f"  可复制 (copy): {user_acl.get('copy', 0)}")
            print()
            
            # 判断权限
            can_write = user_acl.get('update', 0) == 1
            
            if can_write:
                print("权限状态: 可编辑")
                print("可以通过API写入数据!")
            else:
                print("权限状态: 只读")
                print("无法通过API写入数据")
            
            return {
                'success': True,
                'can_write': can_write,
                'permission': user_permission,
                'file_id': fileinfo.get('id'),
                'link_id': linkinfo.get('sid'),
                'file_name': fileinfo.get('fname')
            }
            
        elif response.status_code == 403:
            print("API返回403 - 可能需要登录或文档不公开")
            print("尝试直接访问文档页面...")
            
            # 尝试访问文档页面
            doc_url = f"https://www.kdocs.cn/l/{link_id}"
            doc_response = session.get(doc_url, timeout=10)
            
            if doc_response.status_code == 200:
                content = doc_response.text
                
                # 检查页面内容
                if '只读' in content or 'readonly' in content.lower():
                    print("文档页面可访问，但可能是只读权限")
                    return {'success': True, 'can_write': False, 'permission': 'readonly'}
                elif '编辑' in content or 'edit' in content.lower():
                    print("文档页面可访问，可能有编辑权限")
                    return {'success': True, 'can_write': True, 'permission': 'editable'}
                else:
                    print("文档页面可访问，权限未知")
                    return {'success': True, 'can_write': False, 'permission': 'unknown'}
            else:
                print(f"文档页面访问失败: {doc_response.status_code}")
                return {'success': False, 'error': 'document_not_accessible'}
        else:
            print(f"API请求失败: {response.text[:200]}")
            return {'success': False, 'error': response.text}
            
    except Exception as e:
        print(f"检查权限时出错: {e}")
        return {'success': False, 'error': str(e)}

def main():
    # 检查新文档
    new_link_id = "cqagXO1NDs4P"
    print("检查新KDocs文档")
    print()
    
    result = check_kdocs_permission(new_link_id)
    
    print()
    print("=" * 60)
    print("检查结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print()
    print("=" * 60)
    print("对比旧文档")
    print()
    
    old_link_id = "ctPsso05tvI4"
    old_result = check_kdocs_permission(old_link_id)
    
    print()
    print("=" * 60)
    print("旧文档结果:")
    print(json.dumps(old_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

