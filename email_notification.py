#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件通知模块
当GitHub Actions执行失败时发送邮件通知
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def send_notification_email(subject, message, to_email=None):
    """发送通知邮件"""
    
    # 邮件配置（需要在GitHub Secrets中配置）
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.qq.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        print("⚠️ 邮件配置不完整，跳过邮件发送")
        return False
    
    if not to_email:
        to_email = sender_email  # 默认发送给自己
    
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 邮件内容
        body = f"""
水务数据自动化系统通知

{message}

发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
此邮件由GitHub Actions自动发送
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print(f"✅ 邮件发送成功: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def notify_success(execution_summary):
    """成功执行通知"""
    subject = "✅ 水务数据更新成功"
    message = f"""
执行状态: 成功
更新时间: {execution_summary.get('execution_time', 'N/A')}
更新水表数量: {execution_summary.get('updated_meters', 'N/A')}
Excel文件: {execution_summary.get('excel_file', 'N/A')}
    """
    return send_notification_email(subject, message)

def notify_failure(error_message):
    """失败执行通知"""
    subject = "❌ 水务数据更新失败"
    message = f"""
执行状态: 失败
错误信息: {error_message}
建议操作: 请检查GitHub Actions日志或手动执行更新
    """
    return send_notification_email(subject, message)

def notify_long_time_no_update():
    """长时间未更新通知"""
    subject = "⚠️ 水务数据长时间未更新"
    message = """
系统检测到超过26小时未执行数据更新。

可能原因:
1. GitHub Actions被自动禁用
2. 外部系统维护
3. 网络连接问题

建议操作:
1. 检查GitHub Actions状态
2. 手动触发工作流
3. 检查系统日志
    """
    return send_notification_email(subject, message)
