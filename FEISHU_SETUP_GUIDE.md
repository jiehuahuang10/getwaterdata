# 飞书文档API配置指南

## 🎯 目标

使用飞书文档API实现在线协作的水务数据表格，支持自动更新。

---

## 📋 第一步：注册飞书开放平台

### 1. 访问飞书开放平台

```
https://open.feishu.cn
```

### 2. 注册/登录

- 如果有飞书账号，直接登录
- 如果没有，使用手机号注册（13509289726）

### 3. 创建企业自建应用

1. 登录后，点击**"开发者后台"**或**"创建应用"**
2. 选择**"企业自建应用"**
3. 填写应用信息：
   - **应用名称**: 水务数据自动化
   - **应用描述**: 自动采集水务数据并更新到飞书表格
   - **应用图标**: 可选

4. 创建成功后，您会获得：
   - **App ID**: 类似 `cli_xxxxxxxxxxxxx`
   - **App Secret**: 类似 `xxxxxxxxxxxxxxxxxxxx`

---

## 📋 第二步：配置应用权限

### 1. 进入应用详情

点击刚创建的应用，进入应用管理页面

### 2. 添加应用能力

在左侧菜单找到**"权限管理"**或**"添加应用能力"**

### 3. 开通以下权限

**必需的权限：**

- ✅ **云文档** - `docx:document`
  - 查看、评论和编辑文档
  
- ✅ **电子表格** - `sheets:spreadsheet`
  - 查看和编辑电子表格
  
- ✅ **云空间** - `drive:drive`
  - 访问云空间文件

**具体权限：**
```
bitable:app               # 多维表格
sheets:spreadsheet        # 电子表格读写
drive:drive              # 云空间访问
```

### 4. 发布应用版本

1. 在**"版本管理"**中创建版本
2. 填写版本说明
3. 提交审核（企业自建应用通常秒过）

---

## 📋 第三步：创建飞书表格

### 1. 在飞书中创建表格

1. 打开飞书客户端或网页版
2. 进入**"云文档"**
3. 点击**"新建"** → **"电子表格"**
4. 命名：**石滩供水服务部每日总供水情况**

### 2. 设置表格格式

创建表头（与现有Excel一致）：
```
日期 | 1#水表 | 2#水表 | 3#水表 | 4#水表 | 5#水表 | 6#水表 | 7#水表 | 8#水表
```

### 3. 获取表格ID

1. 打开创建的表格
2. 查看浏览器地址栏，URL格式：
   ```
   https://xxx.feishu.cn/sheets/shtcn***************
   ```
3. 复制 `shtcn***************` 这部分，这是您的**Spreadsheet Token**

---

## 📋 第四步：配置凭证

### 创建配置文件

在项目目录创建 `feishu_config.json`:

```json
{
  "app_id": "您的App ID",
  "app_secret": "您的App Secret",
  "spreadsheet_token": "您的表格Token（shtcn开头）"
}
```

---

## 🔑 关键信息汇总

完成以上步骤后，您需要的信息：

1. **App ID**: `cli_xxxxxxxxxxxxx`
2. **App Secret**: `xxxxxxxxxxxxxxxxxxxx`
3. **Spreadsheet Token**: `shtcnxxxxxxxxxxxxx`

---

## 📞 下一步

获取以上信息后，告诉我：

```
App ID: cli_xxxxxxxxxxxxx
Spreadsheet Token: shtcnxxxxxxxxxxxxx
```

**App Secret 请暂时保密，我会在代码中使用**

然后我会：
1. ✅ 创建飞书API客户端代码
2. ✅ 实现数据自动写入
3. ✅ 测试连接和写入
4. ✅ 部署到GitHub Actions
5. ✅ 完成！

---

## 💡 飞书API优势

- ✅ **Token自动刷新** - Tenant Access Token 2小时有效，可自动刷新
- ✅ **API简单** - 文档清晰，示例丰富
- ✅ **免费使用** - 企业自建应用免费
- ✅ **在线协作** - 多人实时编辑
- ✅ **国内访问快** - 无需魔法上网

---

## 🚀 快速链接

- **飞书开放平台**: https://open.feishu.cn
- **开发者后台**: https://open.feishu.cn/app
- **API文档**: https://open.feishu.cn/document/home/introduction
- **电子表格API**: https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN

---

**准备好了吗？现在就去注册吧！** 🎉

