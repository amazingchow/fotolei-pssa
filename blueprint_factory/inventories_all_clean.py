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
from utils import clean_lookup_table_k_ct_sku_v_boolean
from utils import util_cost_count
from utils import util_silent_remove


# 删除所有库存条目的接口
@blueprint.route("/api/v1/inventories/all/clean", methods=["POST"])
@util_cost_count
def clean_all_inventories():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.inventories;"
        db_connector.drop_table(stmt)
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.inventory_summary;"
        db_connector.drop_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.inventories (
    id                         INT           NOT NULL AUTO_INCREMENT,
    product_code               VARCHAR(64),            /* 商品编码 */
    product_name               VARCHAR(128),           /* 商品名称 */
    specification_code         VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name         VARCHAR(128),           /* 规格名称 */
    st_inventory_qty           INT,                    /* 起始库存数量 */
    st_inventory_total         FLOAT,                  /* 起始库存总额 */
    purchase_qty               INT,                    /* 采购数量 */
    purchase_total             FLOAT,                  /* 采购总额 */
    purchase_then_return_qty   INT,                    /* 采购退货数量 */
    purchase_then_return_total FLOAT,                  /* 采购退货总额 */
    sale_qty                   INT,                    /* 销售数量 */
    sale_total                 FLOAT,                  /* 销售总额 */
    sale_then_return_qty       INT,                    /* 销售退货数量 */
    sale_then_return_total     FLOAT,                  /* 销售退货总额 */
    others_qty                 INT,                    /* 其他变更数量 */
    others_total               FLOAT,                  /* 其他变更总额 */
    ed_inventory_qty           INT,                    /* 截止库存数量 */
    ed_inventory_total         FLOAT,                  /* 截止库存总额 */
    create_time                VARCHAR(10),            /* 年月的格式 */
    extra_brand                VARCHAR(64),            /* 品牌 */
    extra_classification_1     VARCHAR(64),            /* 分类1 */
    extra_classification_2     VARCHAR(64),            /* 分类2 */
    extra_is_combined          VARCHAR(32),            /* 是否是组合商品 */
    anchor                     TINYINT,                /* 锚，防止‘组合商品‘读出来带空格 */
    PRIMARY KEY (id),
    KEY inventories_ct (create_time),
    KEY inventories_specification_code_ct (specification_code, create_time),
    KEY inventories_extra_is_combined_ct (extra_is_combined, create_time),
    KEY inventories_extra_is_combined_extra_brand_ct (extra_is_combined, extra_brand, create_time),
    KEY inventories_extra_is_combined_extra_c1_ct (extra_is_combined, extra_classification_1, create_time),
    KEY inventories_extra_is_combined_extra_c2_ct (extra_is_combined, extra_classification_2, create_time)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.inventory_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        if platform.system() == "Linux":
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_check_table".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table".format(
                os.path.expanduser("~")))
        else:
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table.db".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_check_table.db".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table.db".format(
                os.path.expanduser("~")))
        clean_lookup_table_k_ct_sku_v_boolean()
        response_object = {"status": "success"}
        return jsonify(response_object)
    else:
        response_object = {"status": "invalid input data"}
        return jsonify(response_object)
