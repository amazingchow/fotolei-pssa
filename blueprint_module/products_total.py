# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import cost_count


# 获取总商品条目量的接口
@blueprint.route("/api/v1/products/total", methods=["GET"])
@cost_count
def get_products_total():
    stmt = "SELECT SUM(total) FROM ggfilm.product_summary;"
    ret = db_connector.query(stmt)
    response_object = {"status": "success"}
    if type(ret) is list and len(ret) > 0 and ret[0][0] is not None:
        response_object["products_total"] = ret[0][0]
    else:
        response_object["products_total"] = 0
    return jsonify(response_object)
