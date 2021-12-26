# -*- coding: utf-8 -*-
import os
import platform
import sys
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import lookup_table_sku_get_or_put
from utils import cost_count


# 删除所有商品条目的接口
@blueprint.route("/api/v1/products/all/clean", methods=["POST"])
@cost_count
def clean_all_products():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DROP TABLE IF EXISTS ggfilm.products;"
        db_connector.drop_table(stmt)
        stmt = "DROP TABLE IF EXISTS ggfilm.product_summary;"
        db_connector.drop_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS ggfilm.products (
    id                 INT          NOT NULL AUTO_INCREMENT,
    product_code       VARCHAR(64)  NOT NULL, /* 商品编码 */
    product_name       VARCHAR(128) NOT NULL, /* 商品名称 */
    specification_code VARCHAR(64)  NOT NULL, /* 规格编码 */
    specification_name VARCHAR(128),          /* 规格名称 */
    brand              VARCHAR(64),           /* 品牌 */
    classification_1   VARCHAR(64),           /* 分类1 */
    classification_2   VARCHAR(64),           /* 分类2 */
    product_series     VARCHAR(64),           /* 产品系列 */
    stop_status        VARCHAR(32),           /* STOP状态 */
    product_weight     INT,                   /* 重量/g */
    product_length     INT,                   /* 长度/cm */
    product_width      INT,                   /* 宽度/cm */
    product_height     INT,                   /* 高度/cm */
    is_combined        VARCHAR(32) ,          /* 是否是组合商品 */
    be_aggregated      VARCHAR(32) ,          /* 是否参与统计 */
    is_import          VARCHAR(32) ,          /* 是否是进口商品 */
    supplier_name      VARCHAR(128),          /* 供应商名称 */
    purchase_name      VARCHAR(128),          /* 采购名称 */
    jit_inventory      INT,                   /* 实时可用库存 */
    moq                INT,                   /* 最小订货单元 */
    PRIMARY KEY (id),
    KEY (product_code, specification_code)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS ggfilm.product_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        if platform.system() == "Linux":
            os.remove("./tmp/products_load_file_repetition_lookup_table")
        else:
            os.remove("./tmp/products_load_file_repetition_lookup_table.db")
        lookup_table_sku_get_or_put.clear()
        response_object = {"status": "success"}
        return jsonify(response_object)
    else:
        response_object = {"status": "invalid input data"}
        return jsonify(response_object)
