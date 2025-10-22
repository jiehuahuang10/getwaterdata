# Web版月度统计表部署指南

## 📋 部署方案说明

本指南将帮助您将Web版月度统计表功能部署到GitHub，同时**完全不影响**现有的KDocs Cookie自动化维护功能。

---

## 🎯 部署策略

### 选项1：本地运行（推荐）⭐

**适用场景**：办公室内网使用，数据安全性高

**优点**：
- ✅ 完全不涉及GitHub
- ✅ 现有自动化不受任何影响
- ✅ 数据保存在本地，更安全
- ✅ 无需配置云服务

**部署步骤**：

1. **启动服务器**
   ```bash
   python add_summary_web.py
   ```

2. **访问Web界面**
   - 本机访问：http://localhost:5001
   - 局域网访问：http://你的IP:5001（如：http://192.168.2.83:5001）

3. **开机自启动（可选）**
   - Windows：创建快捷方式到启动文件夹
   - 或使用Windows任务计划程序

---

### 选项2：GitHub Pages部署（仅前端）

**适用场景**：需要远程访问，但Excel文件还是在本地

**说明**：
- GitHub Pages只能托管静态网页
- **无法运行Python后端**
- 可以部署一个纯前端版本，但功能受限

**限制**：
- ❌ 无法直接修改本地Excel文件
- ❌ 无法读取数据源文件
- ⚠️ 需要通过API或其他方式桥接

**不推荐**：因为核心功能（Excel操作）需要Python后端

---

### 选项3：云服务器部署（完整功能）

**适用场景**：需要远程访问，团队协作

**支持的云平台**：
- ✅ 阿里云ECS
- ✅ 腾讯云CVM
- ✅ 华为云ECS
- ✅ AWS EC2
- ✅ Azure VM

**部署步骤概要**：

1. **购买云服务器**（最低配置即可）
   - CPU：1核
   - 内存：1GB
   - 系统：Ubuntu 20.04 或 Windows Server

2. **上传文件**
   ```bash
   # 上传项目文件到服务器
   scp -r getwaterdata/ user@server:/path/to/
   ```

3. **安装依赖**
   ```bash
   pip install flask openpyxl
   ```

4. **使用生产级服务器**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 add_summary_web:app
   ```

5. **配置防火墙**
   - 开放5001端口
   - 配置安全组规则

6. **设置开机自启**
   - 使用systemd服务（Linux）
   - 或Windows服务

---

### 选项4：Docker容器部署

**适用场景**：标准化部署，易于迁移

**需要创建**：
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`

**优点**：
- ✅ 环境一致性
- ✅ 易于迁移
- ✅ 易于扩展

---

## 🔒 GitHub与本地协作方案（推荐）

### 架构设计

```
GitHub (代码仓库)
    ↓
   拉取代码
    ↓
本地服务器 (运行Web服务)
    ↓
   读写Excel文件
    ↓
本地磁盘 (数据存储)
```

### 工作流程

1. **代码管理**：GitHub存储代码（已有）
2. **自动化维护**：GitHub Actions定期检查Cookie（已有）✅
3. **Web服务**：本地运行Flask服务器（新增）✅
4. **数据操作**：直接操作本地Excel文件（新增）✅

### 互不影响的原因

| 功能 | 运行位置 | 操作内容 | 冲突可能性 |
|------|---------|---------|-----------|
| KDocs Cookie维护 | GitHub Actions | 检查Cookie有效期，创建提醒Issue | ✅ 无冲突 |
| Web月度统计表 | 本地电脑 | 修改本地Excel文件 | ✅ 无冲突 |

**完全独立**：
- GitHub Actions不会访问本地Excel文件
- 本地Web服务不会影响GitHub Actions的运行
- 两者使用不同的工作流程

---

## 📦 推荐部署方案：本地 + GitHub代码管理

### 步骤1：提交Web版代码到GitHub

**要提交的文件**：
```
add_summary_web.py          # Flask服务器
templates/add_summary.html  # Web界面
extract_water_data.py       # 数据提取（已有）
DEPLOYMENT_GUIDE.md         # 本文档
```

**不需要提交的文件**：
```
excel_exports/*.xlsx        # Excel文件（数据隐私）
__pycache__/               # Python缓存
*.pyc                      # 编译文件
```

### 步骤2：更新.gitignore

确保Excel数据文件不被上传：
```gitignore
# Excel数据文件
excel_exports/*.xlsx

# Python缓存
__pycache__/
*.pyc
*.pyo

# 虚拟环境
venv/
env/

# IDE配置
.vscode/
.idea/
```

### 步骤3：本地运行服务

```bash
# 1. 克隆仓库（如果在新电脑上）
git clone https://github.com/你的用户名/getwaterdata.git

# 2. 进入目录
cd getwaterdata

# 3. 安装依赖
pip install flask openpyxl

# 4. 启动服务
python add_summary_web.py

# 5. 浏览器访问
# http://localhost:5001
```

---

## 🚀 快速开始：提交代码到GitHub

### 方法1：使用命令行

```bash
# 1. 确保在项目目录
cd D:/pj/getwaterdata

# 2. 查看当前状态
git status

# 3. 添加新文件
git add add_summary_web.py
git add templates/add_summary.html
git add DEPLOYMENT_GUIDE.md

# 4. 提交
git commit -m "Add web-based monthly summary feature"

# 5. 推送到GitHub
git push origin main
```

### 方法2：使用GitHub Desktop

1. 打开GitHub Desktop
2. 选择getwaterdata仓库
3. 勾选要提交的文件：
   - add_summary_web.py
   - templates/add_summary.html
   - DEPLOYMENT_GUIDE.md
4. 填写提交信息："Add web-based monthly summary feature"
5. 点击"Commit to main"
6. 点击"Push origin"

---

## ✅ 验证部署成功

### 1. 验证GitHub Actions（现有自动化）

- 访问：https://github.com/你的用户名/getwaterdata/actions
- 确认"KDocs Cookie维护"工作流正常运行
- 应该看到定期执行的记录

### 2. 验证本地Web服务

- 启动：`python add_summary_web.py`
- 访问：http://localhost:5001
- 测试：输入售水量，点击添加
- 确认：Excel文件成功更新

### 3. 验证互不影响

- GitHub Actions继续每周一检查Cookie ✅
- 本地Web服务随时可用 ✅
- Excel文件只在本地存储 ✅

---

## 📝 维护说明

### 日常使用

1. **添加月度数据**：
   - 打开浏览器
   - 访问 http://localhost:5001
   - 输入售水量
   - 点击"添加新月份统计表"

2. **Cookie维护**（自动）：
   - GitHub Actions每周一自动检查
   - Cookie即将过期时会创建Issue提醒
   - 按Issue说明更新即可

### 代码更新

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重启服务
# 停止当前运行的服务（Ctrl+C）
python add_summary_web.py
```

---

## ❓ 常见问题

### Q1: 我需要在GitHub上运行Web服务吗？

**A**: 不需要。推荐在本地运行，GitHub只用于代码存储和Cookie维护自动化。

### Q2: 会影响现有的GitHub Actions吗？

**A**: 完全不会。两者独立运行：
- GitHub Actions：云端，定时检查Cookie
- Web服务：本地，手动添加数据

### Q3: Excel文件会上传到GitHub吗？

**A**: 不会。`.gitignore`已配置排除Excel文件。

### Q4: 如何让团队其他成员使用？

**A**: 
- **方案1（推荐）**：在办公室一台电脑上运行服务，其他人通过局域网访问
- **方案2**：每个人本地运行服务，Excel文件通过共享文件夹同步

### Q5: 服务器关机后怎么办？

**A**: 重启电脑后，重新运行 `python add_summary_web.py` 即可。
或配置开机自启动。

---

## 🎯 推荐配置：最佳实践

### 配置1：办公室单机部署

```
一台办公电脑
  ↓
运行Web服务 (localhost:5001)
  ↓
本地Excel文件
  ↓
其他同事通过IP访问 (http://192.168.x.x:5001)
```

**优点**：
- ✅ 简单
- ✅ 数据集中
- ✅ 易于管理

**适合**：小团队（5人以内）

### 配置2：个人使用

```
你的电脑
  ↓
运行Web服务 (localhost:5001)
  ↓
本地Excel文件
```

**优点**：
- ✅ 最简单
- ✅ 数据私密
- ✅ 无网络依赖

**适合**：个人使用

---

## 📞 获取帮助

如有问题，可以：
1. 查看项目README.md
2. 检查GitHub Issues
3. 查看运行日志

---

**总结**：推荐使用"本地运行 + GitHub代码管理"方案，既保证了功能完整性，又不影响现有自动化。✨

