# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../utils"))

import csv
import time

from flask import jsonify
from flask import request

from . import blueprint
from utils import util_cost_count
from utils import util_generate_digest


# 预下载"新增SKU数据表"的接口
@blueprint.route("/api/v1/addedskus/prepare", methods=["POST"])
@util_cost_count
def prepare_added_skus():
    payload = request.get_json()
    added_skus = payload.get("added_skus", [])

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("新增SKU_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "新增SKU_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow(["新增SKU"])
        for sku in added_skus:
            csv_writer.writerow([sku])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256

    return jsonify(response_object)
