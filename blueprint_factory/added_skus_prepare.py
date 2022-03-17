# -*- coding: utf-8 -*-
import csv
import os
import sys
import time
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import cost_count
from utils import generate_digest


# 预下载"新增SKU数据表"的接口
@blueprint.route("/api/v1/addedskus/prepare", methods=["POST"])
@cost_count
def prepare_added_skus():
    payload = request.get_json()
    added_skus = payload.get("added_skus", [])

    ts = int(time.time())
    csv_file_sha256 = generate_digest("新增SKU_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
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
