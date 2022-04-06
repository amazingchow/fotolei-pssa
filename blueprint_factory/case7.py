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
from utils import REG_POSITIVE_FLOAT
from utils import REG_POSITIVE_INT
from utils import ROLE_TYPE_ORDINARY_USER
from utils import util_generate_digest


case7_blueprint = Blueprint(
    name="fotolei_pssa_case7_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/case7",
)


# 载入用于计算运费的需求表的接口
@case7_blueprint.route("/upload", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def upload_csv_file_for_case7():
    csv_files = request.files.getlist("file")
    if len(csv_files) != 1:
        return make_response(
            jsonify({"message": "上传的文件数量不等于一份"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    csv_file_sha256 = util_generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/fotolei-pssa/recv_queue/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_case7_demand_table(csv_file):
        return make_response(
            jsonify({"message": "非法的输入数据格式，请人工复查！"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    is_valid, err_msg = do_data_check_for_input_case7_demand_table(csv_file)
    if not is_valid:
        return make_response(
            jsonify({"message": err_msg}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    response_object = {
        "message": "",
        "total_transportation_expenses": 0.0,
        "demand_table": []
    }
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        line = 0
        for row in csv_reader:
            if line == 0:
                response_object["total_transportation_expenses"] = row[3].strip()
            else:
                response_object["demand_table"].append(
                    {
                        "specification_code": row[0].strip(),
                        "quantity": row[1].strip()
                    }
                )
            line += 1

    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


'''
预览效果

规格编码 | 商品名称 | 规格名称 | 采购名称 | 数量 | 单价 | 金额 | 长度/cm | 宽度/cm | 高度/cm | 体积合计/m³ | 重量/g | 重量合计/kg
'''


# 预览"运费计算汇总单"的接口
@case7_blueprint.route("/preview", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def preview_report_file_case7():
    payload = request.get_json()
    compute_mode = int(payload.get("compute_mode", 0))
    total_transportation_expenses = float(payload.get("total_transportation_expenses", "0.0"))
    demand_table = payload.get("demand_table", [])

    weight_and_volume = {}
    for item in demand_table:
        specification_code = item["specification_code"]
        stmt = "SELECT product_weight, product_length, product_width, product_height \
FROM fotolei_pssa.products WHERE specification_code = '{}';".format(specification_code)
        rets = db_connector.query(stmt)
        weight_and_volume[specification_code] = {}
        if type(rets) is list and len(rets) > 0:
            weight_and_volume[specification_code]["quantity"] = int(item["quantity"])
            weight_and_volume[specification_code]["weight"] = rets[0][0]  # unit: g
            weight_and_volume[specification_code]["volume"] = rets[0][1] * rets[0][2] * rets[0][3]  # unit: cm^3
            if weight_and_volume[specification_code]["volume"] / 5 >= weight_and_volume[specification_code]["weight"]:
                weight_and_volume[specification_code]["converted_weight"] = int(weight_and_volume[specification_code]["volume"] / 5)
            else:
                weight_and_volume[specification_code]["converted_weight"] = weight_and_volume[specification_code]["weight"]

    preview_table = []
    if compute_mode == 0:
        total_weight = 0
        for _, v in weight_and_volume.items():
            total_weight += v["weight"] * v["quantity"]
        for k, v in weight_and_volume.items():
            cache = {}
            cache["specification_code"] = k
            cache["quantity"] = v["quantity"]
            cache["shared_weight"] = (v["weight"] * v["quantity"]) / 1000  # unit: kg
            cache["shared_transportation_expenses"] = float("{:.2f}".format(((v["weight"] * v["quantity"]) / total_weight) * total_transportation_expenses))
            cache["single_transportation_expenses"] = float("{:.2f}".format(cache["shared_transportation_expenses"] / v["quantity"]))
            preview_table.append(cache)
    elif compute_mode == 1:
        total_volume = 0
        for _, v in weight_and_volume.items():
            total_volume += v["volume"] * v["quantity"]
        for k, v in weight_and_volume.items():
            cache = {}
            cache["specification_code"] = k
            cache["quantity"] = v["quantity"]
            cache["shared_volume"] = (v["volume"] * v["quantity"]) / 1e6  # unit: m^3
            cache["shared_transportation_expenses"] = float("{:.2f}".format(((v["volume"] * v["quantity"]) / total_volume) * total_transportation_expenses))
            cache["single_transportation_expenses"] = float("{:.2f}".format(cache["shared_transportation_expenses"] / v["quantity"]))
            preview_table.append(cache)
    elif compute_mode == 2:
        total_converted_weight = 0
        for _, v in weight_and_volume.items():
            total_converted_weight += v["converted_weight"] * v["quantity"]
        for k, v in weight_and_volume.items():
            cache = {}
            cache["specification_code"] = k
            cache["quantity"] = v["quantity"]
            cache["shared_converted_weight"] = (v["converted_weight"] * v["quantity"]) / 1000  # unit: kg
            cache["shared_transportation_expenses"] = float("{:.2f}".format(((v["converted_weight"] * v["quantity"]) / total_converted_weight) * total_transportation_expenses))
            cache["single_transportation_expenses"] = float("{:.2f}".format(cache["shared_transportation_expenses"] / v["quantity"]))
            preview_table.append(cache)

    response_object = {"message": ""}
    response_object["preview_table"] = preview_table
    response_object["total_transportation_expenses"] = total_transportation_expenses
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 预下载"运费计算汇总单"的接口
@case7_blueprint.route("/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_EXPORT)
@cost_count
def prepare_report_file_case7():
    payload = request.get_json()
    compute_mode = int(payload.get("compute_mode", 0))
    total_transportation_expenses = payload.get("total_transportation_expenses", "0.0")
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("运费计算汇总单_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "运费计算汇总单_{}.csv".format(ts)
    with open(csv_file, "w", encoding="utf-8-sig") as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        if compute_mode == 0:
            csv_writer.writerow([
                "规格编码", "数量", "分担重量/kg",
                "分担运费", "单个运费", "运费总额：", total_transportation_expenses
            ])
        elif compute_mode == 1:
            csv_writer.writerow([
                "规格编码", "数量", "分担体积/m³",
                "分担运费", "单个运费", "运费总额：", total_transportation_expenses
            ])
        elif compute_mode == 2:
            csv_writer.writerow([
                "规格编码", "数量", "换算后的分担重量/kg",
                "分担运费", "单个运费", "运费总额：", total_transportation_expenses
            ])
        for item in preview_table:
            if compute_mode == 0:
                csv_writer.writerow([
                    item["specification_code"], item["quantity"], item["shared_weight"],
                    item["shared_transportation_expenses"], item["single_transportation_expenses"]
                ])
            elif compute_mode == 1:
                csv_writer.writerow([
                    item["specification_code"], item["quantity"], item["shared_volume"],
                    item["shared_transportation_expenses"], item["single_transportation_expenses"]
                ])
            elif compute_mode == 2:
                csv_writer.writerow([
                    item["specification_code"], item["quantity"], item["shared_converted_weight"],
                    item["shared_transportation_expenses"], item["single_transportation_expenses"]
                ])

    session["op_object"] = output_file

    response_object = {"message": ""}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


def do_data_schema_validation_for_input_case7_demand_table(csv_file: str):
    data_schema = [
        "规格编码", "数量", "运费"
    ]
    is_valid = True
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        for row in csv_reader:
            if len(row) != len(data_schema) + 1:
                is_valid = False
                break
            for idx, item in enumerate(row[:len(row) - 1]):
                if item.strip() != data_schema[idx]:
                    is_valid = False
                    break
            break
    if not is_valid:
        os.remove(csv_file)
    return is_valid


def do_data_check_for_input_case7_demand_table(csv_file: str):
    is_valid = True
    err_msg = ""
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        line = 0
        for row in csv_reader:
            if line == 0:
                if REG_POSITIVE_FLOAT.match(row[3]) is None:
                    is_valid = False
                    err_msg = "'运费'数据存在非法输入"
                    break
            else:
                if not get_lookup_table_k_sku_v_boolean(row[0]):
                    is_valid = False
                    err_msg = "'规格编码'不存在系统内，出现在第{}行。".format(line)
                    break
                if REG_POSITIVE_INT.match(row[1]) is None:
                    is_valid = False
                    err_msg = "'数量'数据存在非法输入，出现在第{}行。".format(line)
                    break
            line += 1
    if not is_valid:
        os.remove(csv_file)
    return is_valid, err_msg
