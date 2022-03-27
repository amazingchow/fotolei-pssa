# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import Blueprint
from flask import jsonify
from flask import send_from_directory

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from .decorator_factory import cost_count
from db import db_connector
from utils import ROLE_TYPE_ORDINARY_USER


common_blueprint = Blueprint(
    name="fotolei_pssa_common_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/common",
)


# 探活接口
@common_blueprint.route("/keepalive", methods=["GET"])
@cost_count
def keepalive():
    return jsonify("alive")


# 下载文件接口
@common_blueprint.route("/download/<path:filename>", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def download(filename):
    return send_from_directory(directory="{}/fotolei-pssa/send_queue".format(os.path.expanduser("~")), path=filename)


# 获取最近20条操作日志的接口
@common_blueprint.route("/oplogs", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
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
