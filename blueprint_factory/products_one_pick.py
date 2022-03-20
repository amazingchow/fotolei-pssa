# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import jsonify
from flask import request

from . import blueprint
from db import db_connector
from utils import get_lookup_table_k_sku_v_boolean
from utils import util_cost_count


# 获取一条商品条目的接口
@blueprint.route("/api/v1/products/one/pick", methods=["GET"])
@util_cost_count
def pick_one_product():
    specification_code = request.args.get("specification_code")
    if not get_lookup_table_k_sku_v_boolean(specification_code):
        response_object = {"status": "not found"}
        return response_object

    stmt = "SELECT * FROM fotolei_pssa.products WHERE specification_code = '{}';".format(specification_code)
    products = db_connector.query(stmt)

    response_object = {"status": "success"}
    if len(products) == 0:
        response_object["status"] = "not found"
    else:
        response_object["product"] = {
            "id": products[0][0],
            "product_code": products[0][1],
            "product_name": products[0][2],
            "specification_name": products[0][4],
            "brand": products[0][5],
            "classification_1": products[0][6],
            "classification_2": products[0][7],
            "product_series": products[0][8],
            "stop_status": products[0][9],
            "product_weight": "{}".format(products[0][10]),
            "product_length": "{}".format(products[0][11]),
            "product_width": "{}".format(products[0][12]),
            "product_height": "{}".format(products[0][13]),
            "is_combined": products[0][14],
            "be_aggregated": products[0][15],
            "is_import": products[0][16],
            "supplier_name": products[0][17],
            "purchase_name": products[0][18],
            "jit_inventory": "{}".format(products[0][19]),
            "moq": "{}".format(products[0][20]),
        }
    return jsonify(response_object)
