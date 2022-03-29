# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import time

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask import session
from flask_api import status as StatusCode

from .decorator_factory import cost_count
from .decorator_factory import has_logged_in
from .decorator_factory import record_action
from .decorator_factory import restrict_access
from db import db_connector
from utils import ACTION_TYPE_EXPORT
from utils import get_lookup_table_k_sku_v_boolean
from utils import REG_POSITIVE_INT
from utils import ROLE_TYPE_ORDINARY_USER
from utils import util_generate_digest


case6_blueprint = Blueprint(
    name="fotolei_pssa_case6_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/case6",
)


# 载入用于计算体积、重量的需求表的接口
@case6_blueprint.route("/upload", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def upload_csv_file_for_case6():
    csv_files = request.files.getlist("file")
    csv_file_sha256 = util_generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/fotolei-pssa/recv_queue/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_case6_demand_table(csv_file):
        return make_response(
            jsonify({"message": "非法的输入数据格式，请人工复查！"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    is_valid, err_msg = do_data_check_for_input_case6_demand_table(csv_file)
    if not is_valid:
        return make_response(
            jsonify({"message": err_msg}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    demand_table = []
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        for row in csv_reader:
            demand_table.append(
                {
                    "specification_code": row[0].strip(),
                    "quantity": row[1].strip()
                }
            )

    response_object = {"message": "", "demand_table": demand_table}
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


'''
预览效果

规格编码 | 商品名称 | 规格名称 | 数量 | 长度/cm | 宽度/cm | 高度/cm | 体积合计/m³ | 重量/g | 重量合计/kg
'''


# 预览"体积、重量计算汇总单"的接口
@case6_blueprint.route("/preview", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def preview_report_file_case6():
    payload = request.get_json()
    demand_table = payload.get("demand_table", [])

    preview_table = []
    for item in demand_table:
        stmt = "SELECT product_name, specification_name, \
product_weight, product_length, product_width, product_height \
FROM fotolei_pssa.products WHERE specification_code = '{}';".format(item["specification_code"])
        rets = db_connector.query(stmt)
        cache = {}
        cache["specification_code"] = item["specification_code"]
        cache["quantity"] = int(item["quantity"])
        if type(rets) is list and len(rets) > 0:
            cache["product_name"] = rets[0][0]
            cache["specification_name"] = rets[0][1]
            cache["product_length"] = rets[0][3]
            cache["product_width"] = rets[0][4]
            cache["product_height"] = rets[0][5]
            cache["product_volume_total"] = float("{:.3f}".format(((rets[0][3] * rets[0][4] * rets[0][5] * int(item["quantity"])) / 1e6)))
            cache["product_weight"] = rets[0][2]
            cache["product_weight_total"] = float("{:.3f}".format(((rets[0][2] * int(item["quantity"])) / 1e3)))
        else:
            cache["product_name"] = ""
            cache["specification_name"] = ""
            cache["product_length"] = 0
            cache["product_width"] = 0
            cache["product_height"] = 0
            cache["product_volume_total"] = 0
            cache["product_weight"] = 0
            cache["product_weight_total"] = 0
        preview_table.append(cache)
    preview_summary_table = {
        "quantity": 0,
        "product_volume_total": 0,
        "product_weight_total": 0
    }
    for item in preview_table:
        preview_summary_table["quantity"] += item["quantity"]
        preview_summary_table["product_volume_total"] += item["product_volume_total"]
        preview_summary_table["product_weight_total"] += item["product_weight_total"]

    response_object = {"message": ""}
    response_object["preview_table"] = preview_table
    response_object["preview_summary_table"] = preview_summary_table
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 预下载"体积、重量计算汇总单"的接口
@case6_blueprint.route("/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_EXPORT)
@cost_count
def prepare_report_file_case6():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])
    preview_summary_table = payload.get("preview_summary_table", {})

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("体积、重量计算汇总单_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "体积、重量计算汇总单_{}.csv".format(ts)
    with open(csv_file, "w", encoding="utf-8-sig") as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "规格编码", "商品名称", "规格名称", "数量",
            "长度/cm", "宽度/cm", "高度/cm", "体积合计/m³", "重量/g", "重量合计/kg",
        ])
        for item in preview_table:
            csv_writer.writerow([
                item["specification_code"], item["product_name"], item["specification_name"], item["quantity"],
                item["product_length"], item["product_width"], item["product_height"],
                item["product_volume_total"], item["product_weight"], item["product_weight_total"],
            ])
        csv_writer.writerow([
            "", "", "", preview_summary_table["quantity"],
            "", "", "",
            preview_summary_table["product_volume_total"], "", preview_summary_table["product_weight_total"],
        ])

    session["op_object"] = output_file

    response_object = {"message": ""}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


def do_data_schema_validation_for_input_case6_demand_table(csv_file: str):
    data_schema = [
        "规格编码", "数量",
    ]
    is_valid = True
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        for row in csv_reader:
            if len(row) != len(data_schema):
                is_valid = False
                break
            for idx, item in enumerate(row):
                if item.strip() != data_schema[idx]:
                    is_valid = False
                    break
            break
    if not is_valid:
        os.remove(csv_file)
    return is_valid


def do_data_check_for_input_case6_demand_table(csv_file: str):
    is_valid = True
    err_msg = ""
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        line = 1
        for row in csv_reader:
            if REG_POSITIVE_INT.match(row[1]) is None:
                is_valid = False
                err_msg = "'数量'数据存在非法输入，出现在第{}行。".format(line)
                break
            if not get_lookup_table_k_sku_v_boolean(row[0]):
                is_valid = False
                err_msg = "'规格编码'不存在系统内，出现在第{}行。".format(line)
                break
            line += 1
    if not is_valid:
        os.remove(csv_file)
    return is_valid, err_msg
