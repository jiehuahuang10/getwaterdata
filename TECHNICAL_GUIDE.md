# 石滩供水数据管理系统 - 技术文档

## 🏗️ 系统架构

### 技术栈

```
前端层
├── HTML5 + CSS3
├── JavaScript (Vanilla)
└── 响应式设计

后端层
├── Flask 2.3.3 (Web框架)
├── Openpyxl 3.1.2 (Excel处理)
├── Requests 2.31.0 (HTTP请求)
└── Python 3.9+

自动化层
├── GitHub Actions (CI/CD)
└── Cron定时任务

云服务层
├── Render (Web托管)
└── GitHub (代码托管+数据存储)
```

---

## 📦 核心模块

### 1. app_unified.py - 统一应用入口

**职责**: 
- Flask应用主入口
- 路由管理
- API接口定义
- GitHub同步逻辑

**主要路由**:
```python
/ - 主页
/summary - 月度统计表管理
/data - 水务数据查询
/auto_update - 手动数据更新
/add_summary - 添加统计表API
/download_excel/<filename> - Excel下载
```

**关键函数**:
```python
def prepare_git_before_modify()
    # 在修改文件前先从GitHub拉取最新代码
    
def sync_excel_to_github(file_path, commit_message)
    # 将Excel文件同步到GitHub
    # 1. 检查文件存在
    # 2. 配置Git
    # 3. 添加文件
    # 4. 提交
    # 5. 推送到远程
```

---

### 2. add_summary_web.py - 月度统计核心

**职责**:
- 从日供水数据提取月度汇总
- 生成月度统计表
- Excel格式化和样式设置

**主要函数**:
```python
def add_monthly_summary_to_main(
    month_offset=1, 
    use_real_data=True,
    sale_values=[]
)
```

**数据提取逻辑**:
```python
# 1. 计算目标月份的日期范围
target_month = datetime.now() + relativedelta(months=month_offset)
start_date = target_month.replace(day=1) - timedelta(days=7)
end_date = start_date + timedelta(days=days_in_month + 6)

# 2. 从Excel提取数据
for row in range(start_row, end_row + 1):
    date_value = ws.cell(row=row, column=1).value
    if start_date <= date_value <= end_date:
        # 累加各水表数据
        
# 3. 生成统计表
# 4. 应用格式（边框、居中、百分比）
```

---

### 3. integrated_excel_updater.py - Excel更新引擎

**职责**:
- 获取实时水表数据
- 更新每日供水情况Excel
- 数据验证和格式化

**执行流程**:
```python
def update_excel_with_real_data(target_date):
    # 1. 获取实时水务数据
    water_data = get_real_water_data_direct(target_date)
    
    # 2. 提取水表数据
    extracted_data = extract_meter_values(water_data)
    
    # 3. 写入Excel
    writer = SpecificExcelWriter(excel_file)
    result = writer.write_data(extracted_data)
    
    # 4. 返回结果
    return {
        'success': True,
        'updated_meters': len(extracted_data),
        'target_date': target_date
    }
```

---

### 4. force_real_data_web.py - 数据获取模块

**职责**:
- 从水务系统API获取数据
- Cookie管理
- 数据解析和缓存

**API调用**:
```python
def get_real_water_data_direct(target_date):
    # 1. 加载Cookie
    cookies = load_kdocs_cookies()
    
    # 2. 构建请求
    headers = {...}
    data = {
        'startTime': target_date,
        'endTime': target_date
    }
    
    # 3. 发送请求
    response = requests.post(
        REPORT_URL,
        headers=headers,
        cookies=cookies,
        json=data,
        timeout=30
    )
    
    # 4. 解析响应
    return parse_water_data(response.json())
```

---

## 🔄 GitHub Actions工作流

### 每日数据更新 (daily-water-data.yml)

```yaml
触发条件:
  - cron: '0 10 * * *'   # 每天18:00(北京时间)
  - cron: '30 10 * * *'  # 每天18:30(北京时间)备份
  - workflow_dispatch     # 手动触发

执行步骤:
  1. 检出代码
  2. 设置Python环境
  3. 安装依赖
  4. 创建配置文件
  5. 执行更新（带重试）
  6. 验证Excel文件
  7. 提交到GitHub
  8. 更新状态徽章
```

**重试机制**:
```bash
MAX_RETRIES=3
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if python github_automation.py; then
    SUCCESS=true
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 30
  fi
done
```

---

### Cookie维护 (kdocs-maintenance.yml)

```yaml
触发条件:
  - cron: '0 */4 * * *'  # 每4小时
  - workflow_dispatch     # 手动触发

执行步骤:
  1. 运行cookie更新脚本
  2. 验证cookie有效性
  3. 提交更新的cookie文件
```

---

## 🔐 安全架构

### 1. 环境变量管理

```
开发环境:
config.env (本地，不提交到Git)

GitHub Actions:
GitHub Secrets
├── LOGIN_URL
├── USERNAME
├── PASSWORD
└── REPORT_URL

Render:
Environment Variables
├── LOGIN_URL
├── USERNAME
├── PASSWORD
├── REPORT_URL
└── GITHUB_TOKEN
```

### 2. GitHub同步认证

```python
# 使用Personal Access Token
repo_url = f'https://{github_token}@github.com/user/repo.git'

# Git配置
git config user.email "render-bot@getwaterdata.com"
git config user.name "Render Auto Sync"
git remote set-url origin {repo_url}

# 执行同步
git pull origin main
git add file
git commit -m "message"
git push origin main
```

### 3. Cookie安全

```python
# Cookie文件结构
{
    "session_id": "encrypted_value",
    "timestamp": "2025-10-25T10:00:00",
    "expires": "2025-10-26T10:00:00"
}

# 自动更新机制
每4小时 → 检查有效性 → 如需要则重新登录 → 更新cookie
```

---

## 📊 数据流转

### 完整数据流程

```
水务系统API
    ↓ (HTTP Request)
Cookie认证
    ↓
获取JSON数据
    ↓ (解析)
提取8个水表读数
    ↓ (验证)
写入Excel文件
    ↓ (Openpyxl)
提交到GitHub
    ↓ (Git Push)
GitHub存储
    ↓ (Git Pull)
Render服务同步
```

### 月度统计数据流

```
Excel日供水数据
    ↓ (读取指定日期范围)
提取各水表月度数据
    ↓ (累加计算)
用户输入售水量
    ↓ (计算)
损耗水量 = 供水量 - 售水量
    ↓ (计算)
水损耗率 = 损耗水量 / 供水量
    ↓ (格式化)
生成月度统计表
    ↓ (应用样式)
写入Excel
    ↓ (Git同步)
推送到GitHub
```

---

## 🛠️ Excel处理技术

### Openpyxl核心操作

```python
# 1. 加载工作簿
wb = openpyxl.load_workbook('file.xlsx')
ws = wb['Sheet1']

# 2. 读取数据
value = ws.cell(row=1, column=1).value

# 3. 写入数据
ws.cell(row=1, column=1, value='data')

# 4. 合并单元格
ws.merge_cells('A1:J1')

# 5. 设置样式
from openpyxl.styles import Font, Alignment, Border, Side

cell.font = Font(bold=True, size=12)
cell.alignment = Alignment(horizontal='center', vertical='center')
cell.border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# 6. 设置数字格式
cell.number_format = '0.00%'  # 百分比
cell.number_format = '0'       # 整数

# 7. 保存
wb.save('file.xlsx')
```

### 数据定位策略

```python
# 方法1: 扫描查找（灵活）
for row in range(1, ws.max_row + 1):
    if ws.cell(row=row, column=1).value == target_date:
        # 找到目标行
        
# 方法2: 计算偏移（快速）
# 假设数据从第3行开始，每天一行
row_index = 3 + days_offset

# 方法3: 查找标题（可靠）
for row in range(1, 100):
    if '监控表供水量' in str(ws.cell(row=row, column=2).value):
        header_row = row
        break
```

---

## 🔧 部署配置

### Render配置

**Procfile**:
```
web: gunicorn --workers=4 --bind=0.0.0.0:$PORT --timeout=120 app_unified:app
```

**runtime.txt**:
```
python-3.10.0
```

**requirements.txt**:
```
Flask==2.3.3
openpyxl==3.1.2
python-dateutil==2.8.2
gunicorn==21.2.0
requests==2.31.0
beautifulsoup4==4.12.2
```

### 环境变量

| 变量名 | 用途 | 示例值 |
|--------|------|--------|
| `LOGIN_URL` | 登录API地址 | `https://api.example.com/login` |
| `USERNAME` | 用户名 | `admin` |
| `PASSWORD` | 密码 | `******` |
| `REPORT_URL` | 报表API地址 | `https://api.example.com/report` |
| `GITHUB_TOKEN` | GitHub访问令牌 | `ghp_xxxxx` |
| `PORT` | 服务端口（Render自动设置） | `10000` |

---

## 🐛 调试技巧

### 1. 本地调试

```python
# 启用Flask调试模式
app.run(debug=True, host='0.0.0.0', port=5000)

# 添加日志
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("Debug message")
```

### 2. 查看Render日志

```bash
# 在Render Dashboard:
Shell → 查看实时日志

# 或通过Render CLI:
render logs -a app-name
```

### 3. GitHub Actions调试

```yaml
# 添加调试步骤
- name: Debug Info
  run: |
    echo "Current directory: $(pwd)"
    echo "Python version: $(python --version)"
    echo "Files: $(ls -la)"
    echo "Environment: $(env)"
```

### 4. Excel文件调试

```python
# 打印工作表信息
print(f"Sheet names: {wb.sheetnames}")
print(f"Active sheet: {wb.active.title}")
print(f"Max row: {ws.max_row}")
print(f"Max column: {ws.max_column}")

# 导出CSV用于检查
import csv
with open('debug.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for row in ws.iter_rows(values_only=True):
        writer.writerow(row)
```

---

## 📈 性能优化

### 1. Excel读写优化

```python
# 使用read_only模式（只读）
wb = openpyxl.load_workbook('file.xlsx', read_only=True)

# 使用write_only模式（只写）
wb = openpyxl.Workbook(write_only=True)

# 批量操作而非逐个单元格
values = [[1, 2, 3], [4, 5, 6]]
for row in values:
    ws.append(row)
```

### 2. API请求优化

```python
# 使用session复用连接
session = requests.Session()
session.headers.update({'User-Agent': 'Custom'})

# 设置合理的超时
response = session.get(url, timeout=(5, 30))  # (连接超时, 读取超时)

# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_data(date):
    return fetch_data(date)
```

### 3. 减少重复计算

```python
# 缓存计算结果
_cache = {}

def get_month_data(month):
    if month in _cache:
        return _cache[month]
    
    result = calculate_month_data(month)
    _cache[month] = result
    return result
```

---

## 🧪 测试

### 单元测试示例

```python
import unittest
from add_summary_web import add_monthly_summary_to_main

class TestMonthlySummary(unittest.TestCase):
    def test_add_summary(self):
        result = add_monthly_summary_to_main(
            month_offset=1,
            use_real_data=False,
            sale_values=[100, 200, 300]
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['rows_added'], 3)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```bash
# 测试API端点
curl http://localhost:5000/get_info

# 测试数据更新
python github_automation.py

# 测试Excel写入
python integrated_excel_updater.py
```

---

## 📝 代码规范

### Python代码风格

```python
# 使用类型提示
def process_data(value: int) -> dict:
    return {'result': value * 2}

# 使用docstring
def calculate_loss(supply: float, sales: float) -> float:
    """
    计算水损耗量
    
    Args:
        supply: 供水量
        sales: 售水量
    
    Returns:
        损耗水量
    """
    return supply - sales

# 异常处理
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return {'success': False, 'error': str(e)}
```

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式化
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关

示例:
feat: add retry mechanism to daily update
fix: resolve Excel file sync issue
docs: update user guide
```

---

## 🔮 未来扩展

### 可能的功能扩展

1. **数据可视化**
   - 添加图表展示
   - 趋势分析
   - 异常检测

2. **多用户支持**
   - 用户认证
   - 权限管理
   - 操作日志

3. **移动App**
   - React Native
   - Flutter
   - 推送通知

4. **报警系统**
   - 数据异常报警
   - 执行失败通知
   - 邮件/短信通知

5. **数据备份**
   - 定时备份到云存储
   - 版本历史管理
   - 一键恢复

---

**文档版本**: v2.0  
**最后更新**: 2025-10-25  
**维护者**: 技术团队

