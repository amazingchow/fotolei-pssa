# -*- coding: utf-8 -*-
import csv
import os
import sys
import time
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import logger
from utils import reg_int
from utils import db_connector
from utils import lookup_table_sku_get_or_put
from utils import cost_count


# 载入"实时可用库存报表"的接口
@blueprint.route("/api/v1/jitinventory/upload", methods=["POST"])
@cost_count
def upload_jit_inventory_data():
    csv_files = request.files.getlist("file")
    csv_file = "{}/ggfilm-server/jit_inventory/{}_{}".format(
        os.path.expanduser("~"), int(time.time()), csv_files[0].filename
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_jit_inventories(csv_file):
        response_object = {"status": "invalid input data schema"}
        return jsonify(response_object)

    is_valid, err_msg = do_data_check_for_input_jit_inventories(csv_file)
    if not is_valid:
        response_object = {"status": "invalid input data"}
        response_object["err_msg"] = err_msg
        return jsonify(response_object)

    sku_inventory_tuple_list = []
    not_inserted_sku_list = []
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        for row in csv_reader:
            if not lookup_table_sku_get_or_put.get(row[0], False):
                not_inserted_sku_list.append(row[0])
            else:
                sku_inventory_tuple_list.append((row[1], row[0]))
    if len(not_inserted_sku_list) > 0:
        response_object = {"status": "failed"}
        logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))
        # 新增sku，需要向用户展示
        response_object["added_skus"] = not_inserted_sku_list
        return jsonify(response_object)

    stmt = "UPDATE fotolei_pssa.products SET jit_inventory = %s WHERE specification_code = %s;"
    db_connector.batch_update(stmt, sku_inventory_tuple_list)
    stmt = "INSERT INTO fotolei_pssa.operation_logs (oplog) VALUES (%s);"
    db_connector.insert(stmt, ("导入{}".format(csv_files[0].filename),))

    response_object = {"status": "success"}
    return jsonify(response_object)


def do_data_schema_validation_for_input_jit_inventories(csv_file: str):
    data_schema = [
        "规格编码", "实时可用库存",
    ]
    is_valid = True
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
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
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        line = 1
        for row in csv_reader:
            if reg_int.match(row[1]) is None:
                is_valid = False
                err_msg = "'实时可用库存'数据存在非法输入，出现在第{}行。".format(line)
                break
            line += 1
    if not is_valid:
        os.remove(csv_file)
    return is_valid, err_msg
