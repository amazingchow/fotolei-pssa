# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import logging
import logging.handlers
_rotate_file_handler = logging.handlers.WatchedFileHandler(
    filename="{}/fotolei-pssa/logs/fotolei-pssa-profile.log".format(os.path.expanduser("~")),
    mode="a"
)
_rotate_file_handler_formatter = logging.Formatter(
    "[%(asctime)-15s][%(levelname)-5s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
_rotate_file_handler.setFormatter(_rotate_file_handler_formatter)
_profile_logger = logging.getLogger("FotoleiPssA_Profile")
_profile_logger.setLevel(logging.INFO)
_profile_logger.addHandler(_rotate_file_handler)
import time

from functools import wraps

from flask import jsonify
from flask import make_response
from flask import Response
from flask import session
from flask_api import status as StatusCode

from db import db_connector
from utils import ACTION_TYPE_DELETE_ALL
from utils import ACTION_TYPE_DELETE_ONE
from utils import ACTION_TYPE_EXPORT
from utils import ACTION_TYPE_IMPORT
from utils import ACTION_TYPE_REGISTER
from utils import ACTION_TYPE_UPDATE_ONE
from utils import ACTION_TYPE_UNREGISTER
from utils import ROLE_TYPE_SUPER_ADMIN


def has_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        is_logged_in = session.get("is_logged_in", False)
        if not is_logged_in:
            return make_response(
                jsonify({"message": "redirect to login page"}),
                StatusCode.HTTP_401_UNAUTHORIZED
            )
        return func(*args, **kwargs)
    return wrapper


def restrict_access(access_level: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = session.get("role", ROLE_TYPE_SUPER_ADMIN)
            if role > access_level:
                return make_response(
                    jsonify({"message": "you do not have permission to access the resource"}),
                    StatusCode.HTTP_403_FORBIDDEN
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cost_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        t = func(*args, **kwargs)
        _profile_logger.info("%s took time: %f secs", func.__name__, time.time() - start)
        return t
    return wrapper


def record_action(action: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            t = func(*args, **kwargs)
            resp = Response(t)
            if resp.status_code == StatusCode.HTTP_200_OK:
                action_zh = ""
                if action == ACTION_TYPE_IMPORT:
                    action_zh = "导入"
                elif action == ACTION_TYPE_EXPORT:
                    action_zh = "导出"
                elif action == ACTION_TYPE_UPDATE_ONE:
                    action_zh = "更新单条"
                elif action == ACTION_TYPE_DELETE_ALL:
                    action_zh = "删除所有"
                elif action == ACTION_TYPE_DELETE_ONE:
                    action_zh = "删除单条"
                elif action == ACTION_TYPE_REGISTER:
                    action_zh = "注册用户"
                elif action == ACTION_TYPE_UNREGISTER:
                    action_zh = "注销用户"
                stmt = "INSERT INTO fotolei_pssa.operation_logs (oplog) VALUES (%s);"
                db_connector.insert(stmt, ("{}{}{}".format(
                    session.get("username", "anonymous"), action_zh, session.get("op_object", "")),))
            return t
        return wrapper
    return decorator
