# 🚀 Render 部署完整指南

## 📋 系统概述

这是一个统一的水务数据管理系统，包含三个核心功能：
1. **月度统计表管理** - 自动添加月度供水统计表
2. **水务数据获取** - 获取最近7天水表数据
3. **自动更新Excel** - 自动获取并更新Excel数据

## 🔧 准备工作

### 1. GitHub 仓库
- ✅ 仓库地址：`https://github.com/jiehuahuang10/getwaterdata.git`
- ✅ 主分支：`main`
- ✅ 所有代码已推送

### 2. 项目文件检查
- ✅ `app_unified.py` - 统一的 Flask 应用
- ✅ `Procfile` - 启动命令：`web: gunicorn -w 4 -b 0.0.0.0:$PORT app_unified:app`
- ✅ `requirements.txt` - Python 依赖
- ✅ `runtime.txt` - Python 版本：`python-3.11.9`
- ✅ `templates/` - 所有 HTML 模板
- ✅ `excel_exports/` - Excel 文件目录

## 📝 Render 部署步骤

### 步骤 1：登录 Render
1. 访问 [https://render.com](https://render.com)
2. 使用 GitHub 账号登录

### 步骤 2：创建新的 Web Service
1. 点击右上角 **"New +"** 按钮
2. 选择 **"Web Service"**

### 步骤 3：连接 GitHub 仓库
1. 选择 **"Build and deploy from a Git repository"**
2. 点击 **"Next"**
3. 选择你的 GitHub 仓库：`getwaterdata`
   - 如果看不到仓库，点击 **"Configure account"** 授权
4. 点击 **"Connect"**

### 步骤 4：配置 Web Service

填写以下信息：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Name** | `water-data-system` | 服务名称（自定义） |
| **Region** | `Singapore (Southeast Asia)` | 选择新加坡（离中国最近） |
| **Branch** | `main` | 部署分支 |
| **Root Directory** | 留空 | 项目根目录 |
| **Runtime** | `Python 3` | 自动检测 |
| **Build Command** | `pip install -r requirements.txt` | 自动填充 |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT app_unified:app` | 从 Procfile 读取 |

### 步骤 5：选择计划
- 选择 **"Free"** 计划（每月 750 小时免费）
- 点击 **"Create Web Service"**

### 步骤 6：等待部署
1. Render 会自动开始构建和部署
2. 查看日志输出，确认没有错误
3. 部署成功后，会显示绿色的 **"Live"** 状态

### 步骤 7：获取访问地址
- 部署成功后，Render 会分配一个 URL
- 格式：`https://water-data-system.onrender.com`
- 点击 URL 即可访问系统

## 🌐 访问系统

部署成功后，可以通过以下路径访问各个功能：

| 功能 | 路径 | 说明 |
|------|------|------|
| **主页** | `/` | 系统首页，三个功能入口 |
| **月度统计表** | `/summary` | 添加月度统计表 |
| **水务数据获取** | `/data` | 获取最近7天数据 |
| **自动更新Excel** | `/auto_update` | 自动更新Excel |

## ⚙️ 环境变量配置（可选）

如果需要配置环境变量：

1. 在 Render 控制台中，进入你的 Web Service
2. 点击左侧菜单的 **"Environment"**
3. 添加环境变量：

```bash
# 示例（根据实际需要添加）
FLASK_ENV=production
PORT=5000
```

## 📊 重要说明

### Excel 文件处理
- Excel 文件在云端部署时可能无法持久化
- 建议每次操作后下载保存到本地
- 或者使用云存储服务（如 AWS S3）

### Cookie 维护
- `kdocs_cookies.json` 文件不会被上传（在 `.gitignore` 中）
- 如需使用 cookie 功能，需要通过其他方式配置

### 性能优化
- Render Free 计划会在 15 分钟无活动后休眠
- 首次访问可能需要 30-60 秒启动
- 可升级到付费计划保持常驻

## 🔧 故障排查

### 部署失败
1. 检查 `requirements.txt` 中的依赖是否正确
2. 查看 Render 日志中的错误信息
3. 确认 Python 版本兼容性

### 应用启动失败
1. 检查 `Procfile` 中的命令是否正确
2. 确认 `app_unified.py` 中的 `app` 对象定义正确
3. 查看应用日志：`gunicorn` 启动日志

### 访问超时
1. Render Free 计划首次访问需要启动时间
2. 刷新页面重试
3. 检查 Render 服务状态

## 🔄 更新部署

当代码有更新时：

1. 本地提交并推送代码到 GitHub：
```bash
git add .
git commit -m "your update message"
git push
```

2. Render 会自动检测并重新部署
3. 或在 Render 控制台手动触发部署：**"Manual Deploy"** → **"Deploy latest commit"**

## 📞 技术支持

如遇到问题，可以：
1. 查看 Render 官方文档：[https://render.com/docs](https://render.com/docs)
2. 查看应用日志排查问题
3. 检查 GitHub Actions 日志

---

## ✅ 部署检查清单

在部署前，请确认：

- [ ] 代码已推送到 GitHub
- [ ] `Procfile` 配置正确
- [ ] `requirements.txt` 包含所有依赖
- [ ] `runtime.txt` 指定 Python 版本
- [ ] `.gitignore` 已配置敏感文件
- [ ] 所有模板文件在 `templates/` 目录
- [ ] Excel 文件在 `excel_exports/` 目录

## 🎉 部署完成

现在你的水务数据管理系统已经成功部署到云端，可以从任何地方访问使用了！

**访问地址：** `https://water-data-system.onrender.com`（实际地址以 Render 分配为准）

---

*文档更新时间：2025-10-25*

