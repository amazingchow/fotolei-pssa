# -*- coding: utf-8 -*-
import os

import errno
import hashlib
import logging
import logging.handlers
_rotate_file_handler = logging.handlers.WatchedFileHandler(
    filename="{}/fotolei-pssa/logs/fotolei-pssa-profile.log".format(os.path.expanduser("~")),
    mode="a"
)
_rotate_file_handler_formatter = logging.Formatter(
    "[%(asctime)-15s][%(levelname)-5s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
_rotate_file_handler.setFormatter(_rotate_file_handler_formatter)
_profile_logger = logging.getLogger("FotoleiPssA_Profile")
_profile_logger.setLevel(logging.INFO)
_profile_logger.addHandler(_rotate_file_handler)
import time

from functools import wraps


# 通用工具函数 - 过程执行耗时统计器
def util_cost_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        t = func(*args, **kwargs)
        _profile_logger.info("%s tooks time: %f secs", func.__name__, time.time() - start)
        return t
    return wrapper


# 通用工具函数 - 为文件生成摘要
def util_generate_file_digest(f: str):
    sha256_hash = hashlib.sha256()
    with open(f, "rb") as fin:
        for byte_block in iter(lambda: fin.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


# 通用工具函数 - 为字符串生成摘要
def util_generate_digest(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# 通用工具函数 - 去除列表中的重复项
def util_remove_duplicates_for_list(arr: list):
    if len(arr) == 0:
        return []
    arr.sort(reverse=False)
    new_arr = [arr[0]]
    if len(arr) == 1:
        return new_arr
    for i in range(1, len(arr)):
        if arr[i] != arr[i - 1]:
            new_arr.append(arr[i])
    return new_arr


# 通用工具函数 - 计算两个月份之间的月份数
def util_calc_month_num(from_date: str, to_date: str):
    from_t = time.strptime(from_date, "%Y-%m")
    to_t = time.strptime(to_date, "%Y-%m")
    gap_months = (to_t.tm_year - from_t.tm_year) * 12 + (to_t.tm_mon - from_t.tm_mon) + 1
    return gap_months


# 通用工具函数 - 删除文件, 即使文件不存在也不报错
def util_silent_remove(filename: str):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
