# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import Blueprint
from flask import jsonify

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from .decorator_factory import cost_count
from db import db_connector
from utils import ROLE_TYPE_ORDINARY_USER


selection_blueprint = Blueprint(
    name="fotolei_pssa_selection_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/selections",
)


# 导出所有可供选择的品牌列表的接口
@selection_blueprint.route("/brands", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def list_all_brand_selections():
    response_object = {"status": "success"}

    # TODO: 优化SQL
    stmt = "SELECT DISTINCT brand FROM fotolei_pssa.products;"
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
@selection_blueprint.route("/classification1", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def list_all_classification_1_selections():
    response_object = {"status": "success"}

    # TODO: 优化SQL
    stmt = "SELECT DISTINCT classification_1 FROM fotolei_pssa.products;"
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
@selection_blueprint.route("/suppliers", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def list_all_supplier_selections():
    response_object = {"status": "success"}

    # TODO: 优化SQL
    stmt = "SELECT DISTINCT supplier_name FROM fotolei_pssa.products;"
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
