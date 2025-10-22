# KDocs登录和自动化指南

## 🎯 目标
实现KDocs文档的自动登录和数据写入，让Python脚本能够自动更新在线Excel表格。

## 📋 准备工作

### 方法1: 使用浏览器Cookie（推荐）

这是最简单的方法，直接使用您已登录的浏览器Cookie。

#### 步骤1: 获取Cookie

1. **打开浏览器**，访问 https://www.kdocs.cn
2. **登录您的账号**（如果还没登录）
3. **打开开发者工具**：
   - Windows/Linux: 按 `F12` 或 `Ctrl+Shift+I`
   - Mac: 按 `Cmd+Option+I`
4. **切换到 Network (网络) 标签**
5. **刷新页面** (F5)
6. **点击任意请求**（通常是第一个）
7. **在右侧找到 Request Headers (请求头)**
8. **找到 Cookie 行**，复制整行的值

**Cookie示例格式**:
```
wps_sid=V02S1234567890abcdef; sensorsdata2015jssdkcross=xxx; kdocs_user_id=123456; ...
```

#### 步骤2: 运行登录脚本

```bash
python kdocs_cookie_login.py
```

按提示粘贴Cookie，脚本会：
- 验证Cookie是否有效
- 保存Cookie到文件（下次自动加载）
- 测试文档访问权限

#### 步骤3: 验证登录

如果看到以下输出，说明登录成功：
```
登录状态: 已登录
文档名称: 石滩供水服务部每日总供水情况 (3)
用户权限: editable
可写入: 1
```

## 🔧 使用方法

### 基本用法

```python
from kdocs_cookie_login import KDocsClient

# 创建客户端（会自动加载已保存的Cookie）
client = KDocsClient()
client.load_cookies()

# 检查登录状态
if client.check_login():
    print("已登录")
    
    # 获取文档信息
    doc_info = client.get_document_info()
    print(doc_info)
```

### 集成到水务数据系统

```python
from kdocs_cookie_login import KDocsClient
from force_real_data_web import force_get_real_data_for_web
from datetime import datetime, timedelta

# 初始化KDocs客户端
kdocs = KDocsClient()
kdocs.load_cookies()

# 获取昨天的水务数据
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
water_data = force_get_real_data_for_web(yesterday)

# 写入到KDocs文档
if water_data:
    # TODO: 实现数据写入逻辑
    print(f"准备写入 {len(water_data)} 个水表的数据")
```

## 🚀 下一步开发

### 需要实现的功能

1. **数据写入API**
   - 研究KDocs的单元格更新API
   - 实现批量数据写入
   - 处理日期和数值格式

2. **错误处理**
   - Cookie过期自动刷新
   - 网络错误重试
   - 数据验证

3. **GitHub Actions集成**
   - 将Cookie作为GitHub Secret
   - 每天自动运行
   - 发送通知

## 🔍 API端点参考

根据浏览器网络请求分析，以下是关键的API端点：

### 登录相关
```
POST https://account.kdocs.cn/api/v3/signIn
GET  https://account.kdocs.cn/api/v3/islogin
```

### 文档操作
```
GET  https://drive.kdocs.cn/api/v5/links/{link_id}
POST https://www.kdocs.cn/api/v3/office/file/{link_id}/open/et
POST https://www.kdocs.cn/api/v3/office/session/{link_id}/et
GET  https://www.kdocs.cn/api/v3/office/file/{file_id}/fonts_config/type/wps
```

### 数据写入（待研究）
```
POST https://www.kdocs.cn/api/v3/office/session/{link_id}/et
- 需要研究具体的数据格式
- 可能需要WebSocket连接
```

## ⚠️ 注意事项

### Cookie安全

1. **不要分享Cookie**
   - Cookie包含您的登录凭证
   - 泄露Cookie = 泄露账号访问权限

2. **定期更新Cookie**
   - Cookie会过期（通常30天）
   - 过期后需要重新获取

3. **使用GitHub Secrets**
   - 在GitHub Actions中使用Cookie时
   - 必须设置为Secret，不要直接写在代码中

### Cookie过期处理

如果Cookie过期，脚本会提示：
```
登录状态: 未登录
Cookie已失效，需要重新获取
```

此时需要：
1. 重新在浏览器中登录KDocs
2. 获取新的Cookie
3. 运行脚本更新Cookie

## 📝 文件说明

- `kdocs_cookie_login.py` - Cookie登录工具
- `kdocs_auto_login.py` - 完整登录工具（支持多种登录方式）
- `kdocs_cookies.json` - 保存的Cookie文件（自动生成）
- `KDOCS_LOGIN_GUIDE.md` - 本文档

## 🐛 故障排除

### 问题1: Cookie无效

**症状**: 提示"登录状态: 未登录"

**解决方案**:
1. 确认浏览器已登录KDocs
2. 重新获取Cookie（完整复制）
3. 检查Cookie格式是否正确

### 问题2: 文档访问失败

**症状**: 返回403或404

**解决方案**:
1. 确认文档链接正确
2. 确认账号有文档访问权限
3. 检查Cookie是否过期

### 问题3: 数据写入失败

**症状**: POST请求返回错误

**解决方案**:
1. 检查数据格式是否正确
2. 确认有文档编辑权限
3. 查看详细错误信息

## 💡 技术细节

### Cookie组成

KDocs的Cookie主要包含：
- `wps_sid` - 会话ID（最重要）
- `sensorsdata2015jssdkcross` - 分析追踪
- `kdocs_user_id` - 用户ID
- 其他辅助Cookie

### 请求头要求

关键的请求头：
```python
{
    'User-Agent': 'Mozilla/5.0 ...',
    'Referer': 'https://www.kdocs.cn/',
    'Cookie': '...'
}
```

### 会话保持

使用`requests.Session()`保持会话：
- 自动管理Cookie
- 保持连接池
- 自动处理重定向

## 📞 获取帮助

如果遇到问题：
1. 查看脚本输出的详细日志
2. 检查网络请求的响应内容
3. 确认浏览器中手动操作是否正常

## ✅ 成功标志

当看到以下输出时，表示一切正常：
```
Cookie有效!
文档访问成功!
用户权限: editable
可写入: 1
```

此时可以开始实现数据写入功能！

