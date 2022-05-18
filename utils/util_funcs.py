# -*- coding: utf-8 -*-
import os

import errno
import hashlib
import io
import random
import time

from datetime import datetime
from dateutil.relativedelta import relativedelta


# 通用工具函数 - 为存储在磁盘上的文件内容生成摘要
def util_generate_bytes_in_hdd_digest(filename: str):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


# 通用工具函数 - 为存储在内存中的内容生成摘要
def util_generate_bytes_in_mem_digest(bytes_io: io.BytesIO):
    sha256_hash = hashlib.sha256()
    with bytes_io as stream:
        for byte_block in iter(lambda: stream.read(4096), b""):
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
def util_calc_month_num(from_date_str: str, to_date_str: str):
    from_t = time.strptime(from_date_str, "%Y-%m")
    to_t = time.strptime(to_date_str, "%Y-%m")
    gap_months = (to_t.tm_year - from_t.tm_year) * 12 + (to_t.tm_mon - from_t.tm_mon) + 1
    return gap_months


# 通用工具函数 - 罗列两个月份之间的所有月份，前闭后开
def util_get_all_months_between_two_months(from_date_str: str, to_date_str: str):
    all_months = []
    from_t = datetime.strptime(from_date_str, "%Y-%m")
    to_t = datetime.strptime(to_date_str, "%Y-%m")

    all_months.append(from_date_str)
    while 1:
        t = from_t + relativedelta(months=1)
        if to_t == t:
            break
        all_months.append(t.strftime("%Y-%m"))
        from_t = t

    return all_months


# 通用工具函数 - 删除文件, 即使文件不存在也不报错
def util_silent_remove(filename: str):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


ALL_DIGIT_NUMS_AND_LETTERS = [str(i) for i in range(0, 10)] + \
    [str(chr(i)) for i in range(ord('a'), ord('z') + 1)] + \
    [str(chr(i)) for i in range(ord('A'), ord('Z') + 1)]
ALL_DIGIT_NUMS_AND_LETTERS_TOTAL = len(ALL_DIGIT_NUMS_AND_LETTERS)


# 通用工具函数 - 生成N位字符串, 字符串由数字和大小写字母组成
def util_generate_n_digit_nums_and_letters(n: int):
    for i in range(len(ALL_DIGIT_NUMS_AND_LETTERS) - 1, 0, -1):
        j = random.randrange(i + 1)
        ALL_DIGIT_NUMS_AND_LETTERS[i], ALL_DIGIT_NUMS_AND_LETTERS[j] = ALL_DIGIT_NUMS_AND_LETTERS[j], ALL_DIGIT_NUMS_AND_LETTERS[i]
    nums_and_letters = [ALL_DIGIT_NUMS_AND_LETTERS[random.randrange(ALL_DIGIT_NUMS_AND_LETTERS_TOTAL)] for _ in range(n)]
    return "".join(nums_and_letters)
