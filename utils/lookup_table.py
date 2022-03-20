# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))

import threading

from collections import defaultdict

from db import db_connector
from .util_funcs import util_generate_digest


_LOOKUP_TABLE_SKU_LOCK = threading.Lock()
_lookup_table_k_sku_v_boolean = defaultdict(bool)
_LOOKUP_TABLE_K_CT_SKU_V_BOOLEAN_LOCK = threading.Lock()
_lookup_table_k_ct_sku_v_boolean = defaultdict(bool)
_LOOKUP_TABLE_K_SKU_V_BRAND_C1_C2_IS_COMBINED_LOCK = threading.Lock()
_lookup_table_k_sku_v_brand_c1_c2_is_combined = defaultdict(list)
_LOOKUP_TABLE_K_C1_V_C1_C2_LOCK = threading.Lock()
_lookup_table_k_c1_v_c1_c2 = defaultdict(set)
_LOOKUP_TABLE_K_BRAND_V_BRAND_C2_LOCK = threading.Lock()
_lookup_table_k_brand_v_brand_c2 = defaultdict(set)
_LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK = threading.Lock()
_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name = {}


def init_lookup_table_k_sku_v_boolean():
    global _lookup_table_k_sku_v_boolean
    with _LOOKUP_TABLE_SKU_LOCK:
        stmt = "SELECT specification_code FROM fotolei_pssa.products;"
        rets = db_connector.query(stmt)
        if type(rets) is list and len(rets) > 0:
            for ret in rets:
                _lookup_table_k_sku_v_boolean[ret[0]] = True


def get_lookup_table_k_sku_v_boolean(sku):
    with _LOOKUP_TABLE_SKU_LOCK:
        return _lookup_table_k_sku_v_boolean.get(sku, False)


def put_lookup_table_k_sku_v_boolean(sku, flag):
    global _lookup_table_k_sku_v_boolean
    with _LOOKUP_TABLE_SKU_LOCK:
        _lookup_table_k_sku_v_boolean[sku] = flag


def clean_lookup_table_k_sku_v_boolean():
    global _lookup_table_k_sku_v_boolean
    with _LOOKUP_TABLE_SKU_LOCK:
        _lookup_table_k_sku_v_boolean.clear()


def init_lookup_table_k_ct_sku_v_boolean():
    global _lookup_table_k_ct_sku_v_boolean
    with _LOOKUP_TABLE_K_CT_SKU_V_BOOLEAN_LOCK:
        stmt = "SELECT create_time, specification_code FROM fotolei_pssa.inventories;"
        rets = db_connector.query(stmt)
        if type(rets) is list and len(rets) > 0:
            for ret in rets:
                _lookup_table_k_ct_sku_v_boolean[util_generate_digest("{} | {}".format(ret[0], ret[1]))] = True


def get_lookup_table_k_ct_sku_v_boolean(ct_sku):
    with _LOOKUP_TABLE_K_CT_SKU_V_BOOLEAN_LOCK:
        return _lookup_table_k_ct_sku_v_boolean.get(ct_sku, False)


def put_lookup_table_k_ct_sku_v_boolean(ct_sku, flag):
    global _lookup_table_k_ct_sku_v_boolean
    with _LOOKUP_TABLE_K_CT_SKU_V_BOOLEAN_LOCK:
        _lookup_table_k_ct_sku_v_boolean[ct_sku] = flag


def clean_lookup_table_k_ct_sku_v_boolean():
    global _lookup_table_k_ct_sku_v_boolean
    with _LOOKUP_TABLE_K_CT_SKU_V_BOOLEAN_LOCK:
        _lookup_table_k_ct_sku_v_boolean.clear()


def init_lookup_table_k_sku_v_brand_c1_c2_is_combined():
    global _lookup_table_k_sku_v_brand_c1_c2_is_combined
    with _LOOKUP_TABLE_K_SKU_V_BRAND_C1_C2_IS_COMBINED_LOCK:
        stmt = "SELECT specification_code, brand, classification_1, classification_2, is_combined FROM fotolei_pssa.products;"
        rets = db_connector.query(stmt)
        # sku -> [品牌 分类1 分类2 是否是组合商品]
        if type(rets) is list and len(rets) > 0:
            for ret in rets:
                _lookup_table_k_sku_v_brand_c1_c2_is_combined[ret[0]].append(ret[1])
                _lookup_table_k_sku_v_brand_c1_c2_is_combined[ret[0]].append(ret[2])
                _lookup_table_k_sku_v_brand_c1_c2_is_combined[ret[0]].append(ret[3])
                _lookup_table_k_sku_v_brand_c1_c2_is_combined[ret[0]].append(ret[4])


def get_lookup_table_k_sku_v_brand_c1_c2_is_combined(sku):
    with _LOOKUP_TABLE_K_SKU_V_BRAND_C1_C2_IS_COMBINED_LOCK:
        return _lookup_table_k_sku_v_brand_c1_c2_is_combined[sku]


def clean_lookup_table_k_sku_v_brand_c1_c2_is_combined():
    global _lookup_table_k_sku_v_brand_c1_c2_is_combined
    with _LOOKUP_TABLE_K_SKU_V_BRAND_C1_C2_IS_COMBINED_LOCK:
        _lookup_table_k_sku_v_brand_c1_c2_is_combined.clear()


def init_lookup_table_k_c1_v_c1_c2():
    global _lookup_table_k_c1_v_c1_c2
    with _LOOKUP_TABLE_K_C1_V_C1_C2_LOCK:
        stmt = "SELECT classification_1, classification_2 FROM fotolei_pssa.products;"
        rets = db_connector.query(stmt)
        # 分类1 -> 分类1|分类2
        _lookup_table_k_c1_v_c1_c2.clear()
        if type(rets) is list and len(rets) > 0:
            for ret in rets:
                classification_1 = ret[0]
                classification_2 = ret[1]
                _lookup_table_k_c1_v_c1_c2[classification_1].add("{}|{}".format(classification_1, classification_2))


def get_lookup_table_k_c1_v_c1_c2(c1):
    with _LOOKUP_TABLE_K_C1_V_C1_C2_LOCK:
        return _lookup_table_k_c1_v_c1_c2[c1]


def get_lookup_table_k_c1_v_c1_c2_keys():
    with _LOOKUP_TABLE_K_C1_V_C1_C2_LOCK:
        return _lookup_table_k_c1_v_c1_c2.keys()


def clean_lookup_table_k_c1_v_c1_c2():
    global _lookup_table_k_c1_v_c1_c2
    with _LOOKUP_TABLE_K_C1_V_C1_C2_LOCK:
        return _lookup_table_k_c1_v_c1_c2.clear()


def init_lookup_table_k_brand_v_brand_c2():
    global _lookup_table_k_brand_v_brand_c2
    with _LOOKUP_TABLE_K_BRAND_V_BRAND_C2_LOCK:
        stmt = "SELECT brand, classification_2 FROM fotolei_pssa.products;"
        rets = db_connector.query(stmt)
        # 品牌 -> 品牌|分类2
        _lookup_table_k_brand_v_brand_c2.clear()
        if type(rets) is list and len(rets) > 0:
            for ret in rets:
                brand = ret[0]
                classification_2 = ret[1]
                _lookup_table_k_brand_v_brand_c2[brand].add("{}|{}".format(brand, classification_2))


def get_lookup_table_k_brand_v_brand_c2(brand):
    with _LOOKUP_TABLE_K_BRAND_V_BRAND_C2_LOCK:
        return _lookup_table_k_brand_v_brand_c2[brand]


def get_lookup_table_k_brand_v_brand_c2_keys():
    with _LOOKUP_TABLE_K_BRAND_V_BRAND_C2_LOCK:
        return _lookup_table_k_brand_v_brand_c2.keys()


def clean_lookup_table_k_brand_v_brand_c2():
    with _LOOKUP_TABLE_K_BRAND_V_BRAND_C2_LOCK:
        _lookup_table_k_brand_v_brand_c2.clear()


def init_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name():
    global _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name
    with _LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK:
        # 品牌 -> 分类1 -> 分类2 -> 产品系列 -> 供应商名称
        _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.clear()
        stmt = "SELECT brand, classification_1, classification_2, product_series, supplier_name FROM fotolei_pssa.products;"
        rets = db_connector.query(stmt)
        if type(rets) is list and len(rets) > 0:
            for ret in rets:
                brand = ret[0]
                classification_1 = ret[1]
                classification_2 = ret[2]
                product_series = ret[3]
                supplier_name = ret[4]
                if brand not in _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.keys():
                    _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand] = {}
                if classification_1 not in _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand].keys():
                    _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand][classification_1] = {}
                if classification_2 not in _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand][classification_1].keys():
                    _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand][classification_1][classification_2] = {}
                if len(product_series) > 0:
                    if product_series not in _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand][classification_1][classification_2].keys():
                        _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand][classification_1][classification_2][product_series] = set()
                    if len(supplier_name) > 0:
                        _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name[brand][classification_1][classification_2][product_series].add(supplier_name)


def get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c1(brand):
    with _LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK:
        return _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.get(brand, {}).keys()


def get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c2(brand, c1):
    with _LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK:
        return _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.get(brand, {}).get(c1, {}).keys()


def get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_product_series(brand, c1, c2):
    with _LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK:
        return _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.get(brand, {}).get(c1, {}).get(c2, {}).keys()


def get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name(brand, c1, c2, product_series):
    with _LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK:
        return _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.get(brand, {}).get(c1, {}).get(c2, {}).get(product_series, set())


def clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name():
    global _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name
    with _LOOKUP_TABLE_K_BRAND_K_C1_K_C2_K_PRODUCT_SERIES_V_SUPPLIER_NAME_LOCK:
        _lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name.clear()
