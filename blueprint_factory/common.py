# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import Blueprint
from flask import jsonify
from flask import send_from_directory

from db import db_connector
from utils import util_cost_count


common_blueprint = Blueprint(
    name="fotolei_pssa_common_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/common",
)


# 探活接口
@common_blueprint.route("/keepalive", methods=["GET"])
@util_cost_count
def keepalive():
    return jsonify("alive")


# 下载文件接口
@common_blueprint.route("/download/<path:filename>", methods=["GET"])
@util_cost_count
def download(filename):
    return send_from_directory(directory="{}/fotolei-pssa/send_queue".format(os.path.expanduser("~")), path=filename)


# 获取最近20条操作日志的接口
@common_blueprint.route("/oplogs", methods=["GET"])
@util_cost_count
def get_oplogs():
    stmt = "SELECT oplog, DATE_FORMAT(create_time, '%Y-%m-%d %H-%i-%s') FROM fotolei_pssa.operation_logs ORDER BY create_time DESC LIMIT 20;"
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
