# KDocs Cookie管理 - 快速开始

## 🎯 目标

解决Cookie每30天过期的问题，实现自动化维护。

## ✅ 推荐方案：自动刷新 + 自动提醒

### 第一步：首次设置Cookie（5分钟）

1. **在浏览器中登录KDocs**
   ```
   访问: https://www.kdocs.cn
   账号: 13509289726
   密码: 1456987bcA$$
   ```

2. **获取Cookie**
   - 按 `F12` 打开开发者工具
   - 切换到 `Console` 标签
   - 输入并回车：`document.cookie`
   - 复制输出的整行内容

3. **保存Cookie到本地**
   ```bash
   python kdocs_cookie_login.py
   ```
   - 粘贴刚才复制的Cookie
   - 看到"Cookie有效!"表示成功

4. **保存Cookie到GitHub（用于自动化）**
   - 进入GitHub仓库: `Settings` → `Secrets and variables` → `Actions`
   - 点击 `New repository secret`
   - 添加两个Secret:
     
     **Secret 1:**
     - Name: `KDOCS_COOKIE_JSON`
     - Value: 复制 `kdocs_cookies.json` 文件的全部内容
     
     **Secret 2:**
     - Name: `KDOCS_COOKIE_META`
     - Value: 复制 `kdocs_cookie_meta.json` 文件的全部内容

### 第二步：启用自动维护（2分钟）

1. **查看GitHub Actions配置**
   - 文件已创建: `.github/workflows/kdocs-maintenance.yml`
   - 功能: 每周一自动检查Cookie状态

2. **手动测试一次**
   - 进入GitHub仓库的 `Actions` 标签
   - 选择 `KDocs Cookie维护` 工作流
   - 点击 `Run workflow` → `Run workflow`
   - 等待运行完成（约1分钟）

3. **查看结果**
   - ✅ 绿色勾号 = Cookie正常
   - ❌ 红色叉号 = 需要更新Cookie
   - 如果失败，会自动创建Issue提醒你

### 第三步：集成到主程序（可选）

如果你想在每次运行主程序时自动检查Cookie：

```python
# 在你的主脚本开头添加
from kdocs_cookie_refresher import KDocsCookieRefresher

# 自动检查并刷新Cookie
refresher = KDocsCookieRefresher()
if not refresher.auto_refresh_if_needed():
    print("警告: Cookie需要手动更新")
    # 可以选择退出或继续
    # exit(1)

# 继续执行你的主程序
# ...
```

## 📅 维护计划

### 自动维护（无需操作）

- ✅ **每周一早上9点**: GitHub Actions自动检查Cookie
- ✅ **Cookie快过期时**: 自动创建Issue提醒
- ✅ **每次运行时**: 自动刷新Cookie（如果集成到主程序）

### 手动维护（每月一次）

**当收到GitHub Issue提醒时：**

1. 在浏览器中重新登录 https://www.kdocs.cn
2. 获取新Cookie（按F12 → Console → `document.cookie`）
3. 运行 `python kdocs_cookie_login.py` 并粘贴Cookie
4. 更新GitHub Secrets:
   - `KDOCS_COOKIE_JSON` = `kdocs_cookies.json` 的内容
   - `KDOCS_COOKIE_META` = `kdocs_cookie_meta.json` 的内容
5. 关闭Issue

**预计时间**: 3分钟

## 🔧 常用命令

```bash
# 检查Cookie状态
python kdocs_cookie_refresher.py

# 更新Cookie
python kdocs_cookie_login.py

# 仅检查有效期（用于测试）
python check_cookie_expiry.py
```

## 📊 工作流程图

```
┌─────────────────────────────────────────────────┐
│  每周一 GitHub Actions 自动检查                    │
└─────────────────┬───────────────────────────────┘
                  │
                  ├─ Cookie有效 (剩余 > 3天)
                  │  └─ ✅ 继续使用
                  │
                  ├─ Cookie即将过期 (剩余 < 3天)
                  │  └─ 🔄 尝试自动刷新
                  │      ├─ 成功 → ✅ 继续使用
                  │      └─ 失败 → ⚠️ 创建Issue提醒
                  │
                  └─ Cookie已失效
                     └─ ⚠️ 创建Issue提醒
                         └─ 👤 手动更新 (3分钟)
```

## ⚠️ 重要提示

1. **Cookie安全**
   - Cookie = 账号访问权限
   - 不要分享给他人
   - 使用GitHub Secrets加密存储

2. **定期检查**
   - 每月1号检查一次GitHub Actions运行状态
   - 确保没有未读的Issue

3. **备份方案**
   - 永远保留手动更新的能力
   - 文档保存在 `COOKIE_EXPIRY_SOLUTIONS.md`

## 🎯 预期效果

- ✅ **自动化程度**: 95%（每月只需3分钟手动操作）
- ✅ **可靠性**: 高（多重检查机制）
- ✅ **维护成本**: 极低（自动提醒）

## 📞 遇到问题？

### Cookie无法保存
```bash
# 检查文件权限
ls -l kdocs_cookies.json

# 手动创建文件
touch kdocs_cookies.json
python kdocs_cookie_login.py
```

### GitHub Actions失败
1. 检查Secrets是否正确设置
2. 查看Actions日志找到错误信息
3. 手动运行 `python kdocs_cookie_refresher.py` 测试

### Cookie频繁过期
- 可能是账号安全设置问题
- 尝试在浏览器中勾选"记住我"
- 联系KDocs客服咨询

## 🚀 下一步

完成以上设置后，你的KDocs Cookie将：
- ✅ 自动检查有效期
- ✅ 自动刷新（大部分情况）
- ✅ 自动提醒更新（少数情况）
- ✅ 每月只需3分钟维护

**开始吧！** 🎉

