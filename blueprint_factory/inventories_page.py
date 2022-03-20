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


# 获取所有库存条目的接口, 带有翻页功能
@blueprint.route("/api/v1/inventories", methods=["GET"])
@util_cost_count
def list_inventories():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    # TODO: 优化SQL
    stmt = "SELECT specification_code, \
st_inventory_qty, purchase_qty, purchase_then_return_qty, sale_qty, \
sale_then_return_qty, others_qty, ed_inventory_qty, create_time \
FROM fotolei_pssa.inventories ORDER BY create_time DESC LIMIT {}, {};".format(
        page_offset, page_limit)
    inventories = db_connector.query(stmt)

    response_object = {"status": "success"}
    if len(inventories) == 0:
        response_object = {"status": "not found"}
        response_object["inventories"] = []
    else:
        response_object["inventories"] = inventories
    return jsonify(response_object)
