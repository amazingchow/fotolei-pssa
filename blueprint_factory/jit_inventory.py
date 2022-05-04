# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import time

from flask import current_app
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
from utils import ACTION_TYPE_IMPORT
from utils import get_lookup_table_k_sku_v_boolean
from utils import REG_INT
from utils import ROLE_TYPE_ORDINARY_USER


jit_inventory_blueprint = Blueprint(
    name="fotolei_pssa_jit_inventory_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/jitinventory",
)


# 载入"实时可用库存表"的接口
@jit_inventory_blueprint.route("/upload", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_IMPORT)
@cost_count
def upload_jit_inventory_data():
    csv_files = request.files.getlist("file")
    if len(csv_files) != 1:
        return make_response(
            jsonify({"message": "上传的文件数量不等于一份"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    csv_file = "{}/fotolei-pssa/jit-inventory/{}_{}".format(
        os.path.expanduser("~"), int(time.time()), csv_files[0].filename
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_jit_inventories(csv_file):
        return make_response(
            jsonify({"message": "非法的输入数据格式，请人工复查！"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    is_valid, err_msg = do_data_check_for_input_jit_inventories(csv_file)
    if not is_valid:
        response_object = {"message": err_msg}
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    sku_inventory_tuple_list = []
    not_inserted_sku_list = []
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        for row in csv_reader:
            if not get_lookup_table_k_sku_v_boolean(row[0]):
                not_inserted_sku_list.append(row[0])
            else:
                sku_inventory_tuple_list.append((row[1], row[0]))
    if len(not_inserted_sku_list) > 0:
        current_app.logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))
        # 新增sku，需要向用户展示
        response_object = {"message": "", "added_skus": not_inserted_sku_list}
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_406_NOT_ACCEPTABLE
        )

    stmt = "UPDATE fotolei_pssa.products SET jit_inventory = %s WHERE specification_code = %s;"
    db_connector.batch_update(stmt, sku_inventory_tuple_list)

    session["op_object"] = csv_files[0].filename
    return make_response(
        jsonify({"message": ""}),
        StatusCode.HTTP_200_OK
    )


def do_data_schema_validation_for_input_jit_inventories(csv_file: str):
    data_schema = [
        "规格编码", "实时可用库存",
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


def do_data_check_for_input_jit_inventories(csv_file: str):
    is_valid = True
    err_msg = ""
    with open(csv_file, "r", encoding="utf-8-sig") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        line = 1
        for row in csv_reader:
            if REG_INT.match(row[1]) is None:
                is_valid = False
                err_msg = "'实时可用库存'数据存在非法输入，出现在第{}行。".format(line)
                break
            line += 1
    if not is_valid:
        os.remove(csv_file)
    return is_valid, err_msg
