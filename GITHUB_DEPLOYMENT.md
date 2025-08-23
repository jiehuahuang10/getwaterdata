# 🚀 GitHub Actions 自动化部署指南

## 📋 概述

本项目已配置GitHub Actions，可以每天下午6点自动执行水务数据更新，并将结果保存到Excel文件中。

## 🔧 部署步骤

### 1. 创建GitHub仓库

1. 登录GitHub，创建新仓库
2. 选择 **Public** 仓库（完全免费）或 **Private** 仓库（有免费额度）
3. 将本项目代码上传到仓库

### 2. 配置GitHub Secrets

在仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加以下密钥：

#### 必需的Secrets：
```
LOGIN_URL=你的登录页面URL
USERNAME=你的用户名
PASSWORD=你的密码
REPORT_URL=报表页面URL
```

#### 可选的Secrets（用于邮件通知）：
```
EMAIL_USERNAME=你的邮箱地址
EMAIL_PASSWORD=你的邮箱密码或应用密码
NOTIFICATION_EMAIL=接收通知的邮箱地址
```

### 3. 启用GitHub Actions

1. 进入仓库的 `Actions` 标签页
2. 如果是第一次使用，点击 `I understand my workflows, go ahead and enable them`
3. 工作流将自动启用

## ⏰ 执行时间

- **自动执行**：每天下午6点（北京时间）
- **手动执行**：在Actions页面点击 `Run workflow` 按钮

## 📊 执行结果

### 自动提交
- 更新的Excel文件会自动提交到仓库
- 提交信息格式：`自动更新水务数据 - 2025-08-21 18:00:00`

### 执行日志
- 在 `Actions` 页面查看详细执行日志
- 每次执行会生成 `last_execution_summary.json` 摘要文件

### 邮件通知（可选）
- 配置邮件Secrets后，每次执行完成会发送结果通知
- 包含执行状态和详细日志链接

## 🔍 监控和调试

### 查看执行状态
1. 进入仓库的 `Actions` 页面
2. 点击最新的工作流运行
3. 查看详细日志和执行结果

### 常见问题

#### 1. 执行失败
- 检查Secrets配置是否正确
- 查看详细错误日志
- 确认网络连接正常

#### 2. 没有自动执行
- 确认工作流文件路径正确：`.github/workflows/daily-water-data.yml`
- 检查cron表达式是否正确
- 确认仓库有足够的活动（GitHub可能暂停不活跃仓库的定时任务）

#### 3. Excel文件没有更新
- 检查数据获取是否成功
- 确认Excel文件路径正确
- 查看提交历史确认文件是否被推送

## 🛠️ 自定义配置

### 修改执行时间
编辑 `.github/workflows/daily-water-data.yml` 文件中的cron表达式：
```yaml
schedule:
  # 修改这里的时间 (UTC时间)
  - cron: '0 10 * * *'  # 每天18:00北京时间
```

### 添加更多通知方式
可以添加企业微信、钉钉等通知方式，修改工作流文件即可。

## 💰 费用说明

### Public仓库
- **完全免费** - 无限制执行时间
- 推荐选择（代码公开，但敏感信息在Secrets中安全存储）

### Private仓库
- **免费额度**：每月2000分钟
- 本项目每天执行约2-5分钟，完全在免费范围内

## 🔐 安全说明

- 所有敏感信息（用户名、密码）都存储在GitHub Secrets中
- Secrets在日志中不会显示，确保安全
- 建议使用专门的账户进行数据获取

## 📞 技术支持

如果遇到问题：
1. 查看Actions执行日志
2. 检查 `last_execution_summary.json` 文件
3. 确认所有Secrets配置正确
4. 测试手动执行是否正常

---

🎉 **恭喜！您的水务数据现在可以全自动更新了！**
