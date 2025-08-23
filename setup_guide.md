# 环境配置指南

## 1. 安装Python依赖

首先确保您已经安装了Python 3.7或更高版本，然后运行以下命令安装所需的Python包：

```bash
pip install -r requirements.txt
```

## 2. 配置环境变量（推荐）

为了安全起见，建议使用环境变量配置登录信息：

### 方法一：使用配置文件
1. 复制 `config.env.example` 为 `config.env`
2. 编辑 `config.env` 文件，填入真实的配置信息

### 方法二：设置系统环境变量
```bash
# Windows (命令提示符)
set WATER_USERNAME=your_username
set WATER_PASSWORD=your_password

# Windows (PowerShell)
$env:WATER_USERNAME="your_username"
$env:WATER_PASSWORD="your_password"

# Linux/macOS
export WATER_USERNAME=your_username
export WATER_PASSWORD=your_password
```

## 3. 运行程序

### 增强版本（推荐）
```bash
# 交互式菜单
python run_enhanced.py

# 快速运行
python run_enhanced.py --quick

# 命令行运行
python water_data_enhanced.py

# 指定参数运行
python water_data_enhanced.py -m "2501200108,2520005" -s 2024-07-24 -e 2024-07-31 --json output.json --csv output.csv
```

### 传统版本
```bash
# Selenium版本（需要Chrome浏览器）
python water_data_scraper.py

# HTTP请求版本
python water_data_http.py

# 最终版本
python water_data_final.py
```

## 4. 安装Chrome浏览器和ChromeDriver（仅Selenium版本需要）

### 方法一：自动安装ChromeDriver（推荐）
代码已经配置为使用webdriver-manager自动管理ChromeDriver，无需手动安装。

### 方法二：手动安装ChromeDriver
1. 下载ChromeDriver：https://chromedriver.chromium.org/
2. 将ChromeDriver.exe放到Python安装目录或添加到系统PATH环境变量中

## 5. 使用说明

### 增强版功能特性
- ✅ 命令行参数支持
- ✅ 环境变量配置
- ✅ 自动重试机制
- ✅ 多日期范围尝试
- ✅ JSON/CSV数据保存
- ✅ 详细日志记录
- ✅ 交互式菜单

### 命令行参数说明
```bash
python water_data_enhanced.py --help
```

### 输出文件
- JSON格式：包含完整的响应数据和元信息
- CSV格式：表格数据，支持Excel直接打开
- 日志文件：`water_data.log`

## 6. 常见问题解决

### 问题1：找不到ChromeDriver（仅Selenium版本）
- 确保Chrome浏览器已安装
- 确保ChromeDriver版本与Chrome浏览器版本匹配
- 建议使用增强版本（不需要Chrome）

### 问题2：网络连接问题
- 检查网络连接
- 确认目标网站可以正常访问
- 查看日志文件获取详细错误信息

### 问题3：登录失败
- 检查用户名密码是否正确
- 确认环境变量配置正确
- 查看 `water_data.log` 获取详细错误信息

### 问题4：无数据返回
- 尝试不同的日期范围
- 检查水表ID格式是否正确
- 使用交互式菜单的测试功能

### 问题5：依赖包安装失败
```bash
# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或者使用启动器自动安装
python run_enhanced.py --install-deps
```