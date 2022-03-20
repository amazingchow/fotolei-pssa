# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import jsonify

from . import blueprint
from utils import util_cost_count


# 探活接口
@blueprint.route("/api/v1/keepalive", methods=["GET"])
@util_cost_count
def keepalive():
    return jsonify("alive")
