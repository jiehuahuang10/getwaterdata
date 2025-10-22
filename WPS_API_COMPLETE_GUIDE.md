# WPS开放平台API完整指南

## ✅ 好消息！我找到了WPS API的位置！

经过测试，以下是可用的WPS API平台：

---

## 📍 第一步：访问WPS开放平台

### 主入口（必看）

```
网址: https://open.wps.cn
状态: ✅ 可访问
说明: WPS官方开放平台主站
```

### 其他入口

- **API文档**: https://open.wps.cn/docs
- **开发者控制台**: https://open.wps.cn/console
- **应用管理**: https://open.wps.cn/apps
- **WebOffice文档**: https://solution.wps.cn/docs

---

## 📋 第二步：注册开发者账号（5分钟）

### 详细步骤

1. **打开浏览器，访问**
   ```
   https://open.wps.cn
   ```

2. **点击右上角"登录"或"注册"**
   - 如果已有WPS账号，直接登录
   - 如果没有，使用手机号注册

3. **使用您的手机号注册**
   ```
   手机号: 13509289726
   ```
   - 输入手机号
   - 接收验证码
   - 设置密码
   - 完成注册

4. **登录成功后**
   - 会看到开放平台首页
   - 顶部有"控制台"、"文档中心"等菜单

---

## 🔧 第三步：创建应用（获取AppID和AppSecret）

### 进入控制台

1. **点击顶部菜单的"控制台"**
   ```
   网址: https://open.wps.cn/console
   ```

2. **如果是第一次使用**
   - 可能需要完善个人信息
   - 阅读并同意开发者协议

### 创建新应用

1. **在控制台页面，点击"创建应用"或"新建应用"**

2. **选择应用类型**
   
   根据您的需求选择：
   
   **选项A: WebOffice（推荐）**
   - 适用于在线编辑Excel、Word等
   - 支持表格读写操作
   - 功能最完整
   
   **选项B: 云文档**
   - 适用于文档存储和管理
   - 支持文件操作
   
   **选项C: 轻文档**
   - 适用于轻量级协作
   - 简单易用

3. **填写应用信息**
   ```
   应用名称: 水务数据自动化系统
   应用简介: 自动获取水务数据并更新到表格
   应用类型: Web应用
   回调地址: http://localhost:5000 (本地测试用)
   ```

4. **提交申请**
   - 个人开发者：通常立即通过
   - 企业用户：可能需要企业认证

5. **获取凭证**
   
   创建成功后，您会看到：
   ```
   AppID: AK20xxxxxxxxxx (类似这样的字符串)
   AppSecret: xxxxxxxxxxxxxxxx (点击"查看"显示)
   ```
   
   **⚠️ 重要：请妥善保管AppSecret，不要泄露！**

---

## 📚 第四步：查看API文档

### 主要文档位置

1. **文档中心首页**
   ```
   https://open.wps.cn/docs
   ```

2. **WebOffice API文档**（如果选择WebOffice）
   ```
   https://solution.wps.cn/docs
   ```

3. **查找表格操作API**
   
   在文档中搜索：
   - "表格" 或 "spreadsheet"
   - "单元格" 或 "cell"
   - "写入" 或 "write"
   - "更新" 或 "update"

### 常用API端点（示例）

```python
# 1. 获取访问凭证
POST https://open.wps.cn/api/v3/auth/token
参数:
{
    "grant_type": "client_credentials",
    "appid": "YOUR_APPID",
    "secret": "YOUR_APPSECRET"
}

# 2. 获取文件列表
GET https://open.wps.cn/api/v3/files
Headers:
{
    "Authorization": "Bearer ACCESS_TOKEN"
}

# 3. 读取表格数据
GET https://open.wps.cn/api/v3/spreadsheet/{fileId}/values
Headers:
{
    "Authorization": "Bearer ACCESS_TOKEN"
}

# 4. 写入表格数据
POST https://open.wps.cn/api/v3/spreadsheet/{fileId}/values
Headers:
{
    "Authorization": "Bearer ACCESS_TOKEN"
}
Body:
{
    "range": "Sheet1!A1:B2",
    "values": [["日期", "用水量"], ["2025-01-10", "1000"]]
}
```

**注意：以上是示例端点，实际API请以官方文档为准！**

---

## 💻 第五步：测试API连接

创建测试脚本：

```python
import requests
import time

class WPSOpenAPI:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self):
        """
        获取访问令牌
        """
        # 如果token还有效，直接返回
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        # 获取新token
        url = "https://open.wps.cn/api/v3/auth/token"
        data = {
            "grant_type": "client_credentials",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                # token有效期通常是7200秒（2小时）
                expires_in = result.get('expires_in', 7200)
                self.token_expires_at = time.time() + expires_in - 60  # 提前1分钟刷新
                
                print(f"获取token成功，有效期: {expires_in}秒")
                return self.access_token
            else:
                print(f"获取token失败: {result}")
                return None
        
        except Exception as e:
            print(f"请求出错: {e}")
            return None
    
    def test_connection(self):
        """
        测试连接
        """
        token = self.get_access_token()
        
        if token:
            print(f"连接成功!")
            print(f"Access Token: {token[:20]}...")
            return True
        else:
            print("连接失败")
            return False

# 使用示例
if __name__ == "__main__":
    # 替换为您的实际凭证
    APP_ID = "YOUR_APPID_HERE"
    APP_SECRET = "YOUR_APPSECRET_HERE"
    
    client = WPSOpenAPI(APP_ID, APP_SECRET)
    client.test_connection()
```

---

## 🎯 第六步：集成到您的项目

一旦获取到AppID和AppSecret，我会帮您：

1. **改造现有代码**
   - 替换Cookie认证为AppID/Secret认证
   - 实现自动获取和刷新access_token
   - 保持现有的数据获取和处理逻辑

2. **实现数据写入**
   - 调用WPS API写入表格
   - 保持与现有Excel格式一致
   - 处理错误和重试

3. **部署到GitHub Actions**
   - 将AppID和AppSecret保存为Secrets
   - 每天自动运行
   - 完全无需人工干预

---

## ❓ 常见问题

### Q1: 找不到"创建应用"按钮？

**A**: 可能需要：
1. 完善个人信息
2. 同意开发者协议
3. 刷新页面重试

### Q2: 提示需要"企业认证"？

**A**: 
- 基础API通常个人也可以使用
- 如果确实需要企业认证，可以考虑方案2（本地Excel）

### Q3: 不确定选择哪种应用类型？

**A**: 
- 推荐选择"WebOffice"
- 功能最全，文档最完善
- 适合表格操作

### Q4: API文档看不懂？

**A**: 
- 没关系！您只需要获取AppID和AppSecret
- 剩下的代码我来写
- 我会处理所有API调用细节

### Q5: 如果实在注册不了怎么办？

**A**: 
- 可以改用方案2：本地Excel + Git
- 5分钟就能切换完成
- 完全不需要任何API

---

## 📞 需要帮助？

### 现在请您做：

1. **访问** https://open.wps.cn
2. **注册/登录** 开发者账号
3. **创建应用** 获取AppID和AppSecret
4. **告诉我** 您获取到的AppID（AppSecret保密，暂时不要发送）

### 然后我会：

1. ✅ 帮您写完整的API集成代码
2. ✅ 测试API连接
3. ✅ 实现数据写入功能
4. ✅ 部署到GitHub Actions
5. ✅ 彻底解决Cookie过期问题

---

## 🚀 快速链接

- **主站**: https://open.wps.cn
- **控制台**: https://open.wps.cn/console
- **文档**: https://open.wps.cn/docs
- **WebOffice文档**: https://solution.wps.cn/docs

---

**准备好了吗？现在就去注册吧！有任何问题随时告诉我！** 🎉

