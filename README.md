# 水务数据获取系统 - 完整版

一个用于从广州增城自来水公司 ThinkWater 智慧水网系统获取水表数据的 Python 工具。

## 🚀 功能特性

### 🏆 完整版本 (推荐)
- ✅ **完整8个水表数据获取** - 获取所有目标水表的完整数据
- ✅ **动态日期计算** - 自动获取最近7天数据（昨天往前推7天）
- ✅ **真实数据获取** - 修复了所有登录和会话问题，获取真实水务数据
- ✅ **JavaScript重定向处理** - 正确处理系统的JavaScript跳转逻辑
- ✅ **MD5密码加密** - 完全模拟浏览器的登录流程
- ✅ **数据完整性验证** - 自动检查获取的水表数量和ID匹配性
- ✅ **详细数据摘要** - 显示每个水表的统计信息和最新数据

### 传统版本
- 🔧 **Selenium版本** - 完整的浏览器自动化
- 🔧 **HTTP版本** - 纯请求方式，无浏览器依赖
- 🔧 **增强版本** - 命令行支持、环境变量、重试机制

## 📋 系统要求

- Python 3.7+
- 网络连接
- （可选）Chrome 浏览器（仅 Selenium 版本需要）

## 🛠️ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd getwaterdata
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量（推荐）
```bash
# 复制配置文件模板
cp config.env.example config.env

# 编辑配置文件，填入真实信息
# WATER_USERNAME=your_username
# WATER_PASSWORD=your_password
```

### 4. 运行程序

#### 方式一：完整版本（推荐）
```bash
# 获取完整8个水表的最近7天数据
python complete_8_meters_getter.py
```

#### 方式二：Selenium版本
```bash
# 使用浏览器自动化
python run.py
```

#### 方式三：增强版本
```bash
# 交互式菜单
python run_enhanced.py

# 命令行运行
python water_data_enhanced.py -m "2501200108,2520005" -s 2024-07-24 -e 2024-07-31 --json output.json
```

## 📖 使用说明

### 命令行参数

```bash
python water_data_enhanced.py --help
```

主要参数：
- `-u, --username` - 登录用户名
- `-p, --password` - 登录密码  
- `-m, --meters` - 水表ID列表（逗号分隔）
- `-s, --start-date` - 开始日期 (YYYY-MM-DD)
- `-e, --end-date` - 结束日期 (YYYY-MM-DD)
- `--json` - JSON输出文件路径
- `--csv` - CSV输出文件路径
- `--log-level` - 日志级别 (DEBUG/INFO/WARNING/ERROR)

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `WATER_USERNAME` | 登录用户名 | 13509288500 |
| `WATER_PASSWORD` | 登录密码 | 288500 |
| `WATER_BASE_URL` | 系统基础URL | http://axwater.dmas.cn |
| `LOG_LEVEL` | 日志级别 | INFO |

### 完整8个水表列表

系统获取以下8个水表的完整数据：
1. `1261181000263` - 荔新大道DN1200流量计
2. `1261181000300` - 新城大道医院DN800流量计
3. `1262330402331` - 宁西总表DN1200
4. `2190066` - 三江新总表DN800
5. `2190493` - 沙庄总表
6. `2501200108` - 2501200108
7. `2520005` - 如丰大道600监控表
8. `2520006` - 三棵树600监控表

## 📁 项目结构

```
getwaterdata/
├── complete_8_meters_getter.py # 🏆 完整版主脚本（推荐）
├── water_data_enhanced.py      # 增强版脚本
├── water_data_scraper.py      # Selenium版本
├── run_enhanced.py            # 增强版启动器
├── run.py                     # Selenium启动脚本
├── config.py                  # 配置文件
├── config.env.example         # 环境变量模板
├── requirements.txt           # 依赖包列表
├── data_viewer.py             # 数据查看工具
│
├── README.md                  # 项目说明
├── setup_guide.md             # 详细配置指南
├── 水务数据获取需求.md         # 需求文档
├── 项目总结.md                # 项目总结
│
├── *.json                     # 真实数据文件
├── *.html                     # 页面备份文件
└── __pycache__/               # Python缓存目录
```

## 📊 输出格式

### JSON格式
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "source": "enhanced_water_data_scraper", 
  "success": true,
  "data_type": "json",
  "data": {
    "rows": [
      {
        "meter_id": "2501200108",
        "date": "2024-07-24",
        "min_value": "134778.000",
        "avg_value": "137656.000"
      }
    ]
  },
  "date_range": {
    "start": "2024-07-24",
    "end": "2024-07-31"
  }
}
```

### CSV格式
```csv
meter_id,date,min_value,avg_value
2501200108,2024-07-24,134778.000,137656.000
```

## 🔧 故障排除

### 常见问题

1. **登录失败**
   - 检查用户名密码是否正确
   - 确认网络连接正常
   - 查看 `water_data.log` 日志文件

2. **无数据返回**
   - 尝试不同的日期范围
   - 检查水表ID格式
   - 使用交互式菜单测试

3. **依赖安装失败**
   ```bash
   # 使用国内镜像源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

4. **Chrome相关问题**（仅Selenium版本）
   - 建议使用增强版本（无需Chrome）
   - 或确保Chrome浏览器已安装

### 日志文件

程序运行时会生成 `water_data.log` 文件，包含详细的执行日志，有助于问题诊断。

## 🔒 安全说明

- 建议使用环境变量存储登录凭证
- 不要将包含密码的配置文件提交到版本控制系统
- 定期更新依赖包以获得安全补丁

## 📈 版本历史

- **v3.0** (完整版) - 修复所有登录问题，获取完整8个水表数据，动态日期计算
- **v2.0** (增强版) - 命令行支持、环境变量、重试机制、多格式输出  
- **v1.0** (传统版) - 基础功能实现，多种技术方案

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 查看项目文档
