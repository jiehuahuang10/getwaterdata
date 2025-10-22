# 🌊 金山文档API集成指南

## 📋 概述

本指南将帮助您将水务数据自动化系统与金山文档在线Excel集成，实现数据的自动同步更新。

## 🚀 快速开始

### 第一步：获取API权限

1. **访问金山文档开放平台**
   - 网址：https://developer.kdocs.cn
   - 使用您的WPS账号登录

2. **创建应用**
   - 点击"创建应用"
   - 填写应用信息：
     - 应用名称：水务数据自动化系统
     - 应用类型：Web应用
     - 回调地址：`http://localhost:5001/callback`

3. **获取应用凭证**
   - 记录下 `App ID` 和 `App Secret`
   - 这两个值需要保密

4. **申请API权限**
   - 在应用管理中申请以下权限：
     - 文件读取权限
     - 文件写入权限
     - 表格操作权限

### 第二步：配置环境变量

在您的系统中设置以下环境变量：

```bash
# Windows (PowerShell)
$env:KDOCS_APP_ID="您的应用ID"
$env:KDOCS_APP_SECRET="您的应用密钥"

# Linux/Mac
export KDOCS_APP_ID="您的应用ID"
export KDOCS_APP_SECRET="您的应用密钥"
```

### 第三步：安装依赖

```bash
pip install requests flask
```

### 第四步：OAuth授权

运行授权助手完成首次授权：

```bash
python kdocs_oauth_helper.py
```

这将：
1. 启动本地授权服务器
2. 自动打开浏览器
3. 引导您完成OAuth授权
4. 保存访问令牌到本地

### 第五步：测试同步

```bash
python kdocs_water_data_sync.py
```

## 📊 功能说明

### 1. API客户端 (`kdocs_api_client.py`)

核心API客户端，提供以下功能：
- OAuth授权管理
- 访问令牌自动刷新
- 文件信息获取
- 表格数据读写
- 错误处理和重试

### 2. OAuth授权助手 (`kdocs_oauth_helper.py`)

简化OAuth授权流程：
- 自动启动本地服务器
- 图形化授权界面
- 自动保存令牌
- 错误处理

### 3. 数据同步器 (`kdocs_water_data_sync.py`)

水务数据同步功能：
- 从本地JSON文件读取数据
- 智能匹配Excel列
- 自动查找或创建日期行
- 批量更新数据

## 🔧 集成到现有系统

### 方案1：扩展Web界面

在 `web_app_fixed.py` 中添加金山文档同步功能：

```python
from kdocs_water_data_sync import WaterDataKDocsSync

# 添加新的路由
@app.route('/sync_to_kdocs', methods=['POST'])
def sync_to_kdocs():
    try:
        data = request.get_json()
        target_date = data.get('target_date')
        
        # 创建同步器
        sync = WaterDataKDocsSync("https://www.kdocs.cn/l/ctPsso05tvI4")
        
        # 查找最新数据文件
        import glob
        data_files = glob.glob("WEB_COMPLETE_8_METERS_*.json")
        if data_files:
            latest_file = max(data_files, key=lambda x: os.path.getmtime(x))
            success = sync.sync_from_local_data(latest_file, target_date)
            
            if success:
                return jsonify({'success': True, 'message': '同步成功'})
            else:
                return jsonify({'success': False, 'message': '同步失败'})
        else:
            return jsonify({'success': False, 'message': '未找到数据文件'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'同步异常: {str(e)}'})
```

### 方案2：GitHub Actions集成

在 `.github/workflows/daily-water-data.yml` 中添加同步步骤：

```yaml
- name: 同步到金山文档
  run: |
    python kdocs_water_data_sync.py
  env:
    KDOCS_APP_ID: ${{ secrets.KDOCS_APP_ID }}
    KDOCS_APP_SECRET: ${{ secrets.KDOCS_APP_SECRET }}
  continue-on-error: true
```

## 🛠️ 配置说明

### 水表名称映射

在 `kdocs_water_data_sync.py` 中的 `meter_mapping` 字典定义了系统水表名称到Excel列名的映射：

```python
self.meter_mapping = {
    '荔新大道DN1200流量计': '荔新大道',
    '新城大道医院DN800流量计': '新城大道',
    '三江新总表DN800（2190066）': '三江新总表',
    # ... 更多映射
}
```

### Excel列映射

`column_mapping` 字典定义了Excel列名到列号的映射：

```python
self.column_mapping = {
    '日期': 'A',
    '石滩供水服务部日供水': 'B',
    '环比差值': 'C',
    # ... 更多映射
}
```

## 🔍 故障排除

### 常见问题

1. **授权失败**
   - 检查App ID和App Secret是否正确
   - 确认回调地址配置正确
   - 检查网络连接

2. **文件访问失败**
   - 确认您有文档的编辑权限
   - 检查文件ID是否正确
   - 验证API权限申请

3. **数据更新失败**
   - 检查Excel列映射是否正确
   - 确认数据格式符合要求
   - 查看错误日志

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 高级功能

### 1. 批量历史数据同步

```python
from datetime import datetime, timedelta

sync = WaterDataKDocsSync("https://www.kdocs.cn/l/ctPsso05tvI4")

# 同步最近7天的数据
for i in range(7):
    date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')
    sync.sync_from_local_data("latest_data.json", date)
```

### 2. 定时同步任务

```python
import schedule
import time

def sync_daily_data():
    sync = WaterDataKDocsSync("https://www.kdocs.cn/l/ctPsso05tvI4")
    sync.sync_from_local_data("latest_data.json")

# 每天18:30执行同步
schedule.every().day.at("18:30").do(sync_daily_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 3. 双向同步

```python
# 从金山文档读取数据
data = sync.client.get_sheet_data(sync.file_id, 'sheet1', 'A1:P100')

# 处理数据并同步到本地
# ... 数据处理逻辑
```

## 🔒 安全注意事项

1. **保护应用凭证**
   - 不要将App ID和App Secret提交到代码仓库
   - 使用环境变量或配置文件
   - 定期更换密钥

2. **访问令牌管理**
   - 令牌文件权限设置为仅当前用户可读
   - 定期检查令牌有效性
   - 实现自动刷新机制

3. **API调用限制**
   - 遵守API调用频率限制
   - 实现重试和退避机制
   - 监控API使用量

## 📞 技术支持

如果在集成过程中遇到问题：

1. 查看金山文档开放平台文档：https://developer.kdocs.cn
2. 检查本地日志文件
3. 验证网络连接和权限设置

---

**集成完成后，您的水务数据将自动同步到金山文档，实现真正的云端协作！** 🎉
