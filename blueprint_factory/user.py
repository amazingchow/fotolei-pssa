# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import hashlib

from flask import Blueprint
from flask import jsonify
from flask import request

from db import db_connector
from utils import util_cost_count
from utils import util_generate_n_digit_nums_and_letters


user_blueprint = Blueprint(
    name="fotolei_pssa_user_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/users",
)


# 注册用户的接口, 用户权限分为管理员和普通用户
@user_blueprint.route("/register", methods=["POST"])
@util_cost_count
def register():
    payload = request.get_json()
    usr = payload.get("username", "")
    pwd = payload.get("password", "")
    if len(usr) < 4 or len(usr) > 32 or len(pwd) < 8:
        response_object = {"status": "invalid username or password"}
        return jsonify(response_object)
    role = payload.get("role", "ordinary")
    salt = util_generate_n_digit_nums_and_letters(10)
    pwd_sha256 = hashlib.sha256("{}_{}".format(pwd, salt).encode('utf-8')).hexdigest()
    stmt = "INSERT INTO fotolei_pssa.users (username, password_sha256, salt, role_type) VALUES (%s, %s, %s, %s);"
    db_connector.insert(stmt, (usr, pwd_sha256, salt, role))
    response_object = {"status": "success"}
    return jsonify(response_object)


# 注销用户的接口
@user_blueprint.route("/unregister", methods=["DELETE"])
@util_cost_count
def unregister():
    usr = request.args.get("username")
    if len(usr) < 4 or len(usr) > 32:
        response_object = {"status": "invalid username"}
        return jsonify(response_object)
    stmt = "DELETE FROM fotolei_pssa.users WHERE username = '{}';".format(usr)
    db_connector.delete(stmt)
    response_object = {"status": "success"}
    return jsonify(response_object)


# 获取所有注册用户的接口, 带有翻页功能
@user_blueprint.route("/", methods=["GET"])
@util_cost_count
def list_users():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT username, role_type FROM fotolei_pssa.users LIMIT {}, {};".format(
        page_offset, page_limit)
    users = db_connector.query(stmt)

    response_object = {"status": "success"}
    if (type(users) is not list) or (type(users) is list and len(users) == 0):
        response_object["status"] = "not found"
        response_object["users"] = []
    else:
        response_object["users"] = users
    return jsonify(response_object)
