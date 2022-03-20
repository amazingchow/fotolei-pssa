# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import platform

from flask import jsonify
from flask import request

from . import blueprint
from db import db_connector
from utils import clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name
from utils import clean_lookup_table_k_brand_v_brand_c2
from utils import clean_lookup_table_k_c1_v_c1_c2
from utils import clean_lookup_table_k_sku_v_boolean
from utils import clean_lookup_table_k_sku_v_brand_c1_c2_is_combined
from utils import util_cost_count
from utils import util_silent_remove


# 删除所有商品条目的接口
@blueprint.route("/api/v1/products/all/clean", methods=["POST"])
@util_cost_count
def clean_all_products():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.products;"
        db_connector.drop_table(stmt)
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.product_summary;"
        db_connector.drop_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.products (
    id                 INT           NOT NULL AUTO_INCREMENT,
    product_code       VARCHAR(64),            /* 商品编码 */
    product_name       VARCHAR(128),           /* 商品名称 */
    specification_code VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name VARCHAR(128),           /* 规格名称 */
    brand              VARCHAR(64),            /* 品牌 */
    classification_1   VARCHAR(64),            /* 分类1 */
    classification_2   VARCHAR(64),            /* 分类2 */
    product_series     VARCHAR(64),            /* 产品系列 */
    stop_status        VARCHAR(32),            /* STOP状态 */
    product_weight     FLOAT,                  /* 重量/g */
    product_length     FLOAT,                  /* 长度/cm */
    product_width      FLOAT,                  /* 宽度/cm */
    product_height     FLOAT,                  /* 高度/cm */
    is_combined        VARCHAR(32),            /* 是否是组合商品 */
    be_aggregated      VARCHAR(32),            /* 是否参与统计 */
    is_import          VARCHAR(32),            /* 是否是进口商品 */
    supplier_name      VARCHAR(128),           /* 供应商名称 */
    purchase_name      VARCHAR(128),           /* 采购名称 */
    jit_inventory      INT,                    /* 实时可用库存 */
    moq                INT,                    /* 最小订货单元 */
    PRIMARY KEY (id),
    KEY products_specification_code (specification_code),
    KEY products_is_combined_product_series (is_combined, product_series),
    KEY products_is_combined_stop_status_be_aggregated_supplier_name (is_combined, stop_status, be_aggregated, supplier_name)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.product_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        if platform.system() == "Linux":
            util_silent_remove("{}/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table".format(
                os.path.expanduser("~")))
        else:
            util_silent_remove("{}/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table.db".format(
                os.path.expanduser("~")))

        clean_lookup_table_k_sku_v_boolean()
        clean_lookup_table_k_sku_v_brand_c1_c2_is_combined()
        clean_lookup_table_k_c1_v_c1_c2()
        clean_lookup_table_k_brand_v_brand_c2()
        clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name()

        response_object = {"status": "success"}
        return jsonify(response_object)
    else:
        response_object = {"status": "invalid input data"}
        return jsonify(response_object)
