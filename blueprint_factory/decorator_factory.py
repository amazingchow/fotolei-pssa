# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../utils"))

from functools import wraps

from flask import jsonify
from flask import make_response
from flask import session
from flask_api import status as StatusCode

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
