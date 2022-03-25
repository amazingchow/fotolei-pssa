# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import pendulum
import platform
import shelve
import shutil
import time

from flask import current_app
from flask import Blueprint
from flask import jsonify
from flask import request

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from db import db_connector
from utils import clean_lookup_table_k_ct_sku_v_boolean
from utils import init_lookup_table_k_ct_sku_v_boolean
from utils import get_lookup_table_k_ct_sku_v_boolean
from utils import get_lookup_table_k_sku_v_boolean
from utils import get_lookup_table_k_sku_v_brand_c1_c2_is_combined
from utils import put_lookup_table_k_ct_sku_v_boolean
from utils import REG_INT
from utils import REG_INT_AND_FLOAT
from utils import ROLE_TYPE_ORDINARY_USER
from utils import ROLE_TYPE_SUPER_ADMIN
from utils import util_cost_count
from utils import util_generate_file_digest, util_generate_digest
from utils import util_silent_remove


inventory_blueprint = Blueprint(
    name="fotolei_pssa_inventory_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/inventories",
)


# 载入"库存数据报表"的接口
@inventory_blueprint.route("/upload", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def upload_inventories():
    csv_files = request.files.getlist("file")
    import_date = request.form.get("import_date", "")
    csv_file_sha256 = util_generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/fotolei-pssa/inventories/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_inventories(csv_file):
        response_object = {"status": "invalid input data schema"}
    else:
        load_file_repetition_lookup_table = shelve.open("{}/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table".format(
            os.path.expanduser("~")), flag='c', writeback=False)
        file_digest = util_generate_file_digest(csv_file)
        if not load_file_repetition_lookup_table.get(file_digest, False):
            not_inserted_sku_list = []
            with open(csv_file, "r", encoding='utf-8-sig') as fd:
                csv_reader = csv.reader(fd, delimiter=",")
                next(csv_reader, None)  # skip the header line
                for row in csv_reader:
                    if not get_lookup_table_k_sku_v_boolean(row[2]):
                        not_inserted_sku_list.append(row[2])
            if len(not_inserted_sku_list) > 0:
                current_app.logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))
                response_object = {"status": "new SKUs"}
                response_object["added_skus"] = not_inserted_sku_list
            else:
                is_valid, err_msg = do_data_check_for_input_inventories(csv_file)
                if not is_valid:
                    response_object = {"status": "invalid input data"}
                    response_object["err_msg"] = err_msg
                    return jsonify(response_object)

                do_intelligent_calibration_for_input_inventories(csv_file)

                if len(import_date) == 0:
                    today = pendulum.today()
                    last_month = today.subtract(months=1)
                    import_date = last_month.strftime('%Y-%m')
                add_date_brand_c1_c2_for_input_inventories(csv_file, import_date.strip())

                repeat = do_remove_repeat_inventories_updates(csv_file)

                record_first_and_last_import_date_for_input_inventories(csv_file)

                db_connector.load_data_infile(
                    """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
                    "INTO TABLE fotolei_pssa.inventories " +
                    "FIELDS TERMINATED BY ',' " +
                    """ENCLOSED BY '"' """ +
                    "LINES TERMINATED BY '\n' " +
                    "IGNORE 1 LINES " +
                    "(create_time, product_code, product_name, specification_code, specification_name, " +
                    "st_inventory_qty, st_inventory_total, purchase_qty, purchase_total, " +
                    "purchase_then_return_qty, purchase_then_return_total, sale_qty, sale_total, " +
                    "sale_then_return_qty, sale_then_return_total, others_qty, others_total, " +
                    "ed_inventory_qty, ed_inventory_total, " +
                    "extra_brand, extra_classification_1, extra_classification_2, extra_is_combined, anchor);"
                )

                with open(csv_file, "r", encoding='utf-8-sig') as fd:
                    csv_reader = csv.reader(fd, delimiter=",")
                    for _ in csv_reader:
                        pass
                    stmt = "INSERT INTO fotolei_pssa.inventory_summary (total) VALUES (%s);"
                    db_connector.insert(stmt, (csv_reader.line_num - 1,))

                stmt = "INSERT INTO fotolei_pssa.operation_logs (oplog) VALUES (%s);"
                db_connector.insert(stmt, ("导入{}".format(csv_files[0].filename),))

                init_lookup_table_k_ct_sku_v_boolean()

                load_file_repetition_lookup_table[file_digest] = True

                response_object = {"status": "success"}
                if repeat > 0:
                    response_object["msg"] = "已自动删除{}条尝试重复导入的库存明细数据，目前不支持库存明细数据的覆盖写操作！".format(repeat)
                else:
                    response_object["msg"] = ""
        else:
            response_object = {"status": "repetition"}
        load_file_repetition_lookup_table.close()
    return jsonify(response_object)


# 获取所有库存条目的接口, 带有翻页功能
@inventory_blueprint.route("/", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@util_cost_count
def list_inventories():
    page_offset = request.args.get("page.offset", 0)
    page_limit = request.args.get("page.limit", 20)

    # TODO: 优化SQL
    stmt = "SELECT specification_code, \
st_inventory_qty, purchase_qty, purchase_then_return_qty, sale_qty, \
sale_then_return_qty, others_qty, ed_inventory_qty, create_time \
FROM fotolei_pssa.inventories ORDER BY create_time DESC LIMIT {}, {};".format(
        page_offset, page_limit)
    inventories = db_connector.query(stmt)

    response_object = {"status": "success"}
    if (type(inventories) is not list) or (type(inventories) is list and len(inventories) == 0):
        response_object = {"status": "not found"}
        response_object["inventories"] = []
    else:
        response_object["inventories"] = inventories
    return jsonify(response_object)


# 获取总库存条目量的接口
@inventory_blueprint.route("/total", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@util_cost_count
def get_inventories_total():
    stmt = "SELECT SUM(total) FROM fotolei_pssa.inventory_summary;"
    ret = db_connector.query(stmt)
    response_object = {"status": "success"}
    if type(ret) is list and len(ret) > 0 and ret[0][0] is not None:
        response_object["inventories_total"] = ret[0][0]
    else:
        response_object["inventories_total"] = 0
    return jsonify(response_object)


# 删除所有库存条目的接口
@inventory_blueprint.route("/all/clean", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def clean_all_inventories():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.inventories;"
        db_connector.drop_table(stmt)
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.inventory_summary;"
        db_connector.drop_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.inventories (
    id                         INT           NOT NULL AUTO_INCREMENT,
    product_code               VARCHAR(64),            /* 商品编码 */
    product_name               VARCHAR(128),           /* 商品名称 */
    specification_code         VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name         VARCHAR(128),           /* 规格名称 */
    st_inventory_qty           INT,                    /* 起始库存数量 */
    st_inventory_total         FLOAT,                  /* 起始库存总额 */
    purchase_qty               INT,                    /* 采购数量 */
    purchase_total             FLOAT,                  /* 采购总额 */
    purchase_then_return_qty   INT,                    /* 采购退货数量 */
    purchase_then_return_total FLOAT,                  /* 采购退货总额 */
    sale_qty                   INT,                    /* 销售数量 */
    sale_total                 FLOAT,                  /* 销售总额 */
    sale_then_return_qty       INT,                    /* 销售退货数量 */
    sale_then_return_total     FLOAT,                  /* 销售退货总额 */
    others_qty                 INT,                    /* 其他变更数量 */
    others_total               FLOAT,                  /* 其他变更总额 */
    ed_inventory_qty           INT,                    /* 截止库存数量 */
    ed_inventory_total         FLOAT,                  /* 截止库存总额 */
    create_time                VARCHAR(10),            /* 年月的格式 */
    extra_brand                VARCHAR(64),            /* 品牌 */
    extra_classification_1     VARCHAR(64),            /* 分类1 */
    extra_classification_2     VARCHAR(64),            /* 分类2 */
    extra_is_combined          VARCHAR(32),            /* 是否是组合商品 */
    anchor                     TINYINT,                /* 锚，防止‘组合商品‘读出来带空格 */
    PRIMARY KEY (id),
    KEY inventories_ct (create_time),
    KEY inventories_specification_code_ct (specification_code, create_time),
    KEY inventories_extra_is_combined_ct (extra_is_combined, create_time),
    KEY inventories_extra_is_combined_extra_brand_ct (extra_is_combined, extra_brand, create_time),
    KEY inventories_extra_is_combined_extra_c1_ct (extra_is_combined, extra_classification_1, create_time),
    KEY inventories_extra_is_combined_extra_c2_ct (extra_is_combined, extra_classification_2, create_time)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.inventory_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        if platform.system() == "Linux":
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_check_table".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table".format(
                os.path.expanduser("~")))
        else:
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table.db".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_check_table.db".format(
                os.path.expanduser("~")))
            util_silent_remove("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table.db".format(
                os.path.expanduser("~")))
        clean_lookup_table_k_ct_sku_v_boolean()
        response_object = {"status": "success"}
        return jsonify(response_object)
    else:
        response_object = {"status": "invalid input data"}
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
    inventories_check_table = shelve.open("{}/fotolei-pssa/tmp-files/inventories_check_table".format(
        os.path.expanduser("~")), flag='c', writeback=False)
    inventories_check_table_tmp = {}

    # 导入的起始库存数量 =? 最近一个月的截止库存数量
    is_valid = True
    err_msg = ""
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        line = 1
        for row in csv_reader:
            if len(row[4]) > 0 and len(row[16]) > 0:
                specification_code = row[2]
                st_inventory_qty = int(row[4])
                ed_inventory_qty = int(row[16])
                if specification_code in inventories_check_table.keys():
                    if st_inventory_qty != inventories_check_table[specification_code]:
                        err_msg = "导入的起始库存数量不等于最近一个月的截止库存数量，出现在第{}行。".format(line)
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
            elif REG_INT.match(row[4]) is None:
                is_valid = False
                err_msg = "'起始库存数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '起始库存数量': {}".format(row[4]))
                break
            if len(row[5]) == 0:
                row[5] = "0"
            elif REG_INT_AND_FLOAT.match(row[5]) is None:
                is_valid = False
                err_msg = "'起始库存总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '起始库存总额': {}".format(row[5]))
                break
            if len(row[6]) == 0:
                row[6] = "0"
            elif REG_INT.match(row[6]) is None:
                is_valid = False
                err_msg = "'采购数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '采购数量': {}".format(row[6]))
                break
            if len(row[7]) == 0:
                row[7] = "0"
            elif REG_INT_AND_FLOAT.match(row[7]) is None:
                is_valid = False
                err_msg = "'采购总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '采购总额': {}".format(row[7]))
                break
            if len(row[8]) == 0:
                row[8] = "0"
            elif REG_INT.match(row[8]) is None:
                is_valid = False
                err_msg = "'采购退货数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '采购退货数量': {}".format(row[8]))
                break
            if len(row[9]) == 0:
                row[9] = "0"
            elif REG_INT_AND_FLOAT.match(row[9]) is None:
                is_valid = False
                err_msg = "'采购退货总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '采购退货总额': {}".format(row[9]))
                break
            if len(row[10]) == 0:
                row[10] = "0"
            elif REG_INT.match(row[10]) is None:
                is_valid = False
                err_msg = "'销售数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '销售数量': {}".format(row[10]))
                break
            if len(row[11]) == 0:
                row[11] = "0"
            elif REG_INT_AND_FLOAT.match(row[11]) is None:
                is_valid = False
                err_msg = "'销售总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '销售总额': {}".format(row[11]))
                break
            if len(row[12]) == 0:
                row[12] = "0"
            elif REG_INT.match(row[12]) is None:
                is_valid = False
                err_msg = "'销售退货数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '销售退货数量': {}".format(row[12]))
                break
            if len(row[13]) == 0:
                row[13] = "0"
            elif REG_INT_AND_FLOAT.match(row[13]) is None:
                is_valid = False
                err_msg = "'销售退货总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '销售退货总额': {}".format(row[13]))
                break
            if len(row[14]) == 0:
                row[14] = "0"
            elif REG_INT.match(row[14]) is None:
                is_valid = False
                err_msg = "'其他变更数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '其他变更数量': {}".format(row[14]))
                break
            if len(row[15]) == 0:
                row[15] = "0"
            elif REG_INT_AND_FLOAT.match(row[15]) is None:
                is_valid = False
                err_msg = "'其他变更总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '其他变更总额': {}".format(row[15]))
                break
            if len(row[16]) == 0:
                row[16] = "0"
            elif REG_INT.match(row[16]) is None:
                is_valid = False
                err_msg = "'截止库存数量'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '截止库存数量': {}".format(row[16]))
                break
            if len(row[17]) == 0:
                row[17] = "0"
            elif REG_INT_AND_FLOAT.match(row[17]) is None:
                is_valid = False
                err_msg = "'截止库存总额'数据存在非法输入，出现在第{}行。".format(line + 1)
                current_app.logger.error("invalid '截止库存总额': {}".format(row[17]))
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
            new_row = ["年月"] + row + ["品牌", "分类1", "分类2", "组合商品", "锚"]
            csv_writer.writerow(new_row)
        else:
            new_row = [import_date] + row + [
                get_lookup_table_k_sku_v_brand_c1_c2_is_combined(row[2])[0],
                get_lookup_table_k_sku_v_brand_c1_c2_is_combined(row[2])[1],
                get_lookup_table_k_sku_v_brand_c1_c2_is_combined(row[2])[2],
                get_lookup_table_k_sku_v_brand_c1_c2_is_combined(row[2])[3],
                "0"
            ]
            csv_writer.writerow(new_row)
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)


def record_first_and_last_import_date_for_input_inventories(csv_file: str):
    inventories_import_date_record_table = shelve.open("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table".format(
        os.path.expanduser("~")), flag='c', writeback=False)

    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        next(csv_reader, None)  # skip the header line
        for row in csv_reader:
            import_date = row[0]
            specification_code = row[3]

            v = inventories_import_date_record_table.get(specification_code, [])
            if len(v) == 0:
                inventories_import_date_record_table[specification_code] = [import_date, import_date]
            else:
                if import_date < v[0]:
                    v[0] = import_date
                elif import_date > v[1]:
                    v[1] = import_date
                inventories_import_date_record_table[specification_code] = v

    inventories_import_date_record_table.close()
    return


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
            k = util_generate_digest("{} | {}".format(row[0], row[3]))
            if not get_lookup_table_k_ct_sku_v_boolean(k):
                put_lookup_table_k_ct_sku_v_boolean(k, True)
                csv_writer.writerow(row)
            else:
                repeat += 1
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)

    return repeat
