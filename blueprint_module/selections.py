# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import cost_count


# 导出所有可供选择的品牌列表的接口
@blueprint.route("/api/v1/brands", methods=["GET"])
@cost_count
def list_all_brand_selections():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT brand FROM ggfilm.products;"
    brand_selections = db_connector.query(stmt)
    if len(brand_selections) == 0:
        response_object["brand_selections"] = []
    else:
        response_object["brand_selections"] = [
            {"value": brand[0], "text": brand[0]} \
                for brand in brand_selections \
                    if len(brand[0].strip()) > 0
        ]

    return jsonify(response_object)


# 导出所有可供选择的分类1的接口
@blueprint.route("/api/v1/classification1", methods=["GET"])
@cost_count
def list_all_classification_1_selections():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT classification_1 FROM ggfilm.products;"
    classification_1_selections = db_connector.query(stmt)
    if len(classification_1_selections) == 0:
        response_object["classification_1_selections"] = []
    else:
        response_object["classification_1_selections"] = [
            {"value": classification_1[0], "text": classification_1[0]} \
                for classification_1 in classification_1_selections \
                    if len(classification_1[0].strip()) > 0
        ]

    return jsonify(response_object)


# 导出所有可供选择的供应商列表的接口
@blueprint.route("/api/v1/suppliers", methods=["GET"])
@cost_count
def list_all_supplier_selections():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_selections = db_connector.query(stmt)
    if len(supplier_name_selections) == 0:
        response_object["supplier_name_selections"] = []
    else:
        response_object["supplier_name_selections"] = [
            {"value": supplier_name_selection[0], "text": supplier_name_selection[0]} \
                for supplier_name_selection in supplier_name_selections \
                    if len(supplier_name_selection[0].strip()) > 0
        ]

    return jsonify(response_object)