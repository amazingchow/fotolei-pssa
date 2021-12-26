# -*- coding: utf-8 -*-
import os
import sys
from flask import send_from_directory
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import cost_count


# 下载文件接口
@blueprint.route("/api/v1/download/<path:filename>", methods=["GET"])
@cost_count
def download(filename):
    return send_from_directory(directory="{}/ggfilm-server/send_queue".format(os.path.expanduser("~")), path=filename)
