#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行水务数据获取并输出到文件
"""

import subprocess
import sys
import time
from datetime import datetime

def run_with_output():
    """运行脚本并捕获输出"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"run_output_{timestamp}.txt"
    
    print(f"🚀 启动水务数据获取...")
    print(f"📝 输出将保存到: {output_file}")
    
    try:
        # 运行完整版脚本
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("水务数据获取 - 最近7天数据\n")
            f.write(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            # 运行脚本
            result = subprocess.run([
                sys.executable, 'complete_8_meters_getter.py'
            ], capture_output=True, text=True, encoding='utf-8')
            
            f.write("STDOUT:\n")
            f.write("-" * 30 + "\n")
            f.write(result.stdout)
            f.write("\n\n")
            
            f.write("STDERR:\n")
            f.write("-" * 30 + "\n")
            f.write(result.stderr)
            f.write("\n\n")
            
            f.write(f"返回代码: {result.returncode}\n")
            f.write(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ 脚本执行完成")
        print(f"📊 返回代码: {result.returncode}")
        print(f"📝 详细输出已保存到: {output_file}")
        
        # 显示输出摘要
        if result.stdout:
            print(f"📤 标准输出长度: {len(result.stdout)} 字符")
            if "成功获取" in result.stdout:
                print("🎉 检测到成功获取数据的信息！")
        
        if result.stderr:
            print(f"⚠️  错误输出长度: {len(result.stderr)} 字符")
        
        # 检查是否生成了新的数据文件
        import glob
        json_files = glob.glob("*COMPLETE_8_METERS*.json") + glob.glob("*TEST_recent*.json")
        if json_files:
            latest_file = max(json_files, key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0)
            print(f"📄 最新数据文件: {latest_file}")
        
        return result.returncode == 0
        
    except Exception as e:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n错误: {e}\n")
        
        print(f"❌ 运行失败: {e}")
        return False

if __name__ == "__main__":
    import os
    
    print("="*60)
    print("🧪 水务数据获取测试运行器")
    print("="*60)
    
    success = run_with_output()
    
    print("\n" + "="*60)
    if success:
        print("✅ 运行完成！")
    else:
        print("❌ 运行中遇到问题")
    print("="*60)
