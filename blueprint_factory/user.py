# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import hashlib

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import make_response
from flask import request
from flask import session
from flask_api import status as StatusCode

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from db import db_connector
from utils import get_lookup_table_k_user_v_boolean
from utils import put_lookup_table_k_user_v_boolean
from utils import ROLE_TYPE_SUPER_ADMIN
from utils import util_cost_count
from utils import util_generate_n_digit_nums_and_letters


user_blueprint = Blueprint(
    name="fotolei_pssa_user_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/users",
)


# 注册用户的接口, 用户权限分为管理员和普通用户
# curl -s -v -b cookies.txt -d '{"username": "summychou", "password":"1234qwer"}' -H "Content-Type: application/json" -X POST http://localhost:15555/api/v1/users/register | jq
@user_blueprint.route("/register", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def register():
    payload = request.get_json()
    usr = payload.get("username", "")
    pwd = payload.get("password", "")
    if len(usr) < 4 or len(usr) > 32 or len(pwd) < 8:
        response_object = {"status": "invalid username or password"}
        return jsonify(response_object)
    if get_lookup_table_k_user_v_boolean(usr):
        response_object = {"status": "username has been registered"}
        return jsonify(response_object)
    role = payload.get("role", 2)
    salt = util_generate_n_digit_nums_and_letters(10)
    pwd_sha256 = hashlib.sha256("{}_{}".format(pwd, salt).encode('utf-8')).hexdigest()

    stmt = "INSERT INTO fotolei_pssa.users (username, password_sha256, salt, role_type) VALUES (%s, %s, %s, %s);"
    db_connector.insert(stmt, (usr, pwd_sha256, salt, role))

    put_lookup_table_k_user_v_boolean(usr, True)
    current_app.logger.info("注册用户 <{}>".format(usr))

    response_object = {"status": "success"}
    return jsonify(response_object)


# 注销用户的接口
# curl -s -v -b cookies.txt -X DELETE http://localhost:15555/api/v1/users/unregister?username=summychou | jq
@user_blueprint.route("/unregister", methods=["DELETE"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def unregister():
    usr = request.args.get("username")
    if len(usr) < 4 or len(usr) > 32:
        response_object = {"status": "invalid username"}
        return jsonify(response_object)
    if not get_lookup_table_k_user_v_boolean(usr):
        response_object = {"status": "username has not been registered"}
        return jsonify(response_object)

    stmt = "DELETE FROM fotolei_pssa.users WHERE username = '{}';".format(usr)
    db_connector.delete(stmt)

    put_lookup_table_k_user_v_boolean(usr, False)
    current_app.logger.info("注销用户 <{}>".format(usr))

    response_object = {"status": "success"}
    return jsonify(response_object)


# 获取所有注册用户的接口, 带有翻页功能
# curl -s -v -b cookies.txt http://localhost:15555/api/v1/users/ | jq
@user_blueprint.route("/", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def list_users():
    page_offset = request.args.get("page.offset", 0)
    page_limit = request.args.get("page.limit", 20)

    stmt = "SELECT username, role_type FROM fotolei_pssa.users LIMIT {}, {};".format(page_offset, page_limit)
    users = db_connector.query(stmt)

    response_object = {"message": "success"}
    if (type(users) is not list) or (type(users) is list and len(users) == 0):
        response_object["message"] = "not found"
        response_object["users"] = []
    else:
        response_object["users"] = [{"username": user[0], "role": user[1]} for user in users]
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 用户登录的接口
# curl -s -v -c cookies.txt -d '{"username": "fotolei", "password":"asdf5678"}' -H "Content-Type: application/json" -X POST http://localhost:15555/api/v1/users/login | jq
@user_blueprint.route("/login", methods=["POST"])
@util_cost_count
def login():
    is_logged_in = session.get("is_logged_in", False)
    if is_logged_in:
        return make_response(
            jsonify({"message": "logged in"}),
            StatusCode.HTTP_200_OK,
            {"Set-Role": "role={}".format(session["role"]), "Set-Logged": "logged=in"}
        )

    payload = request.get_json()
    usr = payload.get("username", "")
    pwd = payload.get("password", "")
    if len(usr) < 4 or len(usr) > 32 or len(pwd) < 8:
        return make_response(
            jsonify({"message": "invalid input username or input password"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )
    if not get_lookup_table_k_user_v_boolean(usr):
        return make_response(
            jsonify({"message": "username has not been registered"}),
            StatusCode.HTTP_404_NOT_FOUND
        )

    stmt = "SELECT password_sha256, salt, role_type FROM fotolei_pssa.users WHERE username = '{}';".format(usr)
    users = db_connector.query(stmt)
    if (type(users) is not list) or (type(users) is list and len(users) == 0):
        return make_response(
            jsonify({"message": "username has not been registered"}),
            StatusCode.HTTP_404_NOT_FOUND
        )
    user = users[0]

    pwd_sha256 = hashlib.sha256("{}_{}".format(pwd, user[1]).encode('utf-8')).hexdigest()
    if pwd_sha256 != user[0]:
        return make_response(
            jsonify({"message": "invalid password"}),
            StatusCode.HTTP_401_UNAUTHORIZED
        )

    session["is_logged_in"] = True
    session["role"] = user[2]
    current_app.logger.info("用户 <usr: {}> 已登录".format(usr))

    return make_response(
        jsonify({"message": "logged in"}),
        StatusCode.HTTP_200_OK,
        {"Set-Role": "role={}".format(session["role"]), "Set-Logged": "logged=in"}
    )


# 用户登出的接口
# curl -s -v -b cookies.txt -X DELETE http://localhost:15555/api/v1/users/logout | jq
@user_blueprint.route("/logout", methods=["DELETE"])
@util_cost_count
def logout():
    is_logged_in = session.get("is_logged_in", False)
    if is_logged_in:
        session["is_logged_in"] = False
        current_app.logger.info("用户 <sid: {}> 已登出".format(session.sid))

    return make_response(
        jsonify({"message": "logged out"}),
        StatusCode.HTTP_200_OK,
        {"Set-Logged": "logged=out"}
    )
