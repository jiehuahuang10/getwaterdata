# 🌊 水务数据自动化系统

## 📋 项目概述

这是一个基于Python和GitHub Actions的自动化水务数据获取和Excel更新系统。系统能够自动从水务系统获取8个水表的每日用水量数据，并更新到指定的Excel文件中。

## ✨ 核心功能

### 🔄 自动化数据获取
- **定时执行**：每天下午6点自动运行
- **数据源**：水务系统API接口
- **覆盖范围**：8个水表的数据
- **数据格式**：JSON格式，自动转换为Excel

### 📊 Excel文件管理
- **目标文件**：`石滩供水服务部每日总供水情况.xlsx`
- **更新方式**：自动写入指定列
- **数据映射**：
  - 荔新大道DN1200流量计 → 荔新大道
  - 新城大道医院DN800流量计 → 新城大道
  - 三江新总表DN800（2190066） → 三江新总表
  - 宁西总表DN1200 → 宁西2总表
  - 沙庄总表 → 沙庄总表
  - 如丰大道600监控表 → 如丰大道600监控表
  - 三棵树600监控表 → 三棵树600监控表
  - 2501200108 → 中山西路DN300流量计

### 🌐 Web界面
- **Flask应用**：提供Web操作界面
- **实时数据**：显示最新获取的数据
- **手动触发**：支持手动执行数据获取
- **Excel导出**：支持手动导出Excel文件

## 🚀 技术架构

### 后端技术栈
- **Python 3.9+**：主要开发语言
- **Flask**：Web框架
- **requests**：HTTP请求库
- **BeautifulSoup4**：HTML解析
- **openpyxl**：Excel文件操作
- **pandas**：数据处理

### 自动化部署
- **GitHub Actions**：CI/CD自动化
- **定时任务**：cron表达式调度
- **环境变量**：GitHub Secrets安全存储
- **自动提交**：文件变更自动提交到仓库

## 📁 项目结构

```
getwaterdata/
├── .github/workflows/          # GitHub Actions配置
│   └── daily-water-data.yml   # 自动化工作流
├── excel_exports/             # Excel文件目录
│   └── 石滩供水服务部每日总供水情况.xlsx
├── templates/                 # Web模板
│   └── index.html            # 主页面
├── github_automation.py      # GitHub Actions执行脚本
├── integrated_excel_updater.py # Excel更新核心模块
├── specific_excel_writer.py   # Excel文件操作模块
├── force_real_data_web.py    # 数据获取核心模块
├── web_app_fixed.py          # Flask Web应用
├── requirements.txt          # Python依赖
└── README.md                 # 项目文档
```

## 🔧 安装和配置

### 1. 环境要求
- Python 3.9+
- Git
- GitHub账户

### 2. 本地安装
```bash
# 克隆项目
git clone https://github.com/jiehuahuang10/getwaterdata.git
cd getwaterdata

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config.env.example config.env
# 编辑config.env文件，填入您的登录信息
```

### 3. GitHub Actions配置

#### 创建GitHub仓库
1. 在GitHub上创建新仓库
2. 选择Public仓库（免费）
3. 上传项目代码

#### 配置Secrets
在仓库Settings → Secrets and variables → Actions中添加：
```
LOGIN_URL=您的水务系统登录URL
USERNAME=您的用户名
PASSWORD=您的密码
REPORT_URL=您的报表URL
```

#### 启用Actions
1. 进入仓库Actions页面
2. 点击"Enable workflows"
3. 工作流将自动启用

## 🎯 使用方法

### 本地运行
```bash
# 启动Web界面
python web_app_fixed.py

# 访问 http://localhost:5000
```

### 自动化运行
- **定时执行**：每天下午6点自动运行
- **手动触发**：在GitHub Actions页面点击"Run workflow"
- **监控日志**：在Actions页面查看执行状态

### Web界面操作
1. **获取数据**：点击"获取数据"按钮
2. **查看结果**：在页面查看获取的数据
3. **更新Excel**：选择日期，点击"更新指定Excel"
4. **下载文件**：点击"导出Excel"下载文件

## 📊 数据流程

### 自动化流程
1. **定时触发** → GitHub Actions启动
2. **环境准备** → 安装依赖，配置环境
3. **数据获取** → 登录系统，获取水表数据
4. **Excel更新** → 写入指定Excel文件
5. **自动提交** → 提交更新到GitHub仓库

### 数据映射
```
API数据 → Excel列映射
├── 荔新大道DN1200流量计 → 第7列 荔新大道
├── 新城大道医院DN800流量计 → 第8列 新城大道
├── 三江新总表DN800（2190066） → 第9列 三江新总表
├── 宁西总表DN1200 → 第12列 宁西2总表
├── 沙庄总表 → 第13列 沙庄总表
├── 如丰大道600监控表 → 第14列 如丰大道600监控表
├── 三棵树600监控表 → 第15列 三棵树600监控表
└── 2501200108 → 第16列 中山西路DN300流量计
```

## 🔍 监控和调试

### GitHub Actions监控
- **执行状态**：查看Actions页面的执行历史
- **详细日志**：点击具体运行记录查看日志
- **错误排查**：根据错误信息定位问题

### 本地调试
```bash
# 测试数据获取
python github_automation.py

# 测试Excel更新
python integrated_excel_updater.py

# 查看日志
tail -f github_automation.log
```

## 🛠️ 故障排除

### 常见问题

#### 1. 环境变量错误
**症状**：`缺少必要的环境变量`
**解决**：检查GitHub Secrets配置是否正确

#### 2. 权限错误
**症状**：`Permission denied (403)`
**解决**：配置仓库Actions权限为"Read and write"

#### 3. 网络连接问题
**症状**：`Connection timeout`
**解决**：检查网络连接和API地址

#### 4. Excel文件锁定
**症状**：`PermissionError`
**解决**：关闭Excel文件，重新运行

### 调试步骤
1. 查看GitHub Actions执行日志
2. 检查环境变量配置
3. 验证网络连接
4. 测试本地运行

## 📈 系统优势

### 🆓 完全免费
- GitHub Actions免费额度
- Public仓库无限制执行
- 无需额外服务器成本

### 🔒 安全可靠
- 敏感信息加密存储
- GitHub Secrets安全机制
- 代码版本控制

### 🤖 全自动化
- 无需人工干预
- 定时自动执行
- 错误自动重试

### 📊 数据完整
- 8个水表全覆盖
- 历史数据保存
- 实时数据更新

## 🔮 未来扩展

### 功能增强
- [ ] 邮件通知功能
- [ ] 数据可视化图表
- [ ] 异常数据告警
- [ ] 多系统数据整合

### 技术优化
- [ ] 数据库存储
- [ ] API接口优化
- [ ] 缓存机制
- [ ] 性能监控

## 📞 技术支持

### 联系方式
- **项目地址**：https://github.com/jiehuahuang10/getwaterdata
- **问题反馈**：通过GitHub Issues提交

### 文档资源
- [GitHub Actions部署指南](GITHUB_DEPLOYMENT.md)
- [Excel功能说明](Excel导出功能说明.md)
- [项目动态总系统](项目动态总系统.md)

---

## 🎉 项目状态

**✅ 部署完成** - 自动化系统已成功部署到GitHub Actions
**✅ 功能测试** - 所有核心功能已通过测试
**✅ 生产就绪** - 系统已准备好投入生产使用

**最后更新**：2025年8月24日
**版本**：v1.0.0
**状态**：生产环境运行中
