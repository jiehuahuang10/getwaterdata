# 下一步操作指南

## ✅ 您已经完成了第一步！

我看到您已经：
1. ✅ 登录了WPS开放平台
2. ✅ 找到了开发者后台
3. ✅ 已经有应用了：**自动化**
4. ✅ 获得了AppID：`AK20251012ADRMHT`

---

## 🔑 现在需要获取AppSecret（1分钟）

### 步骤1: 点击"详情"

在您的截图中，应用"自动化"的右侧有一个**"详情"**按钮，请点击它。

### 步骤2: 查看AppSecret

进入详情页面后，您会看到：

```
AppID: AK20251012ADRMHT
AppSecret: [点击"查看"或"显示"]
```

点击查看AppSecret，会显示一串很长的字符串，类似：
```
1234567890abcdef1234567890abcdef
```

### 步骤3: 复制AppSecret

- 复制整个AppSecret字符串
- **不要分享给任何人！**

---

## 💻 获取AppSecret后的操作（2分钟）

### 步骤1: 创建配置文件

在您的项目文件夹（`d:\pj\getwaterdata`）中：

1. **复制示例配置文件**
   ```bash
   copy wps_config.json.example wps_config.json
   ```

2. **编辑配置文件**
   
   打开 `wps_config.json`，您会看到：
   ```json
   {
     "app_id": "AK20251012ADRMHT",
     "app_secret": "YOUR_APP_SECRET_HERE",
     "kdocs_file_id": "cqagXO1NDs4P",
     "kdocs_link": "https://www.kdocs.cn/l/cqagXO1NDs4P"
   }
   ```

3. **替换AppSecret**
   
   将 `YOUR_APP_SECRET_HERE` 替换为您刚才复制的AppSecret：
   ```json
   {
     "app_id": "AK20251012ADRMHT",
     "app_secret": "您复制的AppSecret",
     "kdocs_file_id": "cqagXO1NDs4P",
     "kdocs_link": "https://www.kdocs.cn/l/cqagXO1NDs4P"
   }
   ```

4. **保存文件**

### 步骤2: 测试API连接

运行测试脚本：
```bash
python wps_api_client.py
```

如果成功，您会看到：
```
============================================================
测试WPS API连接
============================================================
正在获取新的access_token...
Token请求状态码: 200
Token获取成功！
有效期: 7200秒 (2小时)
Token: eyJhbGciOiJIUzI1NiIs...

连接测试成功！
AppID: AK20251012ADRMHT
Token: eyJhbGciOiJIUzI1NiIs...

您可以开始使用WPS API了！
```

---

## 🎯 测试成功后，我会帮您：

1. ✅ **查找WPS的表格操作API**
   - 读取表格数据的API
   - 写入表格数据的API

2. ✅ **集成到现有系统**
   - 替换Cookie认证
   - 实现自动写入KDocs表格
   - 保持现有数据获取逻辑

3. ✅ **部署到GitHub Actions**
   - 将AppID和AppSecret保存为GitHub Secrets
   - 每天自动运行
   - 完全无需手动维护

4. ✅ **彻底解决Cookie过期问题**
   - AppID/AppSecret长期有效
   - Access Token自动刷新
   - 零维护成本

---

## 📞 遇到问题？

### 问题1: 找不到AppSecret的查看按钮

- 尝试点击"编辑"或"管理"
- 或者查看应用设置页面

### 问题2: AppSecret显示为星号

- 点击旁边的"显示"或"眼睛"图标
- 或者重新生成AppSecret

### 问题3: 测试API连接失败

- 检查AppID是否正确
- 检查AppSecret是否正确（包括空格）
- 检查网络连接

---

## 🚀 快速总结

**现在请您做：**
1. 点击"详情"按钮
2. 查看并复制AppSecret
3. 创建 `wps_config.json` 文件
4. 运行 `python wps_api_client.py` 测试

**然后告诉我：**
- "测试成功了！" 或
- 遇到的具体错误信息

**我会立即帮您完成剩下的集成工作！** 🎉

---

## 📝 文件清单

已创建的文件：
- ✅ `wps_config.json.example` - 配置文件示例
- ✅ `wps_api_client.py` - WPS API客户端
- ✅ `NEXT_STEPS.md` - 本文件（操作指南）

待创建：
- `wps_config.json` - 您的实际配置（包含AppSecret）

