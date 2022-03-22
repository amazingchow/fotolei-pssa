# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import jsonify
from flask import request

from . import blueprint
from db import db_connector
from utils import util_cost_count


# 更新一条商品条目的接口
@blueprint.route("/api/v1/products/one/update", methods=["POST"])
@util_cost_count
def update_one_product():
    payload = request.get_json()
    id = payload["id"]

    specification_code = payload.get("specification_code", "").strip()
    product_code = payload.get("product_code", "").strip()
    product_name = payload.get("product_name", "").strip()
    specification_name = payload.get("specification_name", "").strip()
    brand = payload.get("brand", "").strip()
    classification_1 = payload.get("classification_1", "").strip()
    classification_2 = payload.get("classification_2", "").strip()
    product_series = payload.get("product_series", "").strip()
    stop_status = payload.get("stop_status", "全部").strip()
    product_weight = payload.get("product_weight", "")
    product_length = payload.get("product_length", "")
    product_width = payload.get("product_width", "")
    product_height = payload.get("product_height", "")
    is_combined = payload.get("is_combined", "全部").strip()
    be_aggregated = payload.get("be_aggregated", "全部").strip()
    is_import = payload.get("is_import", "全部").strip()
    supplier_name = payload.get("supplier_name", "").strip()
    purchase_name = payload.get("purchase_name", "").strip()
    jit_inventory = payload.get("jit_inventory", "")
    moq = payload.get("moq", "")

    stmt = "UPDATE fotolei_pssa.products SET "
    updates = []
    if len(specification_code) > 0:
        updates.append("specification_code = '{}'".format(specification_code))
    if len(product_code) > 0:
        updates.append("product_code = '{}'".format(product_code))
    if len(product_name) > 0:
        updates.append("product_name = '{}'".format(product_name))
    if len(specification_name) > 0:
        updates.append("specification_name = '{}'".format(specification_name))
    if len(brand) > 0:
        updates.append("brand = '{}'".format(brand))
    if len(classification_1) > 0:
        updates.append("classification_1 = '{}'".format(classification_1))
    if len(classification_2) > 0:
        updates.append("classification_2 = '{}'".format(classification_2))
    if len(product_series) > 0:
        updates.append("product_series = '{}'".format(product_series))
    if stop_status != '全部':
        updates.append("stop_status = '{}'".format(stop_status))
    if len(product_weight) > 0:
        updates.append("product_weight = '{}'".format(product_weight))
    if len(product_length) > 0:
        updates.append("product_length = '{}'".format(product_length))
    if len(product_width) > 0:
        updates.append("product_width = '{}'".format(product_width))
    if len(product_height) > 0:
        updates.append("product_height = '{}'".format(product_height))
    if is_combined != '全部':
        updates.append("is_combined = '{}'".format(is_combined))
    if be_aggregated != '全部':
        updates.append("be_aggregated = '{}'".format(be_aggregated))
    if is_import != '全部':
        updates.append("is_import = '{}'".format(is_import))
    if len(supplier_name) > 0:
        updates.append("supplier_name = '{}'".format(supplier_name))
    if len(purchase_name) > 0:
        updates.append("purchase_name = '{}'".format(purchase_name))
    if len(jit_inventory) > 0:
        updates.append("jit_inventory = '{}'".format(jit_inventory))
    if len(moq) > 0:
        updates.append("moq = '{}'".format(moq))
    stmt += ", ".join(updates)
    stmt += " WHERE id = '{}';".format(id)
    db_connector.update(stmt)

    response_object = {"status": "success"}
    return jsonify(response_object)
