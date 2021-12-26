# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import cost_count


# 获取所有商品条目的接口, 带有翻页功能
@blueprint.route("/api/v1/products", methods=["GET"])
@cost_count
def list_products():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT product_code, specification_code, product_name, specification_name, \
brand, classification_1, classification_2, product_series, stop_status, \
is_combined, is_import, supplier_name, purchase_name, jit_inventory, moq \
FROM ggfilm.products ORDER BY specification_code LIMIT {}, {};".format(
        page_offset, page_limit)
    products = db_connector.query(stmt)

    response_object = {"status": "success"}
    if len(products) == 0:
        response_object["status"] = "not found"
        response_object["products"] = []
    else:
        response_object["products"] = products
    return jsonify(response_object)
