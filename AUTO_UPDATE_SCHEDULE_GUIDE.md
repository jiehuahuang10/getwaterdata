# ⏰ 自动定时更新 Excel 配置指南

## 📋 功能说明

系统已配置为**每天北京时间下午6点**自动更新 `石滩供水服务部每日总供水情况.xlsx` 文件。

## 🔧 工作原理

```
GitHub Actions (定时触发) 
    ↓
调用 Render API
    ↓
执行数据获取和Excel更新
    ↓
完成更新
```

## ⚙️ 配置详情

### 1. 定时任务配置
- **文件位置**: `.github/workflows/auto_update_excel.yml`
- **执行时间**: 每天北京时间下午 6:00 PM（UTC 10:00 AM）
- **更新日期**: 自动更新**昨天**的数据

### 2. 触发方式

#### 自动触发
- 每天下午6点自动执行
- 无需手动操作

#### 手动触发
1. 访问 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **"定时更新Excel数据"** workflow
4. 点击 **"Run workflow"** 按钮
5. 选择分支并点击 **"Run workflow"**

## 📊 查看执行结果

### 方法一：GitHub Actions 日志
1. 访问仓库的 **Actions** 页面
2. 查看最新的 workflow 运行记录
3. 点击查看详细日志

### 方法二：Render 日志
1. 登录 Render Dashboard
2. 选择 `getwaterdata` 服务
3. 点击 **"Logs"** 查看执行日志

## 🔔 执行状态说明

### ✅ 成功标志
```
✅ Excel更新任务已成功触发
🎉 Excel文件更新成功！
```

### ❌ 失败标志
```
❌ 请求失败
⚠️ 任务触发成功但执行可能有问题
```

## 🛠️ 自定义配置

### 修改执行时间

编辑 `.github/workflows/auto_update_excel.yml` 文件：

```yaml
on:
  schedule:
    # 修改这一行的 cron 表达式
    - cron: '0 10 * * *'  # UTC时间
```

#### Cron 表达式说明
- 格式: `分钟 小时 日 月 星期`
- 时区: **UTC 时间**（北京时间 = UTC + 8）

#### 常用时间配置
| 北京时间 | UTC时间 | Cron表达式 |
|---------|---------|-----------|
| 上午 9:00 | 01:00 | `0 1 * * *` |
| 中午 12:00 | 04:00 | `0 4 * * *` |
| 下午 6:00 | 10:00 | `0 10 * * *` |
| 晚上 9:00 | 13:00 | `0 13 * * *` |

### 修改更新日期

如果需要更新**前天**或**当天**的数据，修改以下部分：

```bash
# 昨天的数据（默认）
date -d '1 day ago' '+%Y-%m-%d'

# 前天的数据
date -d '2 days ago' '+%Y-%m-%d'

# 当天的数据
date '+%Y-%m-%d'
```

## 💰 成本说明

### GitHub Actions
- ✅ **完全免费**
- 每月 2000 分钟免费额度（公共仓库无限制）
- 本任务每次执行约 1-2 分钟

### Render
- ✅ 使用现有的免费 Web 服务
- 不需要额外的 Cron Job 服务（需付费）
- 通过 API 调用实现定时更新

## 🚀 启用定时任务

### 立即启用（无需额外操作）
定时任务已自动配置，只需：

1. **提交并推送代码**
   ```bash
   git add .github/workflows/auto_update_excel.yml
   git commit -m "添加定时更新Excel功能"
   git push
   ```

2. **等待下午6点**
   系统会自动执行更新

3. **或立即测试**
   - 访问 GitHub Actions 页面
   - 手动运行 workflow 测试

## 📝 注意事项

1. **Render 服务必须保持运行**
   - 确保 Render 服务状态为 "Live"
   - 免费版在15分钟无活动后会休眠
   - 定时任务会自动唤醒服务

2. **GitHub Actions 权限**
   - 确保仓库的 Actions 权限已启用
   - Settings → Actions → General → 勾选 "Allow all actions"

3. **时区考虑**
   - Cron 使用 UTC 时间
   - 北京时间（CST）= UTC + 8 小时

4. **执行频率限制**
   - 建议不要设置过于频繁（如每分钟）
   - GitHub Actions 可能会限制过于频繁的执行

## 🔍 故障排查

### 问题：定时任务没有执行
1. 检查 GitHub Actions 是否启用
2. 查看 Actions 页面是否有错误日志
3. 确认 cron 表达式是否正确

### 问题：任务执行失败
1. 查看 GitHub Actions 日志
2. 检查 Render 服务是否正常运行
3. 测试 API 端点是否可访问：
   ```bash
   curl https://getwaterdata.onrender.com/test
   ```

### 问题：Render 服务休眠
- 免费版服务在15分钟无活动后会休眠
- 首次请求会自动唤醒（可能需要30-60秒）
- GitHub Actions 会等待服务响应

## 📞 技术支持

如有问题，请：
1. 查看 GitHub Actions 执行日志
2. 查看 Render 服务日志
3. 检查本文档的故障排查部分

---

**最后更新**: 2025-10-25  
**版本**: v1.0

