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


# 删除单条商品条目的接口
@blueprint.route("/api/v1/products/one/clean", methods=["POST"])
@util_cost_count
def clean_one_product():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    specification_code = payload.get("specification_code", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DELETE FROM fotolei_pssa.products WHERE specification_code = '{}';".format(specification_code)
        db_connector.delete(stmt)
        response_object = {"status": "success"}
        return jsonify(response_object)
    else:
        response_object = {"status": "invalid input data"}
        return jsonify(response_object)
