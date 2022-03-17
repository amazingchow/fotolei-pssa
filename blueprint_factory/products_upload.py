# -*- coding: utf-8 -*-
import csv
import os
import shelve
import shutil
import sys
import time
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import logger
from utils import reg_positive_int, reg_int, reg_int_and_float
from utils import db_connector
from utils import lookup_table_sku_get_or_put
from utils import cost_count
from utils import generate_file_digest, generate_digest
from utils import update_lookup_table_brand_classification_1_2_association
from utils import init_lookup_table_sku_brand_classification_1_2_association


# 载入"商品明细数据报表"的接口
@blueprint.route("/api/v1/products/upload", methods=["POST"])
@cost_count
def upload_products():
    csv_files = request.files.getlist("file")
    csv_file_sha256 = generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/fotolei-pssa/products/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    # 校验表格格式，格式有变更，当前不让导入，需要人工干预解决
    if not do_data_schema_validation_for_input_products(csv_file):
        response_object = {"status": "invalid input data schema"}
        return jsonify(response_object)

    # 用于检查是否是重复导入的数据报表？
    load_file_repetition_lookup_table = shelve.open("{}/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table".format(
        os.path.expanduser("~")), flag='c', writeback=False)
    file_digest = generate_file_digest(csv_file)
    if load_file_repetition_lookup_table.get(file_digest, False):
        load_file_repetition_lookup_table.close()
        response_object = {"status": "repetition"}
        return jsonify(response_object)

    # 校验数据格式，对不规范的数据做自动校正，出现无法校正的情况直接报错退出
    is_valid, err_msg = do_intelligent_calibration_for_input_products(csv_file)
    if not is_valid:
        response_object = {"status": "invalid input data"}
        response_object["err_msg"] = err_msg
        return jsonify(response_object)

    response_object = {"status": "success"}
    # 用于检查是否有新增的SKU？是否是重复导入的SKU？
    add, exist = do_data_check_for_input_products(csv_file)
    response_object["items_total"] = add + exist
    response_object["items_add"] = add
    response_object["items_exist"] = exist
    # 如果没有新增SKU，直接返回
    if add > 0:
        logger.info("Insert {} SKUs into lookup_table_sku_get_or_put!!!".format(add))

        db_connector.load_data_infile(
            """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
            "INTO TABLE fotolei_pssa.products " +
            "FIELDS TERMINATED BY ',' " +
            """ENCLOSED BY '"' """ +
            "LINES TERMINATED BY '\n' " +
            "IGNORE 1 LINES " +
            "(product_code, specification_code, product_name, specification_name, " +
            "brand, classification_1, classification_2, product_series, stop_status, " +
            "product_weight, product_length, product_width, product_height, " +
            "is_combined, be_aggregated, is_import, supplier_name, " +
            "purchase_name, jit_inventory, moq);"
        )

        with open(csv_file, "r", encoding='utf-8-sig') as fd:
            csv_reader = csv.reader(fd, delimiter=",")
            for _ in csv_reader:
                pass
            stmt = "INSERT INTO fotolei_pssa.product_summary (total) VALUES (%s);"
            db_connector.insert(stmt, (csv_reader.line_num - 1,))
        stmt = "INSERT INTO fotolei_pssa.operation_logs (oplog) VALUES (%s);"
        db_connector.insert(stmt, ("导入{}".format(csv_files[0].filename),))

        update_lookup_table_brand_classification_1_2_association()
        init_lookup_table_sku_brand_classification_1_2_association()

        load_file_repetition_lookup_table[file_digest] = True
    load_file_repetition_lookup_table.close()
    return jsonify(response_object)


def do_data_schema_validation_for_input_products(csv_file: str):
    data_schema = [
        "商品编码", "规格编码", "商品名称", "规格名称",
        "品牌", "分类1", "分类2", "产品系列", "STOP状态",
        "重量/g", "长度/cm", "宽度/cm", "高度/cm",
        "组合商品", "参与统计", "进口商品", "供应商名称",
        "采购名称", "实时可用库存", "最小订货单元",
    ]
    is_valid = True
    # 详情见 https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
    # 真是一个非常难搞的问题啊!!!
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


def do_intelligent_calibration_for_input_products(csv_file: str):
    # 1. 表格里面存在很多空行（但是有占位符），程序需要做下智能矫正
    # 2. 表格里面存在很多只有逗号的行，程序需要做下智能矫正
    # 3.1. “品牌”，“分类1”，“分类2”，“产品系列”，“供应商名称”，“采购名称”存在“0”这种输入，程序需要做下智能矫正
    # 3.2. “品牌”，“分类1”，“分类2”，“产品系列”，“供应商名称”，“采购名称”中出现的英文全部切成小写，程序需要做下智能矫正
    # 4.1. “STOP状态”，“组合商品”，“参与统计”，“进口商品”存在“0”或”1“这种输入，程序需要做下智能矫正
    # 4.2. “STOP状态”，“组合商品”，“参与统计”，“进口商品”存在非法输入，程序不需要做智能矫正，直接返回错误
    # 5. “重量”，“长度”，“宽度”，“高度”，“实时可用库存“，“最小订货单元”存在非法输入，程序不需要做智能矫正，直接返回错误
    is_valid = True
    err_msg = ""

    fr = open(csv_file, "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")
    line = 0
    for row in csv_reader:
        if line == 0:
            csv_writer.writerow(row)
        else:
            new_row = []
            for item in row:
                new_row.append(item.strip())
            all_empty = True
            for item in new_row:
                if len(item) > 0:
                    all_empty = False
            if not all_empty:
                for i in [4, 5, 6, 7, 16, 17]:
                    if new_row[i] == "0":
                        new_row[i] = ""
                    new_row[i] = new_row[i].lower()
                if new_row[8] != "在用" and new_row[8] != "停用":
                    if len(new_row[8]) == 0 or new_row[8] == "0":
                        new_row[8] = "停用"
                    elif new_row[8] == "1":
                        new_row[8] = "在用"
                    else:
                        is_valid = False
                        err_msg = "'STOP状态'数据存在非法输入，出现在第{}行。".format(line + 1)
                        logger.error("invalid 'STOP状态': {}".format(new_row[8]))
                        break
                if new_row[13] != "是" and new_row[13] != "否":
                    if len(new_row[13]) == 0 or new_row[13] == "0":
                        new_row[13] = "否"
                    elif new_row[13] == "1":
                        new_row[13] = "是"
                    else:
                        is_valid = False
                        err_msg = "'组合商品'数据存在非法输入，出现在第{}行。".format(line + 1)
                        logger.error("invalid '组合商品': {}".format(new_row[13]))
                        break
                if new_row[14] != "参与" and new_row[14] != "不参与":
                    if len(new_row[14]) == 0 or new_row[14] == "0":
                        new_row[14] = "不参与"
                    elif new_row[14] == "1":
                        new_row[14] = "参与"
                    else:
                        is_valid = False
                        err_msg = "'参与统计'数据存在非法输入，出现在第{}行。".format(line + 1)
                        logger.error("invalid '参与统计': {}".format(new_row[14]))
                        break
                if new_row[15] != "进口品" and new_row[15] != "非进口品":
                    if len(new_row[15]) == 0 or new_row[15] == "0":
                        new_row[15] = "非进口品"
                    elif new_row[15] == "1":
                        new_row[15] = "进口品"
                    else:
                        is_valid = False
                        err_msg = "'进口商品'数据存在非法输入，出现在第{}行。".format(line + 1)
                        logger.error("invalid '进口商品': {}".format(new_row[15]))
                        break
                if len(new_row[9]) == 0:
                    new_row[9] = "0"
                elif reg_int_and_float.match(new_row[9]) is None:
                    is_valid = False
                    err_msg = "'重量'数据存在非法输入，出现在第{}行。".format(line + 1)
                    logger.error("invalid '重量': {}".format(new_row[9]))
                    break
                if len(new_row[10]) == 0:
                    new_row[10] = "0"
                elif reg_int_and_float.match(new_row[10]) is None:
                    is_valid = False
                    err_msg = "'长度'数据存在非法输入，出现在第{}行。".format(line + 1)
                    logger.error("invalid '长度': {}".format(new_row[10]))
                    break
                if len(new_row[11]) == 0:
                    new_row[11] = "0"
                elif reg_int_and_float.match(new_row[11]) is None:
                    is_valid = False
                    err_msg = "'宽度'数据存在非法输入，出现在第{}行。".format(line + 1)
                    logger.error("invalid '宽度': {}".format(new_row[11]))
                    break
                if len(new_row[12]) == 0:
                    new_row[12] = "0"
                elif reg_int_and_float.match(new_row[12]) is None:
                    is_valid = False
                    err_msg = "'高度'数据存在非法输入，出现在第{}行。".format(line + 1)
                    logger.error("invalid '高度': {}".format(new_row[12]))
                    break
                if len(new_row[18]) == 0:
                    new_row[18] = "0"
                elif reg_int.match(new_row[18]) is None:
                    is_valid = False
                    err_msg = "'实时可用库存'数据存在非法输入，出现在第{}行。".format(line + 1)
                    logger.error("invalid '实时可用库存': {}".format(new_row[18]))
                    break
                if len(new_row[19]) == 0:
                    new_row[19] = "1"
                elif reg_positive_int.match(new_row[19]) is None:
                    is_valid = False
                    err_msg = "'最小订货单元'数据存在非法输入，出现在第{}行。".format(line + 1)
                    logger.error("invalid '最小订货单元': {}".format(new_row[19]))
                    break
                csv_writer.writerow(new_row)
        line += 1

    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)

    if not is_valid:
        os.remove(csv_file)
    return is_valid, err_msg


def do_data_check_for_input_products(csv_file: str):
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")

    exist = 0
    total = 0
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        line = 0
        for row in csv_reader:
            if line > 0:
                total += 1
                if lookup_table_sku_get_or_put.get(row[1], False):
                    exist += 1
                else:
                    lookup_table_sku_get_or_put[row[1]] = True
                    csv_writer.writerow(row)
            else:
                csv_writer.writerow(row)
            line += 1

    fw.close()
    shutil.move(csv_file + ".tmp", csv_file)
    return total - exist, exist
