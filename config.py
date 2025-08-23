#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水务数据获取系统配置文件
"""

import os
from typing import List

# 默认水表ID列表
DEFAULT_METER_IDS: List[str] = [
    '2501200108',           # 2501200108
    '1261181000263',        # 荔新大道DN1200流量计（修正位数）
    '1261181000300',        # 新塘大道医院DN800流量计（修正位数）
    '1262330402331',        # 宁西总表DN1200（修正位数）
    '2190066',              # 三江新总表DN800
    '2190493',              # 沙庄总表
    '2520005',              # 如丰大道600监控表
    '2520006'               # 三棒桥600监控表
]

# 系统配置
SYSTEM_CONFIG = {
    'base_url': 'http://axwater.dmas.cn',
    'login_path': '/Login.aspx',
    'report_path': '/reports/FluxRpt.aspx',
    'api_path': '/reports/ashx/getRptWaterYield.ashx'
}

# 备用API端点
BACKUP_ENDPOINTS = [
    '/reports/ashx/getWaterData.ashx',
    '/reports/ashx/FluxReport.ashx', 
    '/Handler/WaterYield.ashx',
    '/ajax/getRptData.ashx'
]

# 请求头配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive'
}

# 默认API参数
DEFAULT_API_PARAMS = {
    'meterType': '-1',          # 计量类型（-1表示全部）
    'statisticsType': 'flux',   # 统计类型（流量）
    'type': 'dayRpt'           # 报表类型（日报表）
}

# 日期范围配置（相对于当前日期的天数偏移）
DATE_RANGE_CONFIGS = [
    {'name': '最近7天', 'start_offset': -7, 'end_offset': -1},
    {'name': '上个月同期', 'start_offset': -37, 'end_offset': -30},
    {'name': '去年同期', 'start_offset': -372, 'end_offset': -365}
]

# 固定测试日期范围
FIXED_DATE_RANGES = [
    ('2024-07-24', '2024-07-31'),
    ('2024-12-01', '2024-12-07'),
    ('2025-07-24', '2025-07-31')
]

# 输出配置
OUTPUT_CONFIG = {
    'default_dir': './output',
    'json_indent': 2,
    'csv_encoding': 'utf-8-sig'  # 支持Excel正确显示中文
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'water_data.log'
}

# 重试配置
RETRY_CONFIG = {
    'max_retries': 3,
    'retry_delay': 2,
    'timeout': 15
}
