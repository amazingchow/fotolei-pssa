# -*- coding: utf-8 -*-
import os
import platform
import sys
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import lookup_table_inventory_update_without_repetition
from utils import cost_count


# 删除所有库存条目的接口
@blueprint.route("/api/v1/inventories/all/clean", methods=["POST"])
@cost_count
def clean_all_inventories():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DROP TABLE IF EXISTS ggfilm.inventories;"
        db_connector.drop_table(stmt)
        stmt = "DROP TABLE IF EXISTS ggfilm.inventory_summary;"
        db_connector.drop_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS ggfilm.inventories (
    id                         INT        NOT NULL AUTO_INCREMENT,
    product_code               VARCHAR(64)   NOT NULL, /* 商品编码 */
    product_name               VARCHAR(128)  NOT NULL, /* 商品名称 */
    specification_code         VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name         VARCHAR(128),           /* 规格名称 */
    st_inventory_qty           INT,                    /* 起始库存数量 */
    st_inventory_total         INT,                    /* 起始库存总额 */
    purchase_qty               INT,                    /* 采购数量 */
    purchase_total             INT,                    /* 采购总额 */
    purchase_then_return_qty   INT,                    /* 采购退货数量 */
    purchase_then_return_total INT,                    /* 采购退货总额 */
    sale_qty                   INT,                    /* 销售数量 */
    sale_total                 INT,                    /* 销售总额 */
    sale_then_return_qty       INT,                    /* 销售退货数量 */
    sale_then_return_total     INT,                    /* 销售退货总额 */
    others_qty                 INT,                    /* 其他变更数量 */
    others_total               INT,                    /* 其他变更总额 */
    ed_inventory_qty           INT,                    /* 截止库存数量 */
    ed_inventory_total         INT,                    /* 截止库存总额 */
    create_time                VARCHAR(10),            /* 年月的格式 */
    extra_brand                VARCHAR(64),            /* 品牌 */
    extra_classification_1     VARCHAR(64),            /* 分类1 */
    extra_classification_2     VARCHAR(64),            /* 分类2 */
    PRIMARY KEY (id),
    KEY (specification_code, extra_brand, extra_classification_1, extra_classification_2)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS ggfilm.inventory_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        if platform.system() == "Linux":
            os.remove("./tmp/inventories_load_file_repetition_lookup_table")
            os.remove("./tmp/inventories_check_table")
        else:
            os.remove("./tmp/inventories_load_file_repetition_lookup_table.db")
            os.remove("./tmp/inventories_check_table.db")
        lookup_table_inventory_update_without_repetition.clear()
        response_object = {"status": "success"}
        return jsonify(response_object)
    else:
        response_object = {"status": "invalid input data"}
        return jsonify(response_object)
