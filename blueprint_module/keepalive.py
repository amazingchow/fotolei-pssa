# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import cost_count


# 探活接口
@blueprint.route("/api/v1/keepalive", methods=["GET"])
@cost_count
def keepalive():
    return jsonify("alive")
