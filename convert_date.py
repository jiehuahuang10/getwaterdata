#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

base = datetime(1899, 12, 30)
print('45870 =', (base + timedelta(days=45870)).strftime('%Y年%m月'))
print('45901 =', (base + timedelta(days=45901)).strftime('%Y年%m月'))

