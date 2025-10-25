# 飞书同步功能 - 快速配置指南 ✅

## 📋 你需要做的最后一步

### 添加 GitHub Secrets（3 个）

1. **访问 GitHub 仓库设置**
   ```
   https://github.com/jiehuahuang10/getwaterdata/settings/secrets/actions
   ```

2. **点击 "New repository secret" 添加以下 3 个密钥**：

---

### Secret 1️⃣ : FEISHU_APP_ID
```
Name: FEISHU_APP_ID
Value: cli_a87635b460f0d013
```

### Secret 2️⃣ : FEISHU_APP_SECRET
```
Name: FEISHU_APP_SECRET
Value: vHHuQtU6ps5jPyQIpx1L0cfeDLeeNBS7
```

### Secret 3️⃣ : FEISHU_FOLDER_TOKEN
```
Name: FEISHU_FOLDER_TOKEN
Value: Tc2AfAy4jlxVh5dB4lAckZRyn8d
```

---

## ✅ 配置完成后

### 测试方法

1. **进入 GitHub Actions**
   ```
   https://github.com/jiehuahuang10/getwaterdata/actions
   ```

2. **选择 "每日水务数据自动更新" 工作流**

3. **点击 "Run workflow" → 选择 "main" → 点击 "Run workflow"**

4. **等待执行完成（约 2-3 分钟）**

5. **查看日志，确认看到**：
   ```
   📤 开始同步文件到飞书云空间...
   [飞书] ✅ 成功获取 access_token
   [飞书] ✅ 文件上传成功！
   ✅ Excel文件已成功更新并推送到GitHub
   ✅ 文件已同步到飞书云空间
   ```

---

## 🎉 使用飞书查看数据

### 电脑端
1. 打开飞书客户端
2. 点击"云文档"
3. 找到"石滩供水数据"文件夹
4. 打开"石滩供水服务部每日总供水情况.xlsx"

### 手机端
1. 打开飞书 App
2. 点击"工作台" → "云文档"
3. 找到"石滩供水数据"
4. 点击 Excel 文件查看

### 网页版
1. 访问 https://feishu.cn
2. 登录后进入"云文档"
3. 找到文件夹并打开

---

## 📊 自动同步时间表

| 时间 | 说明 |
|------|------|
| 每天 18:00 | 主执行时间 |
| 每天 18:30 | 备份执行 |
| 每周一 09:00 | 保持活跃 |

---

## 📞 遇到问题？

查看详细文档：
- [FEISHU_SETUP_GUIDE.md](FEISHU_SETUP_GUIDE.md) - 完整配置指南
- [FEISHU_INTEGRATION_PLAN.md](FEISHU_INTEGRATION_PLAN.md) - 技术方案说明
- [PROJECT_README.md](PROJECT_README.md) - 项目文档

---

## 🎯 核心信息速查

| 项目 | 值 |
|------|-----|
| 飞书应用名称 | 水务数据自动同步 |
| App ID | cli_a87635b460f0d013 |
| 文件夹名称 | 石滩供水数据 |
| Folder Token | Tc2AfAy4jlxVh5dB4lAckZRyn8d |
| 文件名 | 石滩供水服务部每日总供水情况.xlsx |

---

**配置时间**: 约 5 分钟  
**难度**: ⭐ 简单  
**效果**: 🌟🌟🌟🌟🌟

立即配置，让团队随时随地查看最新水务数据！🚀

