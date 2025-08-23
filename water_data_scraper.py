#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据获取脚本
功能：自动登录广州增城自来水公司ThinkWater智慧水网系统并获取数据
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class WaterDataScraper:
    def __init__(self):
        """初始化爬虫"""
        self.driver = None
        self.wait = None
        
        # 系统登录信息
        self.login_url = "http://axwater.dmas.cn/Login.aspx"
        self.username = "13509288500"
        self.password = "288500"
        
    def setup_driver(self):
        """设置浏览器驱动"""
        print("正在设置浏览器驱动...")
        
        # Chrome浏览器选项
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        # 如果不需要看到浏览器界面，可以取消下面这行的注释
        # chrome_options.add_argument('--headless')
        
        # 设置用户代理
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            # 自动下载并初始化Chrome驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.maximize_window()
            
            # 设置等待时间
            self.wait = WebDriverWait(self.driver, 10)
            print("浏览器驱动设置成功")
            return True
            
        except Exception as e:
            print(f"浏览器驱动设置失败: {e}")
            print("请确保已安装ChromeDriver并添加到PATH环境变量中")
            return False
    
    def login(self):
        """登录系统"""
        print("开始登录系统...")
        
        try:
            # 打开登录页面
            print(f"正在访问登录页面: {self.login_url}")
            self.driver.get(self.login_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找用户名输入框
            print("正在输入用户名...")
            username_selectors = [
                'input[name="txtUserName"]',
                'input[id="txtUserName"]', 
                'input[type="text"]',
                '#txtUserName'
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"找到用户名输入框: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_input:
                print("未找到用户名输入框，尝试其他方法...")
                # 打印页面源码以便调试
                print("页面标题:", self.driver.title)
                # 查找所有input元素
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                print(f"页面中共找到 {len(inputs)} 个input元素")
                for i, inp in enumerate(inputs):
                    print(f"Input {i}: type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', id='{inp.get_attribute('id')}'")
                return False
            
            # 清空并输入用户名
            username_input.clear()
            username_input.send_keys(self.username)
            print(f"用户名输入完成: {self.username}")
            
            # 查找密码输入框
            print("正在输入密码...")
            password_selectors = [
                'input[name="txtPassword"]',
                'input[id="txtPassword"]',
                'input[type="password"]',
                '#txtPassword'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"找到密码输入框: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_input:
                print("未找到密码输入框")
                return False
            
            # 清空并输入密码
            password_input.clear()
            password_input.send_keys(self.password)
            print("密码输入完成")
            
            # 查找登录按钮
            print("正在查找登录按钮...")
            login_button_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'input[value*="登录"]',
                'input[value*="登錄"]',
                'button:contains("登录")',
                '#btnLogin',
                'input[name="btnLogin"]'
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"找到登录按钮: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                print("未找到登录按钮，尝试查找所有可能的按钮...")
                buttons = self.driver.find_elements(By.TAG_NAME, "input")
                buttons.extend(self.driver.find_elements(By.TAG_NAME, "button"))
                for i, btn in enumerate(buttons):
                    btn_type = btn.get_attribute('type')
                    btn_value = btn.get_attribute('value')
                    btn_text = btn.text
                    print(f"Button {i}: type='{btn_type}', value='{btn_value}', text='{btn_text}'")
                return False
            
            # 点击登录按钮
            print("正在点击登录按钮...")
            login_button.click()
            
            # 等待登录完成
            print("等待登录完成...")
            time.sleep(5)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            print(f"当前页面URL: {current_url}")
            
            if "Login.aspx" not in current_url:
                print("登录成功！")
                print(f"当前页面标题: {self.driver.title}")
                return True
            else:
                print("登录失败，仍在登录页面")
                # 检查是否有错误信息
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .warning")
                    for error in error_elements:
                        if error.is_displayed() and error.text.strip():
                            print(f"错误信息: {error.text}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"登录过程中发生错误: {e}")
            return False
    
    def navigate_to_reports(self):
        """导航到报表页面"""
        print("正在导航到报表页面...")
        
        try:
            # 等待页面完全加载
            time.sleep(3)
            
            # 查找报表菜单项
            report_selectors = [
                'a[href*="Report"]',
                'a:contains("报表")',
                '*[onclick*="Report"]',
                'li:contains("报表")',
                '.menu-item:contains("报表")',
                'span:contains("报表")'
            ]
            
            report_element = None
            for selector in report_selectors:
                try:
                    if ":contains" in selector:
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '报表')]")
                        if elements:
                            report_element = elements[0]
                            print(f"找到报表菜单: XPath")
                            break
                    else:
                        report_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"找到报表菜单: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if not report_element:
                print("未找到报表菜单，尝试查找所有可能的菜单项...")
                # 查找所有包含"报表"文字的元素
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '报表')]")
                print(f"找到 {len(all_elements)} 个包含'报表'的元素")
                for i, elem in enumerate(all_elements):
                    try:
                        if elem.is_displayed():
                            print(f"元素 {i}: {elem.tag_name}, text='{elem.text}', visible={elem.is_displayed()}")
                            if not report_element and elem.is_displayed():
                                report_element = elem
                    except:
                        continue
            
            if not report_element:
                return False
            
            # 点击报表菜单
            print("正在点击报表菜单...")
            self.driver.execute_script("arguments[0].click();", report_element)
            time.sleep(3)
            
            print("成功导航到报表页面")
            return True
            
        except Exception as e:
            print(f"导航到报表页面失败: {e}")
            return False
    
    def select_water_meters(self):
        """选择指定的8个水表"""
        print("正在选择指定的水表...")
        
        # 目标水表列表
        target_meters = [
            "126118100026",  # 荔新大道DN1200流量计
            "126118100030",  # 新塘大道医院DN800流量计  
            "126233040233",  # 宁西总表DN1200
            "2190066",       # 三江新总表DN800
            "2190493",       # 沙庄总表
            "2501200108",    # 2501200108
            "2520005",       # 如丰大道600监控表
            "2520006"        # 三棒桥600监控表
        ]
        
        try:
            selected_count = 0
            
            # 查找并选择每个水表
            for meter_id in target_meters:
                try:
                    # 多种选择器策略查找水表
                    meter_selectors = [
                        f'input[value="{meter_id}"]',
                        f'*[data-id="{meter_id}"]',
                        f'tr:contains("{meter_id}") input[type="checkbox"]',
                        f'*[onclick*="{meter_id}"]'
                    ]
                    
                    meter_element = None
                    for selector in meter_selectors:
                        try:
                            if ":contains" in selector:
                                # 使用XPath查找包含meter_id的行中的checkbox
                                xpath = f"//tr[contains(., '{meter_id}')]//input[@type='checkbox']"
                                elements = self.driver.find_elements(By.XPATH, xpath)
                                if elements:
                                    meter_element = elements[0]
                                    break
                            else:
                                meter_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                break
                        except NoSuchElementException:
                            continue
                    
                    if meter_element and not meter_element.is_selected():
                        self.driver.execute_script("arguments[0].click();", meter_element)
                        selected_count += 1
                        print(f"✅ 已选择水表: {meter_id}")
                        time.sleep(0.5)
                    elif meter_element:
                        print(f"⚠️  水表 {meter_id} 已经被选中")
                        selected_count += 1
                    else:
                        print(f"❌ 未找到水表: {meter_id}")
                        
                except Exception as e:
                    print(f"选择水表 {meter_id} 时出错: {e}")
            
            print(f"总共选择了 {selected_count} 个水表")
            return selected_count > 0
            
        except Exception as e:
            print(f"选择水表过程中发生错误: {e}")
            return False
    
    def set_report_parameters(self):
        """设置报表参数"""
        print("正在设置报表参数...")
        
        try:
            # 设置报表类型为日报表
            print("设置报表类型为日报表...")
            report_type_selectors = [
                'select[name*="reportType"]',
                'select[name*="ReportType"]', 
                'select:contains("日报表")',
                '#ddlReportType',
                'select option[value*="day"]'
            ]
            
            for selector in report_type_selectors:
                try:
                    if ":contains" in selector:
                        # 查找包含日报表的下拉框
                        selects = self.driver.find_elements(By.TAG_NAME, "select")
                        for select in selects:
                            options = select.find_elements(By.TAG_NAME, "option")
                            for option in options:
                                if "日报表" in option.text:
                                    option.click()
                                    print("✅ 已设置报表类型为日报表")
                                    break
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element.tag_name == "select":
                            options = element.find_elements(By.TAG_NAME, "option")
                            for option in options:
                                if "日报表" in option.text or "day" in option.get_attribute("value"):
                                    option.click()
                                    print("✅ 已设置报表类型为日报表")
                                    break
                        break
                except NoSuchElementException:
                    continue
            
            # 设置时间范围
            print("设置时间范围: 2025-07-24 到 2025-07-31...")
            
            # 开始时间
            start_date_selectors = [
                'input[name*="startDate"]',
                'input[name*="StartDate"]',
                'input[type="date"]',
                '#txtStartDate',
                'input[placeholder*="开始"]'
            ]
            
            for selector in start_date_selectors:
                try:
                    start_date_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    start_date_input.clear()
                    start_date_input.send_keys("2025-07-24")
                    print("✅ 已设置开始时间: 2025-07-24")
                    break
                except NoSuchElementException:
                    continue
            
            # 结束时间
            end_date_selectors = [
                'input[name*="endDate"]',
                'input[name*="EndDate"]',
                '#txtEndDate',
                'input[placeholder*="结束"]'
            ]
            
            for selector in end_date_selectors:
                try:
                    end_date_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    end_date_input.clear()
                    end_date_input.send_keys("2025-07-31")
                    print("✅ 已设置结束时间: 2025-07-31")
                    break
                except NoSuchElementException:
                    continue
            
            # 点击查询按钮
            print("正在点击查询按钮...")
            query_selectors = [
                'input[value*="查询"]',
                'button:contains("查询")',
                'input[type="submit"]',
                '#btnQuery',
                '*[onclick*="query"]'
            ]
            
            for selector in query_selectors:
                try:
                    if ":contains" in selector:
                        elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '查询')]")
                        if elements:
                            elements[0].click()
                            print("✅ 已点击查询按钮")
                            break
                    else:
                        query_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        query_button.click()
                        print("✅ 已点击查询按钮")
                        break
                except NoSuchElementException:
                    continue
            
            # 等待数据加载
            print("等待数据加载...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"设置报表参数时发生错误: {e}")
            return False
    
    def extract_data(self):
        """提取数据表格"""
        print("正在提取数据...")
        
        try:
            # 查找数据表格
            table_selectors = [
                'table',
                '.data-table',
                '#dataTable',
                'table[border]'
            ]
            
            data_table = None
            for selector in table_selectors:
                try:
                    tables = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    # 找到最大的表格（通常是数据表格）
                    if tables:
                        data_table = max(tables, key=lambda t: len(t.find_elements(By.TAG_NAME, "tr")))
                        print(f"找到数据表格，包含 {len(data_table.find_elements(By.TAG_NAME, 'tr'))} 行")
                        break
                except NoSuchElementException:
                    continue
            
            if not data_table:
                print("❌ 未找到数据表格")
                return False
            
            # 提取表格数据
            print("正在提取表格数据...")
            rows = data_table.find_elements(By.TAG_NAME, "tr")
            
            print("\n" + "="*80)
            print("📊 水表数据获取结果：")
            print("="*80)
            
            for i, row in enumerate(rows):
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:  # 可能是表头，尝试th
                    cells = row.find_elements(By.TAG_NAME, "th")
                
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    if any(row_data):  # 只打印非空行
                        if i == 0:
                            print("表头:", " | ".join(row_data))
                            print("-" * 80)
                        else:
                            print(f"第{i}行:", " | ".join(row_data))
            
            print("="*80)
            print(f"✅ 数据提取完成，共 {len(rows)} 行数据")
            
            return True
            
        except Exception as e:
            print(f"数据提取过程中发生错误: {e}")
            return False
    
    def get_water_data(self):
        """完整的数据获取流程"""
        print("\n" + "="*60)
        print("🚀 开始完整的水务数据获取流程")
        print("="*60)
        
        try:
            # 1. 登录
            if not self.login():
                print("❌ 登录失败，终止流程")
                return False
            
            # 2. 导航到报表页面
            if not self.navigate_to_reports():
                print("❌ 导航到报表页面失败，终止流程")
                return False
            
            # 3. 选择水表
            if not self.select_water_meters():
                print("❌ 选择水表失败，终止流程")
                return False
            
            # 4. 设置报表参数
            if not self.set_report_parameters():
                print("❌ 设置报表参数失败，终止流程")  
                return False
            
            # 5. 提取数据
            if not self.extract_data():
                print("❌ 数据提取失败，终止流程")
                return False
            
            print("\n🎉 水务数据获取流程全部完成！")
            return True
            
        except Exception as e:
            print(f"❌ 数据获取流程中发生错误: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            print("正在关闭浏览器...")
            try:
                self.driver.quit()
                print("浏览器已关闭")
            except:
                print("浏览器关闭时出现警告，但不影响功能")


def main():
    """主函数 - 执行完整的数据获取流程"""
    scraper = WaterDataScraper()
    
    try:
        # 设置浏览器驱动
        if not scraper.setup_driver():
            return
        
        # 执行完整的数据获取流程
        if scraper.get_water_data():
            print("\n🎉 所有功能测试成功！")
            print("数据获取完成，页面将保持打开10秒以便查看...")
            time.sleep(10)
        else:
            print("\n❌ 数据获取流程失败！")
            
    except KeyboardInterrupt:
        print("用户中断程序")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        # 关闭浏览器
        scraper.close()


if __name__ == "__main__":
    main()