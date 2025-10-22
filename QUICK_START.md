# 快速开始：提交Web版到GitHub

## 📦 一键提交指南

### 方法1：命令行提交（推荐）

```bash
# 1. 查看当前状态
git status

# 2. 添加所有相关文件
git add add_summary_web.py
git add templates/add_summary.html
git add extract_water_data.py
git add requirements.txt
git add DEPLOYMENT_GUIDE.md
git add QUICK_START.md
git add .gitignore

# 3. 提交
git commit -m "✨ 新增Web版月度统计表功能

- 添加Flask Web界面用于手动添加月度统计表
- 支持输入售水量，自动计算供水量、损耗水量和损耗率
- 数据源自动提取（从石滩供水服务部每日总供水情况.xlsx）
- 完全不影响现有的KDocs Cookie自动化维护功能
- 包含详细的部署指南和快速开始文档"

# 4. 推送到GitHub
git push origin main
```

### 方法2：分步提交

```bash
# 第1步：提交核心Web服务
git add add_summary_web.py templates/add_summary.html
git commit -m "Add web-based monthly summary service"

# 第2步：提交依赖配置
git add requirements.txt
git commit -m "Add Python dependencies"

# 第3步：提交文档
git add DEPLOYMENT_GUIDE.md QUICK_START.md
git commit -m "Add deployment guides"

# 第4步：更新gitignore
git add .gitignore
git commit -m "Update gitignore to exclude Excel data files"

# 第5步：推送所有提交
git push origin main
```

---

## ✅ 提交前检查清单

- [x] **add_summary_web.py** - Web服务器主程序
- [x] **templates/add_summary.html** - Web前端界面
- [x] **extract_water_data.py** - 数据提取模块（已存在）
- [x] **requirements.txt** - Python依赖包列表
- [x] **DEPLOYMENT_GUIDE.md** - 详细部署指南
- [x] **QUICK_START.md** - 快速开始指南
- [x] **.gitignore** - 排除Excel数据文件

**不要提交**：
- ❌ excel_exports/*.xlsx（业务数据）
- ❌ kdocs_cookies.json（敏感信息）
- ❌ test_*.py（测试文件）

---

## 🎯 提交后验证

### 1. 在GitHub查看提交

访问：`https://github.com/你的用户名/getwaterdata/commits/main`

应该看到：
- ✅ 最新提交记录
- ✅ 新增的文件
- ✅ 提交说明清晰

### 2. 验证.gitignore生效

```bash
git status
```

应该**看不到**：
- ❌ excel_exports/石滩区分区计量.xlsx
- ❌ excel_exports/石滩供水服务部每日总供水情况.xlsx
- ❌ kdocs_cookies.json

### 3. 验证GitHub Actions未受影响

访问：`https://github.com/你的用户名/getwaterdata/actions`

确认：
- ✅ "KDocs Cookie维护"工作流正常显示
- ✅ 没有新的错误或失败

---

## 🚀 本地运行Web服务

提交到GitHub后，在本地运行：

```bash
# 1. 确保依赖已安装
pip install -r requirements.txt

# 2. 启动Web服务
python add_summary_web.py

# 3. 打开浏览器访问
# http://localhost:5001
```

---

## 🔄 在其他电脑上使用

### 新电脑部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/getwaterdata.git

# 2. 进入目录
cd getwaterdata

# 3. 创建虚拟环境（推荐）
python -m venv venv

# Windows激活
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建Excel文件夹（如果不存在）
mkdir excel_exports

# 6. 复制Excel数据文件到excel_exports文件夹
# - 石滩区分区计量.xlsx
# - 石滩供水服务部每日总供水情况.xlsx

# 7. 启动服务
python add_summary_web.py
```

---

## 📂 完整文件结构

提交后的GitHub仓库结构：

```
getwaterdata/
├── .github/
│   └── workflows/
│       └── kdocs-maintenance.yml      ✅ 现有自动化（不变）
├── templates/
│   ├── index.html                     ✅ 原有页面
│   └── add_summary.html               🆕 新增Web界面
├── add_summary_web.py                 🆕 Web服务器
├── extract_water_data.py              ✅ 数据提取
├── requirements.txt                   🆕 依赖列表
├── DEPLOYMENT_GUIDE.md                🆕 部署指南
├── QUICK_START.md                     🆕 快速开始
├── .gitignore                         ✅ 更新
├── README.md                          ✅ 原有说明
└── excel_exports/                     ❌ 不提交（本地数据）
    ├── 石滩区分区计量.xlsx
    └── 石滩供水服务部每日总供水情况.xlsx
```

---

## 🔐 安全说明

### 已排除的敏感文件

`.gitignore` 已配置排除：

```gitignore
# Excel数据文件（包含敏感业务数据）
excel_exports/*.xlsx

# Cookie文件（敏感信息）
kdocs_cookies.json
kdocs_cookie_meta.json

# 测试文件
test_*.py
debug_*.py
```

### GitHub Secrets（现有配置保持不变）

- ✅ `KDOCS_COOKIE_JSON` - Cookie数据
- ✅ `KDOCS_COOKIE_META` - Cookie元数据

**Web版不需要新的Secrets**

---

## ❓ 常见问题

### Q: 会影响现有的GitHub Actions吗？

**A**: 完全不会。Web版在本地运行，GitHub Actions在云端运行，两者独立。

### Q: 需要部署到GitHub Pages吗？

**A**: 不需要。推荐本地运行，因为需要访问本地Excel文件。

### Q: 团队成员如何访问？

**A**: 
```bash
# 启动服务时允许局域网访问（默认已配置）
python add_summary_web.py

# 其他成员通过IP访问
# http://你的IP:5001
```

查看你的IP：
```bash
# Windows
ipconfig

# 查找 IPv4 地址，如：192.168.2.83
```

### Q: 如何更新代码？

**A**:
```bash
# 拉取最新代码
git pull origin main

# 重启服务
python add_summary_web.py
```

---

## 🎊 完成！

提交完成后：

1. ✅ GitHub上有了Web版代码
2. ✅ 现有自动化继续正常运行
3. ✅ 本地可以使用Web界面添加数据
4. ✅ 可以在任何电脑上克隆使用

**核心原则**：
- **代码在GitHub** - 版本管理，协作开发
- **服务在本地** - 数据安全，访问快速
- **互不影响** - 各司其职，稳定可靠

---

**祝使用愉快！** 🎉

