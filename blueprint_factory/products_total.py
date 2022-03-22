# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import jsonify

from . import blueprint
from db import db_connector
from utils import util_cost_count


# 获取总商品条目量的接口
@blueprint.route("/api/v1/products/total", methods=["GET"])
@util_cost_count
def get_products_total():
    stmt = "SELECT SUM(total) FROM fotolei_pssa.product_summary;"
    ret = db_connector.query(stmt)
    response_object = {"status": "success"}
    if type(ret) is list and len(ret) > 0 and ret[0][0] is not None:
        response_object["products_total"] = ret[0][0]
    else:
        response_object["products_total"] = 0
    return jsonify(response_object)
