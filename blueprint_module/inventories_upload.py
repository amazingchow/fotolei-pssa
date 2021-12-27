# -*- coding: utf-8 -*-
import csv
import os
import pendulum
import shelve
import shutil
import sys
import time
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import logger
from utils import reg_int, reg_int_and_float
from utils import db_connector
from utils import lookup_table_sku_get_or_put
from utils import lookup_table_inventory_update_without_repetition
from utils import lookup_table_sku_brand_classification_1_2_association
from utils import cost_count
from utils import generate_file_digest, generate_digest


# 载入"库存数据报表"的接口
@blueprint.route("/api/v1/inventories/upload", methods=["POST"])
@cost_count
def upload_inventories():
    csv_files = request.files.getlist("file")
    import_date = request.form.get("import_date", "")
    csv_file_sha256 = generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/ggfilm-server/inventories/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_inventories(csv_file):
        response_object = {"status": "invalid input data schema"}
    else:
        load_file_repetition_lookup_table = shelve.open("./tmp/inventories_load_file_repetition_lookup_table", flag='c', writeback=False)
        file_digest = generate_file_digest(csv_file)
        if not load_file_repetition_lookup_table.get(file_digest, False):
            not_inserted_sku_list = []
            with open(csv_file, "r", encoding='utf-8-sig') as fd:
                csv_reader = csv.reader(fd, delimiter=",")
                line = 0
                for row in csv_reader:
                    if line > 0:
                        if not lookup_table_sku_get_or_put.get(row[2], False):
                            not_inserted_sku_list.append(row[2])
                    line += 1
            if len(not_inserted_sku_list) > 0:
                logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))
                response_object = {"status": "new SKUs"}
                response_object["added_skus"] = not_inserted_sku_list
            else:
                is_valid, err_msg = do_data_check_for_input_inventories(csv_file)
                if not is_valid:
                    response_object = {"status": "invalid input data"}
                    response_object["err_msg"] = err_msg
                    return jsonify(response_object)

                load_file_repetition_lookup_table[file_digest] = True

                do_intelligent_calibration_for_input_inventories(csv_file)

                if len(import_date) == 0:
                    today = pendulum.today()
                    last_month = today.subtract(months=1)
                    import_date = last_month.strftime('%Y-%m')
                add_date_brand_c1_c2_for_input_inventories(csv_file, import_date.strip())

                repeat = do_remove_repeat_inventories_updates(csv_file)

                db_connector.load_data_infile(
                    """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
                    "INTO TABLE ggfilm.inventories " +
                    "FIELDS TERMINATED BY ',' " +
                    """ENCLOSED BY '"' """ +
                    "LINES TERMINATED BY '\n' " +
                    "IGNORE 1 LINES " +
                    "(create_time, product_code, product_name, specification_code, specification_name, " +
                    "st_inventory_qty, st_inventory_total, purchase_qty, purchase_total, " +
                    "purchase_then_return_qty, purchase_then_return_total, sale_qty, sale_total, " +
                    "sale_then_return_qty, sale_then_return_total, others_qty, others_total, " +
                    "ed_inventory_qty, ed_inventory_total, " +
                    "extra_brand, extra_classification_1, extra_classification_2, anchor);"
                )

                with open(csv_file, "r", encoding='utf-8-sig') as fd:
                    csv_reader = csv.reader(fd, delimiter=",")
                    for _ in csv_reader:
                        pass
                    stmt = "INSERT INTO ggfilm.inventory_summary (total) VALUES (%s);"
                    db_connector.insert(stmt, (csv_reader.line_num - 1,))

                stmt = "INSERT INTO ggfilm.operation_logs (oplog) VALUES (%s);"
                db_connector.insert(stmt, ("导入{}".format(csv_files[0].filename),))

                response_object = {"status": "success"}
                if repeat > 0:
                    response_object["msg"] = "已自动删除{}条尝试重复导入的库存明细数据，目前不支持库存明细数据的覆盖写操作！".format(repeat)
                else:
                    response_object["msg"] = ""
        else:
            response_object = {"status": "repetition"}
        load_file_repetition_lookup_table.close()
    return jsonify(response_object)


def do_data_schema_validation_for_input_inventories(csv_file: str):
    data_schema = [
        "商品编码", "商品名称", "规格编码", "规格名称",
        "起始库存数量", "起始库存总额", "采购数量", "采购总额",
        "采购退货数量", "采购退货总额", "销售数量", "销售总额",
        "销售退货数量", "销售退货总额", "其他变更数量", "其他变更总额",
        "截止库存数量", "截止库存总额",
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


def do_data_check_for_input_inventories(csv_file: str):
    inventories_check_table = shelve.open("./tmp/inventories_check_table", flag='c', writeback=False)
    inventories_check_table_tmp = {}

    # 导入的起始库存数量 =? 最近一个月的截止库存数量
    is_valid = True
    err_msg = ""
    line = 0
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        for row in csv_reader:
            if line > 0:
                specification_code = row[2]
                st_inventory_qty = int(row[4])
                ed_inventory_qty = int(row[16])
                if specification_code in inventories_check_table.keys():
                    if st_inventory_qty != inventories_check_table[specification_code]:
                        err_msg = "导入的起始库存数量不等于最近一个月的截止库存数量，出现在第{}行。".format(line + 1)
                        is_valid = False
                    else:
                        inventories_check_table_tmp[specification_code] = ed_inventory_qty
                else:
                    inventories_check_table_tmp[specification_code] = ed_inventory_qty
            line += 1
    if is_valid:
        for k, v in inventories_check_table_tmp.items():
            inventories_check_table[k] = v

    if not is_valid:
        os.remove(csv_file)

    inventories_check_table.close()
    return is_valid, err_msg


def do_intelligent_calibration_for_input_inventories(csv_file: str):
    # 1. 表格里面某些数据行存在多余的逗号，程序需要做下智能矫正
    # 2. “起始库存数量”，“起始库存总额”，等数据项存在非法输入，程序不需要做智能矫正，直接返回错误
    fr = open(csv_file, "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")

    is_valid = True
    err_msg = ""

    line = 0
    for row in csv_reader:
        if line == 0:
            csv_writer.writerow(row)
        else:
            if len(row[4]) == 0:
                row[4] = "0"
            elif reg_int.match(row[4]) is None:
                is_valid = False
                err_msg = "'起始库存数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '起始库存数量': {}".format(row[4]))
                break
            if len(row[5]) == 0:
                row[5] = "0"
            elif reg_int_and_float.match(row[5]) is None:
                is_valid = False
                err_msg = "'起始库存总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '起始库存总额': {}".format(row[5]))
                break
            if len(row[6]) == 0:
                row[6] = "0"
            elif reg_int.match(row[6]) is None:
                is_valid = False
                err_msg = "'采购数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '采购数量': {}".format(row[6]))
                break
            if len(row[7]) == 0:
                row[7] = "0"
            elif reg_int_and_float.match(row[7]) is None:
                is_valid = False
                err_msg = "'采购总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '采购总额': {}".format(row[7]))
                break
            if len(row[8]) == 0:
                row[8] = "0"
            elif reg_int.match(row[8]) is None:
                is_valid = False
                err_msg = "'采购退货数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '采购退货数量': {}".format(row[8]))
                break
            if len(row[9]) == 0:
                row[9] = "0"
            elif reg_int_and_float.match(row[9]) is None:
                is_valid = False
                err_msg = "'采购退货总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '采购退货总额': {}".format(row[9]))
                break
            if len(row[10]) == 0:
                row[10] = "0"
            elif reg_int.match(row[10]) is None:
                is_valid = False
                err_msg = "'销售数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '销售数量': {}".format(row[10]))
                break
            if len(row[11]) == 0:
                row[11] = "0"
            elif reg_int_and_float.match(row[11]) is None:
                is_valid = False
                err_msg = "'销售总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '销售总额': {}".format(row[11]))
                break
            if len(row[12]) == 0:
                row[12] = "0"
            elif reg_int.match(row[12]) is None:
                is_valid = False
                err_msg = "'销售退货数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '销售退货数量': {}".format(row[12]))
                break
            if len(row[13]) == 0:
                row[13] = "0"
            elif reg_int_and_float.match(row[13]) is None:
                is_valid = False
                err_msg = "'销售退货总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '销售退货总额': {}".format(row[13]))
                break
            if len(row[14]) == 0:
                row[14] = "0"
            elif reg_int.match(row[14]) is None:
                is_valid = False
                err_msg = "'其他变更数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '其他变更数量': {}".format(row[14]))
                break
            if len(row[15]) == 0:
                row[15] = "0"
            elif reg_int_and_float.match(row[15]) is None:
                is_valid = False
                err_msg = "'其他变更总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '其他变更总额': {}".format(row[15]))
                break
            if len(row[16]) == 0:
                row[16] = "0"
            elif reg_int.match(row[16]) is None:
                is_valid = False
                err_msg = "'截止库存数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '截止库存数量': {}".format(row[16]))
                break
            if len(row[17]) == 0:
                row[17] = "0"
            elif reg_int_and_float.match(row[17]) is None:
                is_valid = False
                err_msg = "'截止库存总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                logger.error("invalid '截止库存总额': {}".format(row[17]))
                break
            if len(row) < 18:
                while len(row) < 18:
                    row.append("0")
            elif len(row) > 18:
                row = row[:18]
            csv_writer.writerow(row)
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)

    if not is_valid:
        os.remove(csv_file)
    return is_valid, err_msg


def add_date_brand_c1_c2_for_input_inventories(csv_file: str, import_date: str):
    fr = open(csv_file, "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")
    line = 0
    for row in csv_reader:
        if line == 0:
            new_row = ["年月"] + row + ["品牌", "分类1", "分类2", "锚"]
            csv_writer.writerow(new_row)
        else:
            new_row = [import_date] + row + [
                lookup_table_sku_brand_classification_1_2_association[row[2]][0],
                lookup_table_sku_brand_classification_1_2_association[row[2]][1],
                lookup_table_sku_brand_classification_1_2_association[row[2]][2],
                "0"
            ]
            csv_writer.writerow(new_row)
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)


def do_remove_repeat_inventories_updates(csv_file: str):
    repeat = 0

    fr = open(csv_file, "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")
    line = 0
    for row in csv_reader:
        if line == 0:
            csv_writer.writerow(row)
        else:
            k = generate_digest("{} | {}".format(row[0], row[3]))
            if not lookup_table_inventory_update_without_repetition.get(k, False):
                lookup_table_inventory_update_without_repetition[k] = True
                csv_writer.writerow(row)
            else:
                repeat += 1
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)

    return repeat
