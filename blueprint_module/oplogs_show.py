# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import cost_count


# 获取最近20条操作日志的接口
@blueprint.route("/api/v1/oplogs", methods=["GET"])
@cost_count
def get_oplogs():
    stmt = "SELECT oplog, DATE_FORMAT(create_time, '%Y-%m-%d %H-%i-%s') FROM ggfilm.operation_logs ORDER BY create_time DESC LIMIT 20;"
    rets = db_connector.query(stmt)
    response_object = {"status": "success"}
    response_object["oplogs"] = []
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            cache = {}
            cache["oplog"] = ret[0]
            cache["create_time"] = ret[1]
            response_object["oplogs"].append(cache)
    return jsonify(response_object)
