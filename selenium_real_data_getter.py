#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Selenium浏览器自动化强制获取7月22日的真实数据
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime
import hashlib

def md5_hash(text):
    """计算MD5哈希值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def setup_driver():
    """设置Chrome驱动"""
    print("🚀 启动Chrome浏览器...")
    
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 先不使用无头模式，方便调试
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def login_to_system(driver):
    """登录到水务系统"""
    try:
        print("🔐 正在登录水务系统...")
        
        # 访问登录页面
        login_url = "http://axwater.dmas.cn/login.aspx"
        driver.get(login_url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "user"))
        )
        
        # 输入用户名和密码
        username_field = driver.find_element(By.NAME, "user")
        password_field = driver.find_element(By.NAME, "pwd")
        
        username_field.clear()
        username_field.send_keys("13509288500")
        
        password_field.clear()
        password_field.send_keys(md5_hash("288500"))  # MD5加密密码
        
        # 查找并点击登录按钮
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' or @type='button']")
        login_button.click()
        
        # 等待登录完成（检查是否跳转到主页面）
        time.sleep(3)
        
        # 检查是否登录成功
        current_url = driver.current_url
        if "frmMain.aspx" in current_url or "Main" in current_url:
            print("✅ 登录成功！")
            return True
        else:
            print(f"❌ 登录可能失败，当前URL: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

def navigate_to_report_page(driver):
    """导航到报表页面"""
    try:
        print("📊 导航到报表页面...")
        
        # 直接访问报表页面
        report_url = "http://axwater.dmas.cn/reports/FluxRpt.aspx"
        driver.get(report_url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("✅ 成功访问报表页面")
        return True
        
    except Exception as e:
        print(f"❌ 访问报表页面异常: {e}")
        return False

def set_date_and_fetch_data(driver, target_date):
    """设置日期并获取数据"""
    try:
        print(f"📅 设置目标日期: {target_date}")
        
        # 等待页面完全加载
        time.sleep(2)
        
        # 查找日期输入框
        date_inputs = driver.find_elements(By.XPATH, "//input[@type='text' and contains(@id, 'date') or contains(@name, 'date')]")
        
        if not date_inputs:
            # 尝试其他可能的日期字段
            date_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        
        print(f"🔍 找到 {len(date_inputs)} 个输入框")
        
        # 设置开始和结束日期为目标日期
        for i, input_field in enumerate(date_inputs[:2]):  # 通常前两个是开始和结束日期
            try:
                input_field.clear()
                input_field.send_keys(target_date)
                print(f"✅ 设置第 {i+1} 个日期字段: {target_date}")
            except Exception as e:
                print(f"⚠️ 设置第 {i+1} 个日期字段失败: {e}")
        
        # 查找并点击查询按钮
        query_buttons = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button' or @value='查询' or @value='Query' or contains(@onclick, 'query')]")
        
        if not query_buttons:
            # 尝试其他可能的查询按钮
            query_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '查询')] | //input[contains(@value, '查询')]")
        
        if query_buttons:
            print(f"🔍 找到 {len(query_buttons)} 个查询按钮")
            query_buttons[0].click()
            print("✅ 点击查询按钮")
        else:
            print("❌ 未找到查询按钮")
            return None
        
        # 等待数据加载
        time.sleep(5)
        
        # 查找数据表格
        tables = driver.find_elements(By.TAG_NAME, "table")
        
        print(f"🔍 找到 {len(tables)} 个表格")
        
        for i, table in enumerate(tables):
            try:
                # 获取表格的HTML内容
                table_html = table.get_attribute('outerHTML')
                
                # 检查表格是否包含水表数据
                if target_date in table_html or "流量计" in table_html or "水表" in table_html:
                    print(f"✅ 在第 {i+1} 个表格中找到相关数据")
                    
                    # 解析表格数据
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    
                    if len(rows) > 1:  # 至少有表头和数据行
                        table_data = parse_selenium_table(rows, target_date)
                        if table_data:
                            return table_data
            
            except Exception as e:
                print(f"⚠️ 解析第 {i+1} 个表格失败: {e}")
                continue
        
        print("❌ 未找到有效的数据表格")
        return None
        
    except Exception as e:
        print(f"❌ 设置日期和获取数据异常: {e}")
        return None

def parse_selenium_table(rows, target_date):
    """解析Selenium获取的表格数据"""
    try:
        if len(rows) < 2:
            return None
        
        # 解析表头
        header_row = rows[0]
        headers = []
        header_cells = header_row.find_elements(By.TAG_NAME, "th")
        if not header_cells:
            header_cells = header_row.find_elements(By.TAG_NAME, "td")
        
        for cell in header_cells:
            headers.append(cell.text.strip())
        
        print(f"📋 表头: {headers}")
        
        # 解析数据行
        data_rows = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                cells = row.find_elements(By.TAG_NAME, "th")
            
            if len(cells) >= len(headers):
                row_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        row_data[headers[i]] = cell.text.strip()
                
                # 检查是否包含目标日期或水表相关信息
                row_text = str(row_data)
                if target_date in row_text or "流量计" in row_text or any("水表" in str(v) for v in row_data.values()):
                    data_rows.append(row_data)
        
        if data_rows:
            print(f"✅ 解析到 {len(data_rows)} 行数据")
            return {
                'success': True,
                'data': {
                    'total': len(data_rows),
                    'rows': data_rows
                },
                'source': 'selenium_browser_automation',
                'target_date': target_date
            }
        
        return None
        
    except Exception as e:
        print(f"❌ 解析表格数据异常: {e}")
        return None

def force_get_real_data_selenium(target_date):
    """使用Selenium强制获取真实数据"""
    driver = None
    
    try:
        print(f"🎯 使用Selenium强制获取 {target_date} 的真实数据")
        print("=" * 60)
        
        # 设置浏览器驱动
        driver = setup_driver()
        
        # 登录系统
        if not login_to_system(driver):
            return None
        
        # 导航到报表页面
        if not navigate_to_report_page(driver):
            return None
        
        # 设置日期并获取数据
        result = set_date_and_fetch_data(driver, target_date)
        
        if result:
            print(f"🎉 成功获取 {target_date} 的真实数据！")
            
            # 保存数据到文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"SELENIUM_REAL_DATA_{target_date.replace('-', '')}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 数据已保存到: {filename}")
            return result
        else:
            print(f"❌ 未能获取 {target_date} 的真实数据")
            return None
        
    except Exception as e:
        print(f"❌ Selenium获取数据异常: {e}")
        return None
    
    finally:
        if driver:
            print("🔚 关闭浏览器...")
            driver.quit()

def main():
    """主函数"""
    target_date = "2025-07-22"
    
    print("🚀 Selenium强制获取真实数据")
    print(f"🎯 目标日期: {target_date}")
    print("=" * 60)
    
    result = force_get_real_data_selenium(target_date)
    
    if result and result.get('success'):
        print(f"\n🎉 任务完成！成功获取 {target_date} 的真实数据")
        print(f"📊 数据来源: {result.get('source', 'unknown')}")
        
        if 'data' in result and 'rows' in result['data']:
            print(f"📈 包含 {len(result['data']['rows'])} 行数据")
            
            # 显示前几行数据作为示例
            for i, row in enumerate(result['data']['rows'][:3]):
                print(f"📋 行 {i+1}: {row}")
    else:
        print(f"\n❌ 任务失败！无法获取 {target_date} 的真实数据")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
