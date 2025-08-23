#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
"""

import sys
import subprocess

def install_requirements():
    """安装所需的Python包"""
    print("正在安装所需的Python包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("水务数据获取系统")
    print("=" * 60)
    
    # 检查是否需要安装依赖
    try:
        import selenium
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ 依赖包已安装")
    except ImportError:
        print("⚠️  需要安装依赖包")
        if not install_requirements():
            return
    
    # 导入并运行主程序
    try:
        from water_data_scraper import WaterDataScraper
        
        scraper = WaterDataScraper()
        
        # 设置浏览器驱动
        if not scraper.setup_driver():
            print("❌ 浏览器驱动设置失败")
            return
        
        # 执行完整的数据获取流程
        if scraper.get_water_data():
            print("✅ 数据获取流程完成！")
            input("按回车键关闭浏览器...")
        else:
            print("❌ 数据获取流程失败")
            
        scraper.close()
        
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")

if __name__ == "__main__":
    main()