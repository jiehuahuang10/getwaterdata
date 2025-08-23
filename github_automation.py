#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 自动化执行脚本
每天下午6点自动执行，更新石滩供水服务部每日总供水情况.xlsx
"""

import os
import sys
from datetime import datetime, timedelta
import logging
from integrated_excel_updater import update_excel_with_real_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('github_automation.log', encoding='utf-8')
    ]
)

def main():
    """主执行函数"""
    try:
        # 获取昨天的日期（因为是下午6点执行，更新昨天的数据）
        yesterday = datetime.now() - timedelta(days=1)
        target_date = yesterday.strftime('%Y-%m-%d')
        
        logging.info(f"🚀 开始GitHub Actions自动执行")
        logging.info(f"📅 目标日期: {target_date}")
        logging.info(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查必要的环境变量
        required_vars = ['LOGIN_URL', 'USERNAME', 'PASSWORD', 'REPORT_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logging.error(f"❌ 缺少必要的环境变量: {missing_vars}")
            sys.exit(1)
        
        logging.info("✅ 环境变量检查通过")
        
        # 执行数据更新
        logging.info("🎯 开始执行水务数据更新...")
        result = update_excel_with_real_data(target_date)
        
        if result['success']:
            logging.info(f"✅ 数据更新成功!")
            logging.info(f"📊 更新了 {result.get('updated_meters', 0)} 个水表的数据")
            logging.info(f"📝 消息: {result.get('message', '')}")
            
            # 检查Excel文件是否存在
            excel_file = 'excel_exports/石滩供水服务部每日总供水情况.xlsx'
            if os.path.exists(excel_file):
                file_size = os.path.getsize(excel_file)
                logging.info(f"📁 Excel文件大小: {file_size} 字节")
            else:
                logging.warning("⚠️ Excel文件不存在")
            
            # 创建执行结果摘要
            create_execution_summary(target_date, result, True)
            
        else:
            logging.error(f"❌ 数据更新失败!")
            logging.error(f"🔍 错误信息: {result.get('error', '未知错误')}")
            
            # 创建执行结果摘要
            create_execution_summary(target_date, result, False)
            
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"💥 执行过程中发生异常: {str(e)}")
        import traceback
        logging.error(f"📋 详细错误信息:\n{traceback.format_exc()}")
        
        # 创建错误摘要
        create_execution_summary(target_date if 'target_date' in locals() else 'unknown', 
                                {'error': str(e)}, False)
        sys.exit(1)

def create_execution_summary(target_date, result, success):
    """创建执行结果摘要文件"""
    try:
        summary = {
            'execution_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'target_date': target_date,
            'success': success,
            'result': result
        }
        
        import json
        with open('last_execution_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        logging.info("📄 执行摘要已保存到 last_execution_summary.json")
        
    except Exception as e:
        logging.error(f"⚠️ 无法创建执行摘要: {str(e)}")

def test_connection():
    """测试连接和环境"""
    try:
        logging.info("🔍 测试网络连接和环境...")
        
        # 测试导入
        from force_real_data_web import force_get_real_data_for_web
        from specific_excel_writer import SpecificExcelWriter
        
        logging.info("✅ 模块导入成功")
        
        # 测试网络连接
        import requests
        response = requests.get('https://www.baidu.com', timeout=10)
        if response.status_code == 200:
            logging.info("✅ 网络连接正常")
        else:
            logging.warning("⚠️ 网络连接可能有问题")
            
    except Exception as e:
        logging.error(f"❌ 环境测试失败: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🌊 水务数据自动化更新系统")
    print("🤖 GitHub Actions 执行版本")
    print("=" * 60)
    
    # 测试环境
    if not test_connection():
        sys.exit(1)
    
    # 执行主程序
    main()
    
    print("=" * 60)
    print("✅ 自动化执行完成")
    print("=" * 60)
