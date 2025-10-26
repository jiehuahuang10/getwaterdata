# 🚀 Vercel部署指南

## 快速开始

### 1. 注册/登录Vercel

访问：https://vercel.com/signup

**推荐使用GitHub账号登录**（可以自动导入仓库）

---

### 2. 导入项目

**方法A：通过Vercel Dashboard（推荐）**

1. 登录后，点击 **"Add New..."** → **"Project"**
2. 选择 **"Import Git Repository"**
3. 找到 `jiehuahuang10/getwaterdata` 仓库
4. 点击 **"Import"**

**方法B：使用CLI**

```bash
# 安装Vercel CLI
npm install -g vercel

# 在项目目录运行
vercel

# 首次运行会提示登录
# 按照提示完成部署
```

---

### 3. 配置环境变量

在Vercel项目设置中添加以下环境变量：

**必需的环境变量**：

```
LOGIN_URL=http://axwater.dmas.cn/Login.aspx
USERNAME=13509288500
PASSWORD=288500
REPORT_URL=http://axwater.dmas.cn/reports/FluxRpt.aspx
```

**添加步骤**：
1. 进入项目 → **Settings** → **Environment Variables**
2. 逐个添加上述变量
3. 选择环境：**Production, Preview, Development**（全选）

**可选环境变量**（如果需要GitHub同步）：

```
GITHUB_TOKEN=your_github_personal_access_token
```

---

### 4. 部署设置

Vercel会自动检测`vercel.json`配置，默认设置已优化：

**配置说明**：
```json
{
  "version": 2,
  "builds": [{
    "src": "app_unified.py",
    "use": "@vercel/python",
    "config": {
      "maxLambdaSize": "50mb"  // 支持大型Excel文件
    }
  }],
  "routes": [{
    "src": "/(.*)",
    "dest": "app_unified.py"   // 所有请求路由到Flask应用
  }],
  "regions": ["hkg1"]          // 使用香港区域（中国访问更快）
}
```

---

### 5. 触发部署

**自动部署**（推荐）：
- 每次`git push`到`main`分支会自动触发部署
- 部署时间：约2-3分钟

**手动部署**：
- 在Vercel Dashboard点击 **"Deployments"**
- 点击 **"Redeploy"**

---

### 6. 访问应用

部署完成后，Vercel会分配一个URL：

```
https://your-project-name.vercel.app
```

**示例**：
```
https://getwaterdata.vercel.app
```

---

## 🔧 常见问题

### Q1: 部署失败，显示"Build Failed"？

**A**: 检查构建日志：
1. 点击失败的部署
2. 查看 **"Building"** 标签下的日志
3. 常见原因：
   - 依赖安装失败（检查`requirements.txt`）
   - Python版本不兼容（Vercel默认Python 3.9）
   - 文件大小超限（检查Excel文件）

**解决方案**：
```bash
# 确保requirements.txt最简化
Flask==2.3.0
openpyxl==3.1.2
Werkzeug==2.3.0
beautifulsoup4==4.12.2
requests==2.31.0
```

---

### Q2: 部署成功但访问报错500？

**A**: 检查运行日志：
1. 进入 **"Functions"** 标签
2. 点击查看函数日志
3. 常见原因：
   - 环境变量未配置
   - Excel文件路径错误
   - 权限问题

**解决方案**：
- 确认所有环境变量已添加
- 检查Excel文件是否在`excel_exports/`目录
- 查看详细错误日志

---

### Q3: Excel文件无法加载？

**A**: Vercel有限制：
- **Lambda函数大小限制**：50MB（已配置）
- **执行时间限制**：10秒（免费版）

**解决方案**：
1. 优化Excel文件大小（删除历史备份）
2. 使用懒加载策略
3. 考虑升级到Pro计划（60秒执行时间）

---

### Q4: 自动化任务（GitHub Actions）如何工作？

**A**: Vercel部署不影响GitHub Actions：
- GitHub Actions仍然每天18:00执行
- 更新Excel文件并push到GitHub
- Vercel自动检测变更并重新部署
- **整个流程自动化，无需人工干预**

---

### Q5: 如何绑定自定义域名？

**A**: 
1. 进入项目 → **Settings** → **Domains**
2. 点击 **"Add Domain"**
3. 输入域名（如：`water.yourdomain.com`）
4. 按照提示配置DNS记录
   - 添加CNAME记录指向`cname.vercel-dns.com`
5. 等待DNS生效（几分钟到几小时）

---

## 🚀 性能优化

### 1. 使用CDN加速

Vercel自动提供全球CDN：
- 静态文件自动缓存
- 动态内容智能路由
- 自动HTTPS

### 2. 区域选择

已配置使用香港区域(`hkg1`)：
- 中国大陆访问速度更快
- 延迟更低

### 3. 冷启动优化

Vercel Serverless函数有冷启动：
- **首次访问**：2-5秒（函数冷启动）
- **后续访问**：<1秒（函数热状态）

**优化建议**：
- 使用Vercel Pro（保持函数温暖）
- 或配置定期心跳请求

---

## 📊 监控和日志

### 查看部署状态
```
Vercel Dashboard → Deployments
```

### 查看运行日志
```
Vercel Dashboard → Functions → View Logs
```

### 查看性能指标
```
Vercel Dashboard → Analytics
```

---

## 💰 费用说明

### 免费版限制
- **带宽**：100GB/月
- **执行时间**：10秒/请求
- **构建时间**：6小时/月
- **并发函数**：12个

**适合场景**：
- 个人项目
- 小团队使用
- 访问量 < 10,000/月

### Pro版（$20/月）
- **带宽**：1TB/月
- **执行时间**：60秒/请求
- **构建时间**：无限制
- **并发函数**：100个
- **自定义域名**：无限制

---

## 🔗 有用链接

- **Vercel文档**：https://vercel.com/docs
- **Python部署指南**：https://vercel.com/docs/frameworks/python
- **环境变量**：https://vercel.com/docs/concepts/projects/environment-variables
- **自定义域名**：https://vercel.com/docs/concepts/projects/custom-domains

---

## ✅ 验证部署

部署完成后，访问以下URL测试：

1. **健康检查**：
   ```
   https://your-app.vercel.app/test
   ```
   应该返回：`{"status": "ok", "version": "2.0"}`

2. **主页**：
   ```
   https://your-app.vercel.app/
   ```
   应该看到三个功能卡片

3. **Excel查看**：
   ```
   https://your-app.vercel.app/view_excel
   ```
   应该加载数据表格

---

## 🎉 部署成功

如果所有测试通过，恭喜！您的应用已成功部署到Vercel！

**下一步**：
- 配置自定义域名
- 设置监控告警
- 优化性能
- 邀请团队成员

---

*最后更新：2025-10-26*


