# 飞书同步功能配置指南

## 📋 概述

本指南将帮助你完成飞书自动同步功能的最后配置步骤。

---

## ✅ 已完成的工作

1. ✅ 创建了飞书企业自建应用："水务数据自动同步"
2. ✅ 添加了云空间权限 (drive:drive)
3. ✅ 获取了应用凭证 (App ID 和 App Secret)
4. ✅ 创建了飞书文件夹："石滩供水数据"
5. ✅ 获取了文件夹 Token
6. ✅ 编写了飞书同步代码 (`feishu_sync.py`)
7. ✅ 修改了 GitHub Actions 工作流

---

## 🔑 需要添加的 GitHub Secrets

### 步骤1: 访问 GitHub Secrets 设置

1. 打开你的 GitHub 仓库
2. 点击 **Settings** (设置)
3. 在左侧菜单找到 **Secrets and variables** → **Actions**
4. 点击 **New repository secret**

---

### 步骤2: 添加以下 3 个 Secrets

#### Secret 1: FEISHU_APP_ID
```
Name: FEISHU_APP_ID
Value: cli_a87635b460f0d013
```

#### Secret 2: FEISHU_APP_SECRET
```
Name: FEISHU_APP_SECRET
Value: vHHuQtU6ps5jPyQIpx1L0cfeDLeeNBS7
```

#### Secret 3: FEISHU_FOLDER_TOKEN
```
Name: FEISHU_FOLDER_TOKEN
Value: Tc2AfAy4jlxVh5dB4lAckZRyn8d
```

---

## 📸 配置截图参考

### 添加 Secret 的界面应该是这样的：

```
Repository secrets

Name: FEISHU_APP_ID
Secret: cli_a87635b460f0d013

[Add secret]
```

**重要**: 每次只能添加一个 Secret，需要重复 3 次。

---

## 🧪 测试飞书同步功能

### 方法1: 本地测试（可选）

如果你想在本地先测试一下：

```bash
# 设置环境变量
export FEISHU_APP_ID="cli_a87635b460f0d013"
export FEISHU_APP_SECRET="vHHuQtU6ps5jPyQIpx1L0cfeDLeeNBS7"
export FEISHU_FOLDER_TOKEN="Tc2AfAy4jlxVh5dB4lAckZRyn8d"

# 运行测试
python feishu_sync.py
```

**预期结果**:
```
飞书文件上传测试
================================================================================
[飞书] 飞书配置:
  App ID: cli_a87635b460f0d013
  App Secret: vHHuQtU6p...
  Folder Token: Tc2AfAy4jlxVh5dB4lAckZRyn8d
================================================================================
[飞书] 开始获取 tenant_access_token...
[飞书] ✅ 成功获取 access_token
================================================================================
[飞书] 开始上传文件到飞书云空间...
[飞书] 文件路径: excel_exports/石滩供水服务部每日总供水情况.xlsx
[飞书] 文件名: 石滩供水服务部每日总供水情况.xlsx
[飞书] 文件大小: 512.34 KB
[飞书] 正在上传文件...
[飞书] ✅ 文件上传成功！
================================================================================

✅ 测试成功！
```

---

### 方法2: GitHub Actions 测试（推荐）

配置好 Secrets 后，手动触发一次测试：

1. 进入 **Actions** 标签
2. 选择 **"每日水务数据自动更新"** 工作流
3. 点击右侧 **"Run workflow"** 按钮
4. 选择 **"main"** 分支
5. 点击 **"Run workflow"** 开始执行

---

## 📊 查看执行结果

### GitHub Actions 日志

在执行日志中，你应该看到：

```
📤 开始同步文件到飞书云空间...
================================================================================
[飞书] 飞书配置:
  App ID: cli_a87635b460f0d013
  App Secret: vHHuQtU6p...
  Folder Token: Tc2AfAy4jlxVh5dB4lAckZRyn8d
[飞书] ✅ 成功获取 access_token
[飞书] ✅ 文件上传成功！
================================================================================
✅ GitHub Actions执行成功
✅ Excel文件已成功更新并推送到GitHub
✅ 文件已同步到飞书云空间
```

---

### 飞书云文档检查

1. 打开**飞书**
2. 进入**云文档**
3. 找到**"石滩供水数据"**文件夹
4. 应该能看到**"石滩供水服务部每日总供水情况.xlsx"**文件
5. 打开文件，查看数据是否正确

---

## 🔄 自动同步时间表

配置完成后，系统将按照以下时间表自动执行：

| 时间（北京时间） | 说明 |
|----------------|------|
| 每天 18:00 | 主执行时间 |
| 每天 18:30 | 备份执行（防止第一次失败）|
| 每周一 09:00 | 保持活跃（防止 GitHub Actions 休眠）|

---

## 🎯 完整的数据流程

```
每天18:00
    ↓
GitHub Actions 启动
    ↓
登录水务系统获取数据
    ↓
更新本地 Excel 文件
    ↓
【新增】上传到飞书云空间 ✨
    ↓
提交到 GitHub 仓库
    ↓
完成！
```

---

## ❓ 常见问题

### Q: 飞书上传失败怎么办？

**A**: 检查以下几点：
1. GitHub Secrets 是否配置正确（注意大小写）
2. 飞书应用权限是否已开通
3. Folder Token 是否正确
4. 查看 Actions 日志中的错误信息

---

### Q: 文件上传到飞书后，在哪里查看？

**A**: 
1. 打开飞书客户端或网页版
2. 点击"云文档"
3. 找到"石滩供水数据"文件夹
4. 文件名为"石滩供水服务部每日总供水情况.xlsx"

---

### Q: 飞书同步失败会影响 GitHub 更新吗？

**A**: 不会！我们设置了 `continue-on-error: true`，即使飞书同步失败，文件仍然会正常提交到 GitHub。

---

### Q: 可以修改上传到飞书的文件名吗？

**A**: 可以！修改 `feishu_sync.py` 的第 280 行：

```python
# 当前默认文件名
test_file = "excel_exports/石滩供水服务部每日总供水情况.xlsx"

# 也可以在上传时指定不同的文件名
result = sync_excel_to_feishu(
    test_file, 
    folder_token,
    file_name="自定义文件名.xlsx"  # 添加这个参数
)
```

---

### Q: 如何停用飞书同步功能？

**A**: 有两种方法：

**方法1**: 删除 GitHub Secrets
- 删除 `FEISHU_APP_ID`
- 删除 `FEISHU_APP_SECRET`
- 删除 `FEISHU_FOLDER_TOKEN`

**方法2**: 注释掉 GitHub Actions 中的飞书同步步骤
- 编辑 `.github/workflows/daily-water-data.yml`
- 注释掉或删除"同步到飞书云空间"步骤

---

### Q: 飞书 App Secret 泄露了怎么办？

**A**: 立即重置：
1. 进入飞书开放平台
2. 进入应用 → 凭证与基础信息
3. 点击 App Secret 右侧的刷新图标 🔄
4. 复制新的 Secret
5. 更新 GitHub Secret: `FEISHU_APP_SECRET`

---

## 🔐 安全建议

1. **不要** 在代码中硬编码凭证
2. **不要** 在公开场合分享 App Secret
3. **定期** 检查 GitHub Actions 日志
4. **定期** 检查飞书应用权限
5. **如有泄露**，立即重置 App Secret

---

## 📞 技术支持

如果遇到问题：

1. 查看 GitHub Actions 执行日志
2. 查看本文档的"常见问题"部分
3. 检查飞书开放平台的 API 文档：https://open.feishu.cn/document/

---

## 🎉 完成！

配置完成后，你的水务数据将：

✅ 每天自动从水务系统获取  
✅ 自动更新到 GitHub  
✅ 自动同步到飞书云空间  
✅ 支持手机、电脑、网页多端查看  
✅ 团队成员可以方便地访问最新数据  

**享受自动化带来的便利吧！** 🚀

---

**文档版本**: v1.0  
**创建日期**: 2025-10-25  
**最后更新**: 2025-10-25
