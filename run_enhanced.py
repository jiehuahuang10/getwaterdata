#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版水务数据获取系统启动脚本
提供交互式菜单和快速启动选项
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path

def check_and_install_dependencies():
    """检查并安装依赖包"""
    print("🔍 检查Python依赖包...")
    
    try:
        # 检查关键包是否已安装
        import requests
        from bs4 import BeautifulSoup
        print("✅ 核心依赖包已安装")
        return True
    except ImportError:
        print("⚠️  需要安装依赖包")
        
        try:
            print("📦 正在安装依赖包...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ 依赖包安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖包安装失败: {e}")
            return False

def create_output_directory():
    """创建输出目录"""
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    return str(output_dir)

def get_date_range_options():
    """获取日期范围选项"""
    today = datetime.now()
    
    options = [
        {
            'name': '最近7天',
            'start': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end': (today - timedelta(days=1)).strftime('%Y-%m-%d')
        },
        {
            'name': '上个月同期',
            'start': (today - timedelta(days=37)).strftime('%Y-%m-%d'),
            'end': (today - timedelta(days=30)).strftime('%Y-%m-%d')
        },
        {
            'name': '去年同期',
            'start': (today - timedelta(days=372)).strftime('%Y-%m-%d'),
            'end': (today - timedelta(days=365)).strftime('%Y-%m-%d')
        },
        {
            'name': '2024年7月测试期',
            'start': '2024-07-24',
            'end': '2024-07-31'
        },
        {
            'name': '2024年12月测试期',
            'start': '2024-12-01',
            'end': '2024-12-07'
        }
    ]
    
    return options

def interactive_menu():
    """交互式菜单"""
    print("=" * 80)
    print("🚀 增强版水务数据获取系统")
    print("=" * 80)
    
    # 检查依赖
    if not check_and_install_dependencies():
        return False
    
    # 创建输出目录
    output_dir = create_output_directory()
    print(f"📁 输出目录: {output_dir}")
    
    while True:
        print("\n请选择运行模式：")
        print("1. 快速运行（使用默认配置）")
        print("2. 自定义配置运行")
        print("3. 指定日期范围运行")
        print("4. 测试登录功能")
        print("5. 查看系统信息")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                return True
                
            elif choice == "1":
                return run_quick_mode(output_dir)
                
            elif choice == "2":
                return run_custom_mode(output_dir)
                
            elif choice == "3":
                return run_date_range_mode(output_dir)
                
            elif choice == "4":
                return test_login()
                
            elif choice == "5":
                show_system_info()
                
            else:
                print("❌ 请输入有效的选择 (0-5)")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消，再见！")
            return True

def run_quick_mode(output_dir):
    """快速运行模式"""
    print("\n🚀 快速运行模式")
    print("使用默认水表ID和自动日期范围...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f"{output_dir}/water_data_quick_{timestamp}.json"
    csv_file = f"{output_dir}/water_data_quick_{timestamp}.csv"
    
    cmd = [
        sys.executable, "water_data_enhanced.py",
        "--json", json_file,
        "--csv", csv_file,
        "--log-level", "INFO"
    ]
    
    return run_command(cmd)

def run_custom_mode(output_dir):
    """自定义配置运行模式"""
    print("\n⚙️ 自定义配置模式")
    
    # 获取用户输入
    username = input("用户名 (留空使用默认): ").strip()
    password = input("密码 (留空使用默认): ").strip()
    
    meters_input = input("水表ID列表 (用逗号分隔，留空使用默认): ").strip()
    
    start_date = input("开始日期 (YYYY-MM-DD，留空自动选择): ").strip()
    end_date = input("结束日期 (YYYY-MM-DD，留空自动选择): ").strip()
    
    # 构建命令
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f"{output_dir}/water_data_custom_{timestamp}.json"
    csv_file = f"{output_dir}/water_data_custom_{timestamp}.csv"
    
    cmd = [
        sys.executable, "water_data_enhanced.py",
        "--json", json_file,
        "--csv", csv_file,
        "--log-level", "INFO"
    ]
    
    if username:
        cmd.extend(["--username", username])
    if password:
        cmd.extend(["--password", password])
    if meters_input:
        cmd.extend(["--meters", meters_input])
    if start_date:
        cmd.extend(["--start-date", start_date])
    if end_date:
        cmd.extend(["--end-date", end_date])
    
    return run_command(cmd)

def run_date_range_mode(output_dir):
    """日期范围选择模式"""
    print("\n📅 日期范围选择模式")
    
    date_options = get_date_range_options()
    
    print("请选择日期范围：")
    for i, option in enumerate(date_options, 1):
        print(f"{i}. {option['name']} ({option['start']} 到 {option['end']})")
    
    try:
        choice = int(input(f"\n请选择 (1-{len(date_options)}): ").strip())
        
        if 1 <= choice <= len(date_options):
            selected = date_options[choice - 1]
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_file = f"{output_dir}/water_data_{selected['start']}_{selected['end']}.json"
            csv_file = f"{output_dir}/water_data_{selected['start']}_{selected['end']}.csv"
            
            cmd = [
                sys.executable, "water_data_enhanced.py",
                "--start-date", selected['start'],
                "--end-date", selected['end'],
                "--json", json_file,
                "--csv", csv_file,
                "--log-level", "INFO"
            ]
            
            print(f"\n🎯 使用日期范围: {selected['name']}")
            return run_command(cmd)
        else:
            print("❌ 无效的选择")
            return False
            
    except (ValueError, KeyboardInterrupt):
        print("❌ 无效的输入")
        return False

def test_login():
    """测试登录功能"""
    print("\n🔐 测试登录功能")
    
    cmd = [
        sys.executable, "-c",
        """
from water_data_enhanced import EnhancedWaterDataScraper
import sys

scraper = EnhancedWaterDataScraper()
if scraper.login():
    print("✅ 登录测试成功！")
    sys.exit(0)
else:
    print("❌ 登录测试失败！")
    sys.exit(1)
        """
    ]
    
    return run_command(cmd)

def show_system_info():
    """显示系统信息"""
    print("\n📋 系统信息")
    print("=" * 50)
    
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查关键文件
    key_files = [
        "water_data_enhanced.py",
        "requirements.txt", 
        "config.py",
        "config.env.example"
    ]
    
    print("\n📁 关键文件检查:")
    for file in key_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (缺失)")
    
    # 检查环境变量
    env_vars = ['WATER_USERNAME', 'WATER_PASSWORD', 'WATER_BASE_URL']
    print("\n🔧 环境变量检查:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"✅ {var}: ***")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: 未设置")
    
    input("\n按回车键继续...")

def run_command(cmd):
    """运行命令"""
    print(f"\n🔧 执行命令: {' '.join(cmd)}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 80)
        print("✅ 命令执行成功！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 命令执行失败，退出码: {e.returncode}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
        return False

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='增强版水务数据获取系统启动器',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--quick', action='store_true',
                       help='快速运行模式（跳过交互菜单）')
    parser.add_argument('--install-deps', action='store_true',
                       help='仅安装依赖包然后退出')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    if args.install_deps:
        print("📦 安装依赖包模式")
        success = check_and_install_dependencies()
        sys.exit(0 if success else 1)
    
    if args.quick:
        print("⚡ 快速运行模式")
        if check_and_install_dependencies():
            output_dir = create_output_directory()
            success = run_quick_mode(output_dir)
            sys.exit(0 if success else 1)
        else:
            sys.exit(1)
    
    # 交互式菜单
    try:
        success = interactive_menu()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 用户取消，再见！")
        sys.exit(0)

if __name__ == "__main__":
    main()
