# -*- coding: utf-8 -*-
import errno
import hashlib
import logging
import os
import re
import sys
import time
from collections import defaultdict
sys.path.append(os.path.abspath("../db"))
from db.mysqlcli import MySQLConnector
from functools import wraps

# 日志工具
logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger("FotoleiPssA")

# 正则匹配工具
reg_positive_int = re.compile(r'^([0-9]*)*$')
reg_int = re.compile(r'^[+-]?([0-9]*)*$')
reg_int_and_float = re.compile(r'^[+-]?([0-9]*)*(\.([0-9]+))?$')


# 通用工具函数 - 过程执行耗时统计器
def cost_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        t = func(*args, **kwargs)
        logger.info("%s tooks time: %f secs", func.__name__, time.time()-start)
        return t
    return wrapper


# 通用工具函数 - 为文件生成摘要
def generate_file_digest(f: str):
    sha256_hash = hashlib.sha256()
    with open(f, "rb") as fin:
        for byte_block in iter(lambda: fin.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


# 通用工具函数 - 为字符串生成摘要
def generate_digest(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# 通用工具函数 - 去除列表中的重复项
def remove_duplicates_for_list(arr :list):
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
def calc_month_num(from_date: str, to_date: str):
    from_t = time.strptime(from_date, "%Y-%m")
    to_t = time.strptime(to_date, "%Y-%m")
    gap_months = (to_t.tm_year - from_t.tm_year) * 12 + (to_t.tm_mon - from_t.tm_mon) + 1
    return gap_months


# 通用工具函数 - 删除文件, 即使文件不存在也不报错
def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


# 数据库连接器 + 查询表
db_connector = MySQLConnector.instance()
db_connector.init_conn("fotolei_pssa")

lookup_table_sku_get_or_put = defaultdict(bool)
lookup_table_inventory_update_without_repetition = defaultdict(bool)
lookup_table_brand_classification_1_2_association = {}
lookup_table_classification_1_2_association = {}
lookup_table_brand_classification_2_association = {}
lookup_table_sku_brand_classification_1_2_association = defaultdict(list)

def init_lookup_table_sku_get_or_put():
    global lookup_table_sku_get_or_put

    stmt = "SELECT specification_code FROM fotolei_pssa.products;"
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            lookup_table_sku_get_or_put[ret[0]] = True
        logger.info("Insert {} SKUs into lookup_table_sku_get_or_put!!!".format(
            len(lookup_table_sku_get_or_put)))

init_lookup_table_sku_get_or_put()


def init_lookup_table_inventory_update_without_repetition():
    global lookup_table_inventory_update_without_repetition

    stmt = "SELECT create_time, specification_code FROM fotolei_pssa.inventories;"
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            lookup_table_inventory_update_without_repetition[generate_digest("{} | {}".format(ret[0], ret[1]))] = True
        logger.info("Insert {} INVENTORIES_UPDATEs into lookup_table_inventory_update_without_repetition!!!".format(
            len(lookup_table_inventory_update_without_repetition)))

init_lookup_table_inventory_update_without_repetition()


def update_lookup_table_brand_classification_1_2_association():
    global lookup_table_brand_classification_1_2_association
    global lookup_table_classification_1_2_association
    global lookup_table_brand_classification_2_association

    # 品牌 -> 分类1 -> 分类2 -> 产品系列 -> 供应商名称
    lookup_table_brand_classification_1_2_association.clear()
    stmt = "SELECT brand, classification_1, classification_2, product_series, supplier_name FROM fotolei_pssa.products;"
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            brand = ret[0]
            classification_1 = ret[1]
            classification_2 = ret[2]
            product_series = ret[3]
            supplier_name = ret[4]
            if brand not in lookup_table_brand_classification_1_2_association.keys():
                lookup_table_brand_classification_1_2_association[brand] = {}
            if classification_1 not in lookup_table_brand_classification_1_2_association[brand].keys():
                lookup_table_brand_classification_1_2_association[brand][classification_1] = {}
            if classification_2 not in lookup_table_brand_classification_1_2_association[brand][classification_1].keys():
                lookup_table_brand_classification_1_2_association[brand][classification_1][classification_2] = {}
            if len(product_series) > 0:
                if product_series not in lookup_table_brand_classification_1_2_association[brand][classification_1][classification_2].keys():
                    lookup_table_brand_classification_1_2_association[brand][classification_1][classification_2][product_series] = set()
                if len(supplier_name) > 0:
                    lookup_table_brand_classification_1_2_association[brand][classification_1][classification_2][product_series].add(supplier_name)
    # 分类1 -> 分类2
    lookup_table_classification_1_2_association.clear()
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            classification_1 = ret[1]
            classification_2 = ret[2]
            if classification_1 not in lookup_table_classification_1_2_association.keys():
                lookup_table_classification_1_2_association[classification_1] = set()
            lookup_table_classification_1_2_association[classification_1].add("{}|{}".format(classification_1, classification_2))
    # 品牌 -> 分类2
    lookup_table_brand_classification_2_association.clear()
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            brand = ret[0]
            classification_2 = ret[2]
            if brand not in lookup_table_brand_classification_2_association.keys():
                lookup_table_brand_classification_2_association[brand] = set()
            lookup_table_brand_classification_2_association[brand].add("{}|{}".format(brand, classification_2))

update_lookup_table_brand_classification_1_2_association()


def init_lookup_table_sku_brand_classification_1_2_association():
    global lookup_table_sku_brand_classification_1_2_association

    stmt = "SELECT specification_code, brand, classification_1, classification_2, is_combined FROM fotolei_pssa.products;"
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            lookup_table_sku_brand_classification_1_2_association[ret[0]].append(ret[1])
            lookup_table_sku_brand_classification_1_2_association[ret[0]].append(ret[2])
            lookup_table_sku_brand_classification_1_2_association[ret[0]].append(ret[3])
            lookup_table_sku_brand_classification_1_2_association[ret[0]].append(ret[4])

init_lookup_table_sku_brand_classification_1_2_association()
