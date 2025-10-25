# 石滩供水数据管理系统

## 📋 项目简介

这是一个自动化的水务数据管理系统，集成了**数据采集**、**Excel处理**、**月度统计**和**云端部署**功能。系统通过 GitHub Actions 和 Render 云服务实现全自动化运行，无需人工干预即可完成每日数据更新和月度报表生成。

### 🎯 核心功能

1. **每日水务数据自动更新** - 每天自动获取水表读数并更新 Excel
2. **月度统计表管理** - 自动生成月度分区计量统计报表
3. **水务数据实时查询** - 查看最近7天的水表数据
4. **手动数据更新** - 支持手动选择日期更新特定数据
5. **🆕 飞书云空间同步** - 自动同步 Excel 到飞书，支持多端查看

---

## 🏗️ 系统架构

```
石滩供水数据管理系统
├── 前端界面 (Web)
│   ├── 主页 - 三大功能入口
│   ├── 月度统计表管理
│   ├── 水务数据查询
│   └── 手动数据更新
│
├── 后端服务 (Flask)
│   ├── app_unified.py - 统一应用入口
│   ├── add_summary_web.py - 月度统计逻辑
│   ├── integrated_excel_updater.py - Excel更新核心
│   └── force_real_data_web.py - 数据获取模块
│
├── 自动化任务 (GitHub Actions)
│   ├── 每日数据更新 (18:00 & 18:30)
│   ├── 🆕 飞书云空间同步
│   ├── Cookie维护 (每4小时)
│   └── 健康检查 (每周一)
│
├── 云端部署 (Render)
│   ├── Web服务 (24/7在线)
│   ├── 自动同步到GitHub
│   └── 环境变量管理
│
└── 🆕 飞书集成
    ├── 自动上传Excel到飞书
    ├── 多端查看（手机/电脑）
    └── 团队协作共享
```

---

## 📊 数据文件说明

### 1. 石滩供水服务部每日总供水情况.xlsx
- **用途**: 存储每日8个水表的读数
- **更新方式**: 每天下午6点自动更新
- **数据源**: 从水务管理系统API获取
- **🆕 同步到**: GitHub + 飞书云空间
- **覆盖的水表**:
  - 荔新大道DN1200监控表
  - 新城大道医院DN800监控表
  - 宁西2总表DN1200
  - 如丰大道600监控表
  - 沙庄总表
  - 2501200108
  - 三棵树600监控表
  - 荣山墟路DN300监控表

### 2. 石滩区分区计量.xlsx
- **用途**: 月度分区计量统计表
- **更新方式**: 手动通过Web界面添加
- **数据内容**: 
  - 1区、2区、3区的供水量
  - 售水量（手动输入）
  - 损耗水量（自动计算）
  - 水损耗率（自动计算）
- **同步**: 修改后自动同步到GitHub

---

## 🚀 快速开始

### 本地运行

#### 1. 克隆项目
```bash
git clone https://github.com/jiehuahuang10/getwaterdata.git
cd getwaterdata
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
创建 `config.env` 文件：
```env
LOGIN_URL=你的登录URL
USERNAME=你的用户名
PASSWORD=你的密码
REPORT_URL=你的报表URL
```

#### 4. 启动服务
```bash
python app_unified.py
```

访问 http://localhost:5000

---

## 🌐 Web界面使用说明

### 主页 (/)
显示三个功能入口卡片：
- 💼 月度统计表管理
- 📊 水务数据查询
- 🔄 手动数据更新

### 1. 月度统计表管理 (/summary)

**功能**: 添加月度分区计量统计表

**使用步骤**:
1. 系统自动显示当前月份信息
2. 输入各区售水量：
   - 1区售水量
   - 2区售水量
   - 3区售水量
3. 点击"新增下月统计表"
4. 系统自动：
   - 从日供水数据提取月度汇总
   - 计算损耗水量 = 供水量 - 售水量
   - 计算水损耗率 = 损耗水量 / 供水量
   - 生成完整的月度报表
   - 同步到GitHub

**输出结果**:
- 更新 `石滩区分区计量.xlsx` 文件
- 添加新的月度统计表
- 自动同步到GitHub仓库

### 2. 水务数据查询 (/data)

**功能**: 查看最近7天的水表数据

**使用步骤**:
1. 页面自动加载最近的历史数据
2. 点击"获取最近7天数据"刷新
3. 查看8个水表的详细读数
4. 支持导出为Excel文件

**数据展示**:
- 日期范围
- 8个水表的实时读数
- 数据统计信息

### 3. 手动数据更新 (/auto_update)

**功能**: 手动选择日期更新水表数据

**使用步骤**:
1. 选择目标日期（或点击"快速选择昨天"）
2. 点击"执行更新"
3. 系统自动：
   - 从水务系统获取指定日期数据
   - 更新到Excel文件
   - 显示更新结果

**适用场景**:
- 补充历史数据
- 修正错误数据
- 手动触发更新

---

## ⚙️ GitHub Actions 自动化

### 1. 每日数据更新

**文件**: `.github/workflows/daily-water-data.yml`

**执行时间**:
- 每天 18:00（北京时间）- 主要执行
- 每天 18:30（北京时间）- 备份执行

**执行流程**:
```
1. 检出代码
2. 安装Python和依赖
3. 创建配置文件
4. 执行数据更新（最多重试3次）
5. 验证Excel文件
6. 提交并推送到GitHub
7. 更新执行状态
```

**可靠性保证**:
- 双重定时执行（18:00 和 18:30）
- 自动重试机制（最多3次）
- 文件完整性验证
- 详细的错误日志

### 2. Cookie维护

**文件**: `.github/workflows/kdocs-maintenance.yml`

**执行时间**: 每4小时

**作用**: 保持水务系统登录状态，确保数据获取不中断

### 3. 健康检查

**执行时间**: 每周一上午9:00

**作用**: 确保系统正常运行，定期唤醒Render服务

---

## 🔧 Render 云端部署

### 部署配置

**服务URL**: https://getwaterdata.onrender.com

**运行命令**: 
```bash
gunicorn --workers=4 --bind=0.0.0.0:$PORT app_unified:app
```

**环境变量**:
- `LOGIN_URL` - 登录地址
- `USERNAME` - 用户名
- `PASSWORD` - 密码
- `REPORT_URL` - 报表地址
- `GITHUB_TOKEN` - GitHub访问令牌（用于自动同步）

### 自动同步机制

当通过Web界面添加月度统计表时，系统会自动：
1. 更新本地Excel文件
2. 执行 Git 操作
3. 推送到GitHub仓库

**同步流程**:
```
Web界面添加数据
    ↓
更新Excel文件
    ↓
Git pull (获取最新代码)
    ↓
修改文件
    ↓
Git commit
    ↓
Git push to GitHub
```

---

## 📁 项目文件结构

```
getwaterdata/
├── app_unified.py                 # 统一Web应用入口
├── add_summary_web.py             # 月度统计核心逻辑
├── integrated_excel_updater.py    # Excel更新引擎
├── force_real_data_web.py         # 数据获取模块
├── specific_excel_writer.py       # Excel写入工具
├── github_automation.py           # GitHub Actions执行脚本
│
├── templates/                     # HTML模板
│   ├── index_unified.html        # 主页
│   ├── add_summary.html          # 月度统计页面
│   ├── index.html                # 数据查询页面
│   └── auto_update.html          # 手动更新页面
│
├── excel_exports/                 # Excel文件目录
│   ├── 石滩供水服务部每日总供水情况.xlsx
│   └── 石滩区分区计量.xlsx
│
├── .github/workflows/             # GitHub Actions配置
│   ├── daily-water-data.yml      # 每日数据更新
│   ├── kdocs-maintenance.yml     # Cookie维护
│   └── auto_update_excel.yml     # 其他自动化任务
│
├── requirements.txt               # Python依赖
├── Procfile                      # Render启动配置
└── runtime.txt                   # Python版本
```

---

## 🔐 安全说明

### 敏感信息管理

1. **GitHub Secrets**
   - `LOGIN_URL` - 存储在GitHub Secrets
   - `USERNAME` - 存储在GitHub Secrets
   - `PASSWORD` - 存储在GitHub Secrets
   - `REPORT_URL` - 存储在GitHub Secrets

2. **Render环境变量**
   - 在Render Dashboard中配置
   - 与GitHub Secrets同步

3. **本地开发**
   - 使用 `config.env` 文件（已在 `.gitignore` 中）
   - 不要将敏感信息提交到Git

### Cookie安全

- Cookie文件自动加密存储
- 定期自动更新
- 不在代码中硬编码

---

## 🐛 故障排查

### 常见问题

#### 1. GitHub Actions执行失败

**可能原因**:
- 网络连接问题
- 登录凭证过期
- 水务系统维护中

**解决方案**:
1. 检查GitHub Secrets配置
2. 手动触发workflow测试
3. 查看Actions日志详情

#### 2. Render服务休眠

**现象**: 首次访问很慢

**原因**: Render免费版15分钟无活动会休眠

**解决方案**:
- 正常现象，等待服务唤醒（约30秒）
- 已配置健康检查定期唤醒

#### 3. Excel文件未同步到GitHub

**检查项**:
1. Render是否配置了 `GITHUB_TOKEN`
2. Token权限是否包含 `repo` 范围
3. 查看Render日志中的 `[GITHUB SYNC]` 部分

**日志示例**:
```
[GITHUB SYNC] Starting synchronization process...
[GITHUB SYNC] File exists: excel_exports/石滩区分区计量.xlsx
[GITHUB SYNC] GITHUB_TOKEN found
[GITHUB SYNC] SUCCESS: Synced to GitHub!
```

#### 4. 数据更新失败

**可能原因**:
- API连接超时
- 数据格式变化
- Excel文件损坏

**解决方案**:
1. 检查网络连接
2. 手动测试API接口
3. 备份并重新生成Excel文件

---

## 📈 监控和维护

### 执行状态查看

1. **GitHub Actions**
   - 访问: https://github.com/jiehuahuang10/getwaterdata/actions
   - 查看每日执行记录
   - 检查成功/失败状态

2. **Render日志**
   - 登录Render Dashboard
   - 查看实时日志
   - 监控系统状态

3. **执行状态文件**
   - `execution_status.md` - 最后执行状态
   - `last_execution_summary.json` - 详细执行摘要

### 日常维护

**每周检查**:
- [ ] GitHub Actions执行记录
- [ ] Excel文件完整性
- [ ] Render服务状态

**每月检查**:
- [ ] 月度统计表是否正确生成
- [ ] 数据准确性验证
- [ ] 日志文件清理

---

## 🔄 数据备份

### 自动备份

- **GitHub**: 所有代码和Excel文件自动版本控制
- **Render**: 每次部署自动从GitHub拉取最新数据

### 手动备份建议

1. **定期下载Excel文件**
   - 从GitHub下载
   - 或通过Web界面下载

2. **导出历史数据**
   - 使用"水务数据查询"功能
   - 导出为Excel备份

---

## 📞 技术支持

### 开发信息

- **项目地址**: https://github.com/jiehuahuang10/getwaterdata
- **在线服务**: https://getwaterdata.onrender.com
- **技术栈**: Python, Flask, Openpyxl, GitHub Actions, Render

### 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 直接修改代码提交PR

---

## 🆕 飞书云空间集成

### 功能特点

- ✅ **自动同步**: 每日更新后自动上传到飞书
- ✅ **多端查看**: 支持手机、电脑、网页多端访问
- ✅ **团队协作**: 可设置权限，方便团队成员查看
- ✅ **实时更新**: 数据更新后立即同步到飞书
- ✅ **安全可靠**: 使用官方 API，数据传输加密

### 使用方法

#### 查看飞书上的数据

1. 打开**飞书**客户端或网页版
2. 点击**云文档**
3. 找到**"石滩供水数据"**文件夹
4. 打开**"石滩供水服务部每日总供水情况.xlsx"**
5. 查看最新数据！

#### 配置飞书同步

详细配置步骤请参考：[FEISHU_SETUP_GUIDE.md](FEISHU_SETUP_GUIDE.md)

需要配置的 GitHub Secrets:
```
FEISHU_APP_ID - 飞书应用 ID
FEISHU_APP_SECRET - 飞书应用密钥
FEISHU_FOLDER_TOKEN - 飞书文件夹 Token
```

### 数据流程

```
水务系统 API
    ↓
GitHub Actions 获取数据
    ↓
更新 Excel 文件
    ↓
┌────────────────┬────────────────┐
│                │                │
↓                ↓                ↓
提交到 GitHub    上传到飞书      保存到 Render
                  云空间
```

### 技术实现

- **飞书 SDK**: 使用官方 API 上传文件
- **自动重试**: 失败自动重试 3 次
- **错误处理**: 飞书同步失败不影响 GitHub 更新
- **日志记录**: 完整的上传日志便于排查问题

---

## 📝 更新日志

### v2.1 (2025-10-25) 🆕
- ✅ 集成飞书云空间自动同步
- ✅ 支持多端查看水务数据
- ✅ 完善飞书集成文档

### v2.0 (2025-10-25)
- ✅ 统一三大功能到单一平台
- ✅ 实现自动GitHub同步
- ✅ 优化每日更新可靠性（双重定时+重试机制）
- ✅ 完善Web界面和用户体验

### v1.0 (2025-08)
- ✅ 实现每日数据自动更新
- ✅ 月度统计表功能
- ✅ 部署到Render云服务

---

## 📄 许可证

本项目仅供内部使用，请勿外传。

---

## ⚠️ 免责声明

- 本系统仅用于水务数据管理，请确保符合相关法律法规
- 请妥善保管登录凭证，避免泄露
- 定期检查数据准确性，系统不对数据错误负责

---

**最后更新**: 2025-10-25
**版本**: v2.0
**维护者**: 石滩供水服务部

