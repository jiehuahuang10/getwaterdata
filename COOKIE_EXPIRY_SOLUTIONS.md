# Cookie过期问题的完整解决方案

## 🎯 问题

KDocs的Cookie通常30天过期，需要定期更新。

## ✅ 解决方案（从简单到复杂）

### 方案1: 自动刷新Cookie（推荐）⭐

**原理**: 每次运行时自动检查Cookie有效性，如果即将过期就自动刷新。

#### 使用方法

```bash
# 每次运行前先刷新Cookie
python kdocs_cookie_refresher.py

# 然后运行主程序
python your_main_script.py
```

#### 集成到现有脚本

```python
from kdocs_cookie_refresher import KDocsCookieRefresher

# 在主程序开始时
refresher = KDocsCookieRefresher()
if not refresher.auto_refresh_if_needed():
    print("Cookie需要手动更新")
    exit(1)

# 继续执行主程序
# ...
```

#### 优点
- ✅ 自动化程度高
- ✅ 无需手动干预（大部分情况）
- ✅ 每次运行都会检查

#### 缺点
- ⚠️ 如果Cookie完全失效，仍需手动更新

---

### 方案2: GitHub Actions自动提醒

**原理**: 定期检查Cookie有效期，快过期时发送通知。

#### 创建检查脚本

```python
# check_cookie_expiry.py
from kdocs_cookie_refresher import KDocsCookieRefresher
import sys

refresher = KDocsCookieRefresher()
need_refresh, reason = refresher.check_cookie_expiry()

if need_refresh:
    print(f"警告: Cookie {reason}")
    sys.exit(1)  # 退出码1表示需要更新
else:
    print(f"正常: Cookie {reason}")
    sys.exit(0)
```

#### GitHub Actions配置

```yaml
# .github/workflows/check-cookie.yml
name: 检查KDocs Cookie

on:
  schedule:
    # 每周一检查一次
    - cron: '0 1 * * 1'
  workflow_dispatch:

jobs:
  check-cookie:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 安装依赖
        run: pip install requests
      
      - name: 恢复Cookie
        run: |
          echo '${{ secrets.KDOCS_COOKIE_JSON }}' > kdocs_cookies.json
      
      - name: 检查Cookie有效期
        id: check
        continue-on-error: true
        run: python check_cookie_expiry.py
      
      - name: 发送通知（如果需要更新）
        if: steps.check.outcome == 'failure'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '⚠️ KDocs Cookie即将过期',
              body: 'KDocs Cookie即将在3天内过期，请及时更新！\n\n更新步骤：\n1. 在浏览器中登录 https://www.kdocs.cn\n2. 复制Cookie\n3. 更新GitHub Secret: KDOCS_COOKIE_JSON'
            })
```

#### 优点
- ✅ 提前3天提醒
- ✅ 自动创建GitHub Issue
- ✅ 不会突然中断

#### 缺点
- ⚠️ 仍需手动更新Cookie

---

### 方案3: 使用长期有效的API Token（如果支持）

**检查KDocs是否支持API Token**

```python
# 查询是否有API Token功能
# 访问 https://www.kdocs.cn/settings/api
# 或 https://account.kdocs.cn/settings
```

如果KDocs支持API Token:
1. 在账户设置中生成Token
2. Token通常有效期更长（1年或永久）
3. 使用Token代替Cookie

#### 优点
- ✅ 有效期长（1年+）
- ✅ 更安全
- ✅ 专门用于API访问

#### 缺点
- ⚠️ 需要KDocs支持此功能
- ⚠️ 可能需要付费账户

---

### 方案4: 保持Cookie活跃

**原理**: 定期访问KDocs来刷新Cookie有效期。

#### GitHub Actions定期访问

```yaml
# .github/workflows/keep-alive.yml
name: 保持KDocs Cookie活跃

on:
  schedule:
    # 每周访问一次
    - cron: '0 2 * * 1'
  workflow_dispatch:

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 安装依赖
        run: pip install requests
      
      - name: 恢复Cookie
        run: |
          echo '${{ secrets.KDOCS_COOKIE_JSON }}' > kdocs_cookies.json
      
      - name: 刷新Cookie
        run: python kdocs_cookie_refresher.py
      
      - name: 保存更新后的Cookie
        run: |
          echo "请将以下内容更新到 KDOCS_COOKIE_JSON:"
          cat kdocs_cookies.json
```

#### 优点
- ✅ 自动保持活跃
- ✅ 延长Cookie有效期
- ✅ 无需频繁手动更新

#### 缺点
- ⚠️ 需要定期运行
- ⚠️ 可能仍会过期

---

### 方案5: 混合方案（最佳实践）⭐⭐⭐

**结合多个方案的优点**

#### 实施步骤

1. **日常运行**: 使用方案1（自动刷新）
   ```python
   # 在主脚本开始时
   refresher = KDocsCookieRefresher()
   refresher.auto_refresh_if_needed()
   ```

2. **定期检查**: 使用方案2（GitHub Actions提醒）
   - 每周检查一次Cookie有效期
   - 快过期时创建Issue提醒

3. **保持活跃**: 使用方案4（定期访问）
   - 每周自动访问一次
   - 延长Cookie有效期

4. **手动备份**: 保存更新流程
   - 文档化Cookie更新步骤
   - 设置日历提醒（每月1号）

#### 完整配置

```yaml
# .github/workflows/kdocs-maintenance.yml
name: KDocs维护

on:
  schedule:
    # 每周一早上9点
    - cron: '0 1 * * 1'
  workflow_dispatch:

jobs:
  maintain:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 安装依赖
        run: pip install requests
      
      - name: 恢复Cookie
        run: |
          echo '${{ secrets.KDOCS_COOKIE_JSON }}' > kdocs_cookies.json
          echo '${{ secrets.KDOCS_COOKIE_META }}' > kdocs_cookie_meta.json
      
      - name: 检查并刷新Cookie
        id: refresh
        continue-on-error: true
        run: python kdocs_cookie_refresher.py
      
      - name: 保存更新后的Cookie
        if: success()
        run: |
          # 这里可以自动提交更新后的Cookie
          # 或者输出到日志供手动更新
          echo "Cookie已刷新"
      
      - name: 发送警告（如果刷新失败）
        if: steps.refresh.outcome == 'failure'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 KDocs Cookie需要手动更新',
              body: '自动刷新失败，请手动更新Cookie！\n\n步骤：\n1. 访问 https://www.kdocs.cn 并登录\n2. 复制Cookie\n3. 更新GitHub Secret: KDOCS_COOKIE_JSON',
              labels: ['urgent', 'maintenance']
            })
```

#### 优点
- ✅ 多重保障
- ✅ 自动化程度最高
- ✅ 提前预警
- ✅ 降低手动维护频率

---

## 📊 方案对比

| 方案 | 自动化程度 | 可靠性 | 维护成本 | 推荐度 |
|------|-----------|--------|---------|--------|
| 方案1: 自动刷新 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 方案2: 自动提醒 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 方案3: API Token | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 方案4: 保持活跃 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 方案5: 混合方案 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎯 推荐实施

### 立即实施（今天）

1. **使用方案1**: 在主脚本中集成自动刷新
   ```python
   from kdocs_cookie_refresher import KDocsCookieRefresher
   
   refresher = KDocsCookieRefresher()
   if not refresher.auto_refresh_if_needed():
       # 发送通知或记录日志
       print("需要手动更新Cookie")
   ```

2. **设置日历提醒**: 每月1号检查Cookie

### 本周内实施

1. **添加GitHub Actions**: 实施方案2（自动提醒）
2. **测试自动刷新**: 确保方案1正常工作

### 长期优化

1. **研究API Token**: 查看KDocs是否支持
2. **实施混合方案**: 多重保障

## 💡 最佳实践

1. **永远保留手动更新方案**: 作为最后的备份
2. **文档化更新流程**: 写清楚更新步骤
3. **设置多个提醒**: GitHub Issue + 日历提醒
4. **定期测试**: 每月测试一次Cookie更新流程

## 🔧 快速开始

```bash
# 1. 测试Cookie刷新
python kdocs_cookie_refresher.py

# 2. 查看Cookie状态
python -c "from kdocs_cookie_refresher import KDocsCookieRefresher; r = KDocsCookieRefresher(); r.load_cookies(); r.check_cookie_expiry()"

# 3. 集成到主脚本
# 在脚本开头添加自动刷新逻辑
```

## 📞 需要帮助？

如果Cookie过期了：
1. 在浏览器中重新登录
2. 运行 `python kdocs_cookie_login.py`
3. 粘贴新Cookie
4. 更新GitHub Secret（如果使用）

**记住**: 自动化是为了减少手动操作，但永远保留手动更新的能力！

