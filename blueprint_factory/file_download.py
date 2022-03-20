# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../utils"))

from flask import send_from_directory

from . import blueprint
from utils import util_cost_count


# 下载文件接口
@blueprint.route("/api/v1/download/<path:filename>", methods=["GET"])
@util_cost_count
def download(filename):
    return send_from_directory(directory="{}/fotolei-pssa/send_queue".format(os.path.expanduser("~")), path=filename)
