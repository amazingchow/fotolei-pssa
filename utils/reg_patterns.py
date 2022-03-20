# -*- coding: utf-8 -*-
import re

# 正则匹配工具
REG_INT = re.compile(r'^[+-]?([0-9]*)*$')
REG_INT_AND_FLOAT = re.compile(r'^[+-]?([0-9]*)*(\.([0-9]+))?$')
REG_POSITIVE_INT = re.compile(r'^([0-9]*)*$')
