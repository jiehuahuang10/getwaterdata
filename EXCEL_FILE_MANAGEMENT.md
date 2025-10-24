# 📊 Excel 文件管理说明

## 🎯 **当前系统的文件流程**

### 1. 文件存储位置

#### GitHub 仓库（永久存储）
```
github.com/jiehuahuang10/getwaterdata/
├── excel_exports/
│   ├── 石滩供水服务部每日总供水情况.xlsx  ← 主要数据文件
│   └── 石滩区分区计量.xlsx               ← 月度统计文件
```

#### Render 服务器（临时存储）
```
/opt/render/project/src/
├── excel_exports/
│   ├── 石滩供水服务部每日总供水情况.xlsx  ← 从GitHub复制过来
│   └── 石滩区分区计量.xlsx               ← 从GitHub复制过来
```

### 2. 当前工作流程

#### 部署时（Git Push）
```
1. 你在本地修改代码
2. git push 到 GitHub
3. Render 自动部署
4. Render 从 GitHub 复制所有文件（包括 Excel）
```

#### 使用功能时
```
【月度统计表添加】
1. 读取：Render 上的 石滩区分区计量.xlsx
2. 读取数据源：Render 上的 石滩供水服务部每日总供水情况.xlsx
3. 修改：在 Render 服务器上修改 石滩区分区计量.xlsx
4. 保存：保存到 Render 服务器

【自动更新Excel】
1. 获取水务系统数据
2. 读取：Render 上的 石滩供水服务部每日总供水情况.xlsx
3. 修改：在 Render 服务器上修改此文件
4. 保存：保存到 Render 服务器
```

## ⚠️ **关键问题：数据丢失风险**

### 问题 1：Render 重启会丢失所有修改
```
❌ Render 免费版使用临时文件系统
❌ 服务重启/重新部署后，所有 Excel 修改会丢失
❌ 每次部署都会用 GitHub 上的旧文件覆盖
```

### 问题 2：本地和 Render 的数据不同步
```
场景：
1. 你在 Render 网页上添加了 10 月份的月度统计
2. Excel 文件在 Render 服务器上已更新
3. 但 GitHub 上的文件还是旧的
4. 你在本地做了其他修改，git push
5. Render 重新部署，用 GitHub 的旧文件覆盖
6. 10 月份的数据丢失！
```

## ✅ **推荐的解决方案**

### 方案 A：手动下载-更新-上传（简单但麻烦）

#### 步骤：
1. **使用功能前**：确保 GitHub 上的 Excel 是最新的
2. **使用功能后**：
   - 在 Render Shell 中下载修改后的文件
   - 提交到 GitHub
   - 或在本地同步

#### 下载文件的方法：
在 Render Shell 中执行：
```bash
# 查看文件
ls -la excel_exports/

# 使用 cat + base64 输出文件内容（然后复制到本地）
base64 excel_exports/石滩区分区计量.xlsx
```

### 方案 B：使用 GitHub API 自动同步（推荐）

#### 优点：
- ✅ 完全自动化
- ✅ 每次修改都实时同步到 GitHub
- ✅ 数据永久保存

#### 实现步骤：

##### 1. 创建 GitHub Personal Access Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选权限：
   - `repo` (完整权限)
4. 生成并复制 token（注意：只显示一次！）

##### 2. 在 Render 配置环境变量
1. Render Dashboard → 选择服务 → Settings → Environment
2. 添加环境变量：
   ```
   Key: GITHUB_TOKEN
   Value: ghp_xxxxxxxxxxxxxxxxxxxx  (你的 token)
   ```

##### 3. 修改代码自动同步
修改后的代码会在每次 Excel 操作后自动提交到 GitHub。

### 方案 C：使用云存储（可选）

#### 优点：
- ✅ 独立于 Git 仓库
- ✅ 不占用 Git 空间
- ✅ 访问速度快

#### 支持的云存储：
- 阿里云 OSS
- 腾讯云 COS
- AWS S3
- Google Drive API

## 🚀 **建议的最佳实践**

### 短期方案（立即可用）

1. **每次使用前**：
   ```bash
   # 在本地
   git pull  # 确保本地是最新的
   ```

2. **每次使用后**：
   - 在 Render Shell 中查看文件是否有更新：
     ```bash
     ls -l excel_exports/*.xlsx
     stat excel_exports/石滩区分区计量.xlsx
     ```
   
   - 如果你知道文件已更新，在本地执行：
     ```bash
     # 手动下载并提交
     # （需要先从 Render 获取文件）
     git add excel_exports/*.xlsx
     git commit -m "更新Excel文件"
     git push
     ```

### 长期方案（推荐实施）

**实施 GitHub API 自动同步**：
1. 配置 GitHub Token（见上文）
2. 部署更新后的代码
3. 系统会自动同步所有 Excel 修改到 GitHub

## 📝 **当前文件使用情况**

### 石滩供水服务部每日总供水情况.xlsx
- **用途**：存储每日8个水表的数据
- **更新频率**：每天（通过"自动更新Excel"功能）
- **数据来源**：水务系统 API
- **风险**：⚠️ 高风险 - 每天更新，丢失会影响数据连续性

### 石滩区分区计量.xlsx  
- **用途**：月度统计表
- **更新频率**：每月（通过"月度统计表添加"功能）
- **数据来源**：从"石滩供水服务部每日总供水情况.xlsx"提取
- **风险**：⚠️ 中风险 - 每月更新一次，但手动重建困难

## 🎯 **立即行动建议**

### 选项 1：接受现状，手动管理（免费）
- 每次使用后手动备份 Excel
- 定期从本地上传最新版本

### 选项 2：实施自动同步（免费 + 15分钟设置）
1. 创建 GitHub Token
2. 配置到 Render 环境变量
3. 我帮你修改代码实现自动同步
4. 部署更新

### 选项 3：升级 Render 计划（付费）
- 使用 Render 的持久化磁盘
- 月费约 $7
- 永久保存文件

---

**你希望我帮你实施哪个方案？**

1. **方案 B - GitHub API 自动同步**（推荐，免费）
2. **方案 A - 手动管理**（接受现状）
3. **方案 C - 云存储集成**（需要云服务账号）

告诉我你的选择，我会协助你完成配置！

