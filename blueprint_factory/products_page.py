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


# 获取所有商品条目的接口, 带有翻页功能
@blueprint.route("/api/v1/products", methods=["GET"])
@util_cost_count
def list_products():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    # TODO: 优化SQL
    stmt = "SELECT product_code, specification_code, product_name, specification_name, \
brand, classification_1, classification_2, product_series, stop_status, \
is_combined, is_import, supplier_name, purchase_name, jit_inventory, moq \
FROM fotolei_pssa.products ORDER BY specification_code LIMIT {}, {};".format(
        page_offset, page_limit)
    products = db_connector.query(stmt)

    response_object = {"status": "success"}
    if len(products) == 0:
        response_object["status"] = "not found"
        response_object["products"] = []
    else:
        response_object["products"] = products
    return jsonify(response_object)
