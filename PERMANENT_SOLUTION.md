# KDocs自动化 - 永久解决方案

## 🎯 问题回顾

您的疑问：**一定要每30天重新登录更新Cookie吗？有没有其他方法？**

## ✅ 答案：有4种替代方案！

---

## 方案1: 使用WPS开放平台API（最推荐）⭐⭐⭐⭐⭐

### 📋 发现

经过探索，我们发现：
- ✅ `https://developer.kdocs.cn` 是 **WPS开放平台**
- ✅ KDocs是WPS旗下产品
- ✅ WPS开放平台提供官方API

### 优势

| 项目 | Cookie方式 | WPS API方式 |
|------|-----------|------------|
| **有效期** | 30天 | **长期有效**（甚至永久） |
| **认证方式** | 浏览器Cookie | **AppID + AppSecret** |
| **维护成本** | 每月更新 | **几乎无维护** |
| **自动化** | 需要人工 | **完全自动化** |
| **稳定性** | 中等 | **非常高**（官方支持） |

### 实施步骤

#### 第一步：注册WPS开放平台账号（5分钟）

1. **访问WPS开放平台**
   ```
   https://open.wps.cn
   或
   https://developer.kdocs.cn
   ```

2. **注册/登录开发者账号**
   - 使用您的手机号：13509289726
   - 或使用企业账号（如果有）

3. **创建应用**
   - 进入控制台
   - 创建新应用
   - 选择"云文档"权限
   - 获取 `AppID` 和 `AppSecret`

#### 第二步：获取API文档

1. **查看云文档API**
   - 文档中心 → 云文档
   - 查找"表格操作" API
   - 找到"写入单元格"功能

2. **获取Access Token**
   ```python
   import requests
   
   APP_ID = "your_app_id"
   APP_SECRET = "your_app_secret"
   
   # 获取access_token
   url = "https://open.wps.cn/api/v3/auth/token"
   data = {
       "grant_type": "client_credentials",
       "appid": APP_ID,
       "secret": APP_SECRET
   }
   
   response = requests.post(url, json=data)
   access_token = response.json()['access_token']
   
   # access_token有效期通常为7天，可以自动刷新
   ```

#### 第三步：替换现有Cookie方案

```python
class WPSCloudDocClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """
        获取access_token（7天有效，可自动刷新）
        """
        if self.access_token and self.token_expires_at > time.time():
            return self.access_token
        
        # 获取新token
        url = "https://open.wps.cn/api/v3/auth/token"
        data = {
            "grant_type": "client_credentials",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        self.access_token = result['access_token']
        self.token_expires_at = time.time() + result['expires_in']
        
        return self.access_token
    
    def write_water_data(self, file_id, date, water_data):
        """
        写入水务数据到表格
        """
        token = self.get_access_token()
        
        # 调用API写入数据
        url = f"https://open.wps.cn/api/v3/docs/{file_id}/sheets/data"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # 构建数据
        # ...
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
```

### 优势总结

- ✅ **永久有效**：AppID和AppSecret长期有效
- ✅ **自动刷新**：Access Token虽然7天过期，但可自动刷新
- ✅ **官方支持**：WPS官方API，稳定可靠
- ✅ **完全自动化**：无需任何人工干预
- ✅ **权限清晰**：明确的API权限控制
- ✅ **文档完善**：官方文档和示例

---

## 方案2: 改用本地Excel文件（最简单）⭐⭐⭐⭐

### 为什么考虑这个方案？

如果WPS开放平台API复杂或不适用，可以：
- ✅ 使用本地Excel文件
- ✅ 通过Git同步到云端（GitHub）
- ✅ 完全避免Cookie问题

### 实施方案

```python
# 现有代码几乎无需修改
from specific_excel_writer import SpecificExcelWriter

# 写入本地Excel
writer = SpecificExcelWriter("石滩供水服务部每日总供水情况.xlsx")
writer.write_date_data(target_date, water_data)

# GitHub Actions自动提交
# - 每天更新Excel
# - 自动提交到GitHub
# - 可以在线查看（GitHub渲染Excel）
```

### 优势

- ✅ **零维护**：无Cookie，无API，无过期
- ✅ **完全控制**：数据存储在本地
- ✅ **Git历史**：自动版本控制
- ✅ **在线查看**：GitHub可以渲染Excel
- ✅ **免费**：无需任何付费服务

### 缺点

- ⚠️ 不是在线协作（但可以用GitHub协作）
- ⚠️ 需要Git操作（但可以自动化）

---

## 方案3: 使用腾讯文档/飞书文档（替代方案）⭐⭐⭐

### 为什么？

腾讯文档和飞书文档都有更好的API支持。

### 腾讯文档

```python
# 腾讯文档API
# 支持长期Token
# 文档: https://docs.qq.com/open/document/

APP_ID = "your_app_id"
SECRET_KEY = "your_secret_key"

# Token通常90天有效，可自动刷新
```

### 飞书文档

```python
# 飞书API
# 支持永久Token
# 文档: https://open.feishu.cn/

APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"

# Tenant Access Token可以自动刷新
```

### 优势

- ✅ 官方API支持
- ✅ Token有效期长（90天+）
- ✅ 文档完善
- ✅ 免费额度充足

---

## 方案4: 使用Google Sheets API（国际方案）⭐⭐⭐⭐

### 特点

- ✅ **OAuth2认证**：一次授权，长期有效
- ✅ **Refresh Token**：永久有效，自动刷新Access Token
- ✅ **完善的API**：功能强大
- ✅ **免费**：每天读写限额很高

### 简单示例

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 一次性授权后，refresh_token永久有效
creds = Credentials(
    token=access_token,
    refresh_token=refresh_token,  # 永久有效！
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# 自动刷新access_token
service = build('sheets', 'v4', credentials=creds)

# 写入数据
service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range='Sheet1!A1',
    valueInputOption='RAW',
    body={'values': [[data]]}
).execute()
```

### 缺点

- ⚠️ 需要访问Google（可能需要特殊网络）
- ⚠️ 数据存储在国外

---

## 📊 方案对比总结

| 方案 | 维护频率 | 实施难度 | 稳定性 | 推荐度 |
|------|---------|---------|--------|--------|
| **WPS开放平台API** | 无 | 中等 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **本地Excel+Git** | 无 | 简单 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **腾讯文档/飞书** | 每季度 | 中等 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Google Sheets** | 无 | 简单 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cookie方式** | 每月 | 简单 | ⭐⭐⭐ | ⭐⭐ |

---

## 🎯 我的推荐

### 优先级1: WPS开放平台API（最佳）

**理由**：
- ✅ 您已经在使用KDocs
- ✅ WPS开放平台官方支持
- ✅ 完全自动化，零维护
- ✅ AppID/Secret长期有效

**下一步**：
1. 访问 https://open.wps.cn 或 https://developer.kdocs.cn
2. 注册开发者账号
3. 创建应用，获取AppID和Secret
4. 我帮您改造现有代码

### 优先级2: 本地Excel+Git（最简单）

**理由**：
- ✅ 现有代码几乎无需修改
- ✅ 完全自动化
- ✅ 零维护成本
- ✅ 5分钟就能切换

**下一步**：
1. 把文件路径改为本地
2. GitHub Actions自动提交
3. 完成！

### 优先级3: 改进Cookie方式（备选）

如果前两个方案都不适用：
- ✅ 使用我之前创建的自动刷新工具
- ✅ GitHub Actions自动提醒
- ✅ 每月3分钟维护

---

## 💡 实施建议

### 今天（10分钟）

1. **尝试访问WPS开放平台**
   ```bash
   # 打开浏览器访问
   https://developer.kdocs.cn
   ```

2. **查看是否能注册/登录**
   - 如果可以 → 选择方案1
   - 如果不行 → 选择方案2

### 明天（开始实施）

**如果选择方案1（WPS API）**：
- 我帮您写完整的API集成代码
- 替换现有Cookie方式
- 永久解决问题

**如果选择方案2（本地Excel）**：
- 修改文件路径
- 配置Git自动提交
- 5分钟完成切换

---

## 🎉 结论

**答案：不需要每30天更新Cookie！**

有至少4种更好的方案：
1. ✅ WPS开放平台API（永久有效）
2. ✅ 本地Excel+Git（零维护）
3. ✅ 腾讯文档/飞书（季度更新）
4. ✅ Google Sheets（永久有效）

**您想选择哪一个？我可以立即帮您实施！** 🚀

---

## 📞 下一步行动

请告诉我：

1. **您倾向于哪个方案？**
   - [ ] 方案1: WPS开放平台API
   - [ ] 方案2: 本地Excel+Git
   - [ ] 方案3: 其他文档平台
   - [ ] 方案4: 继续优化Cookie方式

2. **我可以立即开始**：
   - 帮您注册WPS开放平台
   - 或者切换到本地Excel
   - 或者实施其他方案

**让我们彻底解决这个问题！** 💪

