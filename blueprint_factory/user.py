# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import hashlib

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import Response
from flask import session
from flask_api import status as StatusCode

from db import db_connector
from utils import get_lookup_table_k_user_v_boolean
from utils import put_lookup_table_k_user_v_boolean
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
@util_cost_count
def register():
    is_logged_in = session.get("is_logged_in", False)
    if not is_logged_in:
        response_object = {"status": "redirect to login page"}
        return jsonify(response_object)

    payload = request.get_json()
    usr = payload.get("username", "")
    pwd = payload.get("password", "")
    if len(usr) < 4 or len(usr) > 32 or len(pwd) < 8:
        response_object = {"status": "invalid username or password"}
        return jsonify(response_object)
    if get_lookup_table_k_user_v_boolean(usr):
        response_object = {"status": "username has been registered"}
        return jsonify(response_object)
    role = payload.get("role", "ordinary")
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
@util_cost_count
def unregister():
    is_logged_in = session.get("is_logged_in", False)
    if not is_logged_in:
        response_object = {"status": "redirect to login page"}
        return jsonify(response_object)

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
@util_cost_count
def list_users():
    is_logged_in = session.get("is_logged_in", False)
    if not is_logged_in:
        response_object = {"status": "redirect to login page"}
        return jsonify(response_object)

    page_offset = request.args.get("page.offset", 0)
    page_limit = request.args.get("page.limit", 20)

    stmt = "SELECT username, role_type FROM fotolei_pssa.users LIMIT {}, {};".format(page_offset, page_limit)
    users = db_connector.query(stmt)

    response_object = {"status": "success"}
    if (type(users) is not list) or (type(users) is list and len(users) == 0):
        response_object["status"] = "not found"
        response_object["users"] = []
    else:
        response_object["users"] = users
    return jsonify(response_object)


# 用户登录的接口
# curl -s -v -c cookies.txt -d '{"username": "summychou", "password":"1234qwer"}' -H "Content-Type: application/json" -X POST http://localhost:15555/api/v1/users/login | jq
@user_blueprint.route("/login", methods=["POST"])
@util_cost_count
def login():
    is_logged_in = session.get("is_logged_in", False)
    if is_logged_in:
        return Response(
            "logged in",
            status=StatusCode.HTTP_200_OK,
        )

    payload = request.get_json()
    usr = payload.get("username", "")
    pwd = payload.get("password", "")
    if len(usr) < 4 or len(usr) > 32 or len(pwd) < 8:
        return Response(
            "invalid input username or input password",
            status=StatusCode.HTTP_400_BAD_REQUEST,
        )
    if not get_lookup_table_k_user_v_boolean(usr):
        return Response(
            "username has not been registered",
            status=StatusCode.HTTP_404_NOT_FOUND,
        )

    stmt = "SELECT password_sha256, salt, role_type FROM fotolei_pssa.users WHERE username = '{}';".format(usr)
    users = db_connector.query(stmt)
    if (type(users) is not list) or (type(users) is list and len(users) == 0):
        return Response(
            "username has not been registered",
            status=StatusCode.HTTP_404_NOT_FOUND,
        )
    user = users[0]

    pwd_sha256 = hashlib.sha256("{}_{}".format(pwd, user[1]).encode('utf-8')).hexdigest()
    if pwd_sha256 != user[0]:
        return Response(
            "invalid password",
            status=StatusCode.HTTP_401_UNAUTHORIZED,
        )

    session["is_logged_in"] = True
    session["role"] = user[2]
    current_app.logger.info("用户 <usr: {}> 已登录".format(usr))

    return Response(
        "logged in",
        status=StatusCode.HTTP_200_OK,
    )


# 用户登出的接口
# curl -s -v -b cookies.txt -X DELETE http://localhost:15555/api/v1/users/logout | jq
@user_blueprint.route("/logout", methods=["DELETE"])
@util_cost_count
def logout():
    is_logged_in = session.get("is_logged_in", False)
    if is_logged_in:
        session["is_logged_in"] = False
        current_app.logger.info("用户 <sid: {}> 登出".format(session.sid))
    response_object = {"status": "success"}
    return jsonify(response_object)
