# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import platform
import shelve
import shutil
import time

from flask import current_app
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask_api import status as StatusCode

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from db import db_connector
from utils import get_lookup_table_k_sku_v_boolean
from utils import init_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name
from utils import init_lookup_table_k_brand_v_brand_c2
from utils import init_lookup_table_k_c1_v_c1_c2
from utils import init_lookup_table_k_sku_v_boolean
from utils import init_lookup_table_k_sku_v_brand_c1_c2_is_combined
from utils import clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name
from utils import clean_lookup_table_k_brand_v_brand_c2
from utils import clean_lookup_table_k_c1_v_c1_c2
from utils import clean_lookup_table_k_sku_v_boolean
from utils import clean_lookup_table_k_sku_v_brand_c1_c2_is_combined
from utils import put_lookup_table_k_sku_v_boolean
from utils import REG_INT
from utils import REG_INT_AND_FLOAT
from utils import REG_POSITIVE_INT
from utils import ROLE_TYPE_ORDINARY_USER
from utils import ROLE_TYPE_SUPER_ADMIN
from utils import util_cost_count
from utils import util_generate_digest
from utils import util_generate_bytes_in_hdd_digest
from utils import util_silent_remove


product_blueprint = Blueprint(
    name="fotolei_pssa_product_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/products",
)


# 载入"商品明细数据报表"的接口
@product_blueprint.route("/upload", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def upload_products():
    csv_files = request.files.getlist("file")
    if len(csv_files) != 1:
        return make_response(
            jsonify({"message": "invalid upload"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    csv_file_sha256 = util_generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/fotolei-pssa/products/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    # 校验表格格式，格式有变更，当前不让导入，需要人工干预解决
    if not do_data_schema_validation_for_input_products(csv_file):
        return make_response(
            jsonify({"message": "invalid data schema"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    # 用于检查是否是重复导入的数据报表？
    load_file_repetition_lookup_table = shelve.open("{}/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table".format(
        os.path.expanduser("~")), flag='c', writeback=False)
    digest = util_generate_bytes_in_hdd_digest(csv_file)
    if load_file_repetition_lookup_table.get(digest, False):
        load_file_repetition_lookup_table.close()
        return make_response(
            jsonify({"message": "repeated upload"}),
            StatusCode.HTTP_409_CONFLICT
        )

    # 校验数据格式，对不规范的数据做自动校正，出现无法校正的情况直接报错退出
    is_valid, err_msg = do_intelligent_calibration_for_input_products(csv_file)
    if not is_valid:
        return make_response(
            jsonify({"message": "invalid data: {}".format(err_msg)}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    response_object = {"message": ""}
    # 用于检查是否有新增的SKU？是否是重复导入的SKU？
    add, exist = do_data_check_for_input_products(csv_file)
    response_object["items_total"] = add + exist
    response_object["items_add"] = add
    response_object["items_exist"] = exist
    # 如果没有新增SKU，直接返回
    if add > 0:
        current_app.logger.info("Insert {} SKUs into lookup_table_sku!!!".format(add))

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

        init_lookup_table_k_sku_v_boolean()
        init_lookup_table_k_sku_v_brand_c1_c2_is_combined()
        init_lookup_table_k_c1_v_c1_c2()
        init_lookup_table_k_brand_v_brand_c2()
        init_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name()

        load_file_repetition_lookup_table[digest] = True
    load_file_repetition_lookup_table.close()
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 获取所有商品条目的接口, 带有翻页功能
@product_blueprint.route("/", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@util_cost_count
def list_products():
    page_offset = request.args.get("page.offset", 0)
    page_limit = request.args.get("page.limit", 20)

    # TODO: 优化SQL
    stmt = "SELECT product_code, specification_code, product_name, specification_name, \
brand, classification_1, classification_2, product_series, stop_status, \
is_combined, is_import, supplier_name, purchase_name, jit_inventory, moq \
FROM fotolei_pssa.products ORDER BY specification_code LIMIT {}, {};".format(
        page_offset, page_limit)
    products = db_connector.query(stmt)

    if (type(products) is not list) or (type(products) is list and len(products) == 0):
        response_object = {"message": "not found", "products": []}
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_200_OK
        )
    response_object = {"message": "", "products": products}
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 获取总商品条目量的接口
@product_blueprint.route("/total", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@util_cost_count
def get_products_total():
    stmt = "SELECT SUM(total) FROM fotolei_pssa.product_summary;"
    ret = db_connector.query(stmt)
    response_object = {"message": "", "products_total": 0}
    if type(ret) is list and len(ret) > 0 and ret[0][0] is not None:
        response_object["products_total"] = ret[0][0]
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 更新一条商品条目的接口
@product_blueprint.route("/one/update", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def update_one_product():
    payload = request.get_json()
    id = payload["id"]

    specification_code = payload.get("specification_code", "").strip()
    product_code = payload.get("product_code", "").strip()
    product_name = payload.get("product_name", "").strip()
    specification_name = payload.get("specification_name", "").strip()
    brand = payload.get("brand", "").strip()
    classification_1 = payload.get("classification_1", "").strip()
    classification_2 = payload.get("classification_2", "").strip()
    product_series = payload.get("product_series", "").strip()
    stop_status = payload.get("stop_status", "全部").strip()
    product_weight = payload.get("product_weight", "")
    product_length = payload.get("product_length", "")
    product_width = payload.get("product_width", "")
    product_height = payload.get("product_height", "")
    is_combined = payload.get("is_combined", "全部").strip()
    be_aggregated = payload.get("be_aggregated", "全部").strip()
    is_import = payload.get("is_import", "全部").strip()
    supplier_name = payload.get("supplier_name", "").strip()
    purchase_name = payload.get("purchase_name", "").strip()
    jit_inventory = payload.get("jit_inventory", "")
    moq = payload.get("moq", "")

    stmt = "UPDATE fotolei_pssa.products SET "
    updates = []
    if len(specification_code) > 0:
        updates.append("specification_code = '{}'".format(specification_code))
    if len(product_code) > 0:
        updates.append("product_code = '{}'".format(product_code))
    if len(product_name) > 0:
        updates.append("product_name = '{}'".format(product_name))
    if len(specification_name) > 0:
        updates.append("specification_name = '{}'".format(specification_name))
    if len(brand) > 0:
        updates.append("brand = '{}'".format(brand))
    if len(classification_1) > 0:
        updates.append("classification_1 = '{}'".format(classification_1))
    if len(classification_2) > 0:
        updates.append("classification_2 = '{}'".format(classification_2))
    if len(product_series) > 0:
        updates.append("product_series = '{}'".format(product_series))
    if stop_status != '全部':
        updates.append("stop_status = '{}'".format(stop_status))
    if len(product_weight) > 0:
        updates.append("product_weight = '{}'".format(product_weight))
    if len(product_length) > 0:
        updates.append("product_length = '{}'".format(product_length))
    if len(product_width) > 0:
        updates.append("product_width = '{}'".format(product_width))
    if len(product_height) > 0:
        updates.append("product_height = '{}'".format(product_height))
    if is_combined != '全部':
        updates.append("is_combined = '{}'".format(is_combined))
    if be_aggregated != '全部':
        updates.append("be_aggregated = '{}'".format(be_aggregated))
    if is_import != '全部':
        updates.append("is_import = '{}'".format(is_import))
    if len(supplier_name) > 0:
        updates.append("supplier_name = '{}'".format(supplier_name))
    if len(purchase_name) > 0:
        updates.append("purchase_name = '{}'".format(purchase_name))
    if len(jit_inventory) > 0:
        updates.append("jit_inventory = '{}'".format(jit_inventory))
    if len(moq) > 0:
        updates.append("moq = '{}'".format(moq))
    stmt += ", ".join(updates)
    stmt += " WHERE id = '{}';".format(id)
    db_connector.update(stmt)

    return make_response(
        jsonify({"message": ""}),
        StatusCode.HTTP_200_OK
    )


# 获取一条商品条目的接口
@product_blueprint.route("/one/pick", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def pick_one_product():
    specification_code = request.args.get("specification_code")
    if not get_lookup_table_k_sku_v_boolean(specification_code):
        return make_response(
            jsonify({"message": "not found"}),
            StatusCode.HTTP_404_NOT_FOUND
        )

    stmt = "SELECT * FROM fotolei_pssa.products WHERE specification_code = '{}';".format(specification_code)
    products = db_connector.query(stmt)

    if len(products) == 0:
        response_object = {"message": "not found", "product": {}}
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_404_NOT_FOUND
        )

    response_object = {"message": ""}
    response_object["product"] = {
        "id": products[0][0],
        "product_code": products[0][1],
        "product_name": products[0][2],
        "specification_name": products[0][4],
        "brand": products[0][5],
        "classification_1": products[0][6],
        "classification_2": products[0][7],
        "product_series": products[0][8],
        "stop_status": products[0][9],
        "product_weight": "{}".format(products[0][10]),
        "product_length": "{}".format(products[0][11]),
        "product_width": "{}".format(products[0][12]),
        "product_height": "{}".format(products[0][13]),
        "is_combined": products[0][14],
        "be_aggregated": products[0][15],
        "is_import": products[0][16],
        "supplier_name": products[0][17],
        "purchase_name": products[0][18],
        "jit_inventory": "{}".format(products[0][19]),
        "moq": "{}".format(products[0][20]),
    }
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


# 删除所有商品条目的接口
@product_blueprint.route("/all/clean", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def clean_all_products():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.products;"
        db_connector.drop_table(stmt)
        stmt = "DROP TABLE IF EXISTS fotolei_pssa.product_summary;"
        db_connector.drop_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.products (
    id                 INT           NOT NULL AUTO_INCREMENT,
    product_code       VARCHAR(64),            /* 商品编码 */
    product_name       VARCHAR(128),           /* 商品名称 */
    specification_code VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name VARCHAR(128),           /* 规格名称 */
    brand              VARCHAR(64),            /* 品牌 */
    classification_1   VARCHAR(64),            /* 分类1 */
    classification_2   VARCHAR(64),            /* 分类2 */
    product_series     VARCHAR(64),            /* 产品系列 */
    stop_status        VARCHAR(32),            /* STOP状态 */
    product_weight     FLOAT,                  /* 重量/g */
    product_length     FLOAT,                  /* 长度/cm */
    product_width      FLOAT,                  /* 宽度/cm */
    product_height     FLOAT,                  /* 高度/cm */
    is_combined        VARCHAR(32),            /* 是否是组合商品 */
    be_aggregated      VARCHAR(32),            /* 是否参与统计 */
    is_import          VARCHAR(32),            /* 是否是进口商品 */
    supplier_name      VARCHAR(128),           /* 供应商名称 */
    purchase_name      VARCHAR(128),           /* 采购名称 */
    jit_inventory      INT,                    /* 实时可用库存 */
    moq                INT,                    /* 最小订货单元 */
    PRIMARY KEY (id),
    KEY products_specification_code (specification_code),
    KEY products_is_combined_product_series (is_combined, product_series),
    KEY products_is_combined_stop_status_be_aggregated_supplier_name (is_combined, stop_status, be_aggregated, supplier_name)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        stmt = '''
CREATE TABLE IF NOT EXISTS fotolei_pssa.product_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
'''
        db_connector.create_table(stmt)
        if platform.system() == "Linux":
            util_silent_remove("{}/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table".format(
                os.path.expanduser("~")))
        else:
            util_silent_remove("{}/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table.db".format(
                os.path.expanduser("~")))

        clean_lookup_table_k_sku_v_boolean()
        clean_lookup_table_k_sku_v_brand_c1_c2_is_combined()
        clean_lookup_table_k_c1_v_c1_c2()
        clean_lookup_table_k_brand_v_brand_c2()
        clean_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name()

        return make_response(
            jsonify({"message": ""}),
            StatusCode.HTTP_200_OK
        )
    else:
        return make_response(
            jsonify({"message": ""}),
            StatusCode.HTTP_403_FORBIDDEN
        )


# 删除单条商品条目的接口
@product_blueprint.route("/one/clean", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@util_cost_count
def clean_one_product():
    payload = request.get_json()
    admin_usr = payload.get("admin_usr", "").strip()
    admin_pwd = payload.get("admin_pwd", "").strip()
    specification_code = payload.get("specification_code", "").strip()
    if admin_usr == "fotolei" and admin_pwd == "asdf5678":
        stmt = "DELETE FROM fotolei_pssa.products WHERE specification_code = '{}';".format(specification_code)
        db_connector.delete(stmt)
        return make_response(
            jsonify({"message": ""}),
            StatusCode.HTTP_200_OK
        )
    else:
        return make_response(
            jsonify({"message": ""}),
            StatusCode.HTTP_403_FORBIDDEN
        )


# 预下载"新增SKU数据表"的接口
@product_blueprint.route("/addedskus/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
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

    response_object = {"message": ""}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256

    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


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
                        current_app.logger.error("invalid 'STOP状态': {}".format(new_row[8]))
                        break
                if new_row[13] != "是" and new_row[13] != "否":
                    if len(new_row[13]) == 0 or new_row[13] == "0":
                        new_row[13] = "否"
                    elif new_row[13] == "1":
                        new_row[13] = "是"
                    else:
                        is_valid = False
                        err_msg = "'组合商品'数据存在非法输入，出现在第{}行。".format(line + 1)
                        current_app.logger.error("invalid '组合商品': {}".format(new_row[13]))
                        break
                if new_row[14] != "参与" and new_row[14] != "不参与":
                    if len(new_row[14]) == 0 or new_row[14] == "0":
                        new_row[14] = "不参与"
                    elif new_row[14] == "1":
                        new_row[14] = "参与"
                    else:
                        is_valid = False
                        err_msg = "'参与统计'数据存在非法输入，出现在第{}行。".format(line + 1)
                        current_app.logger.error("invalid '参与统计': {}".format(new_row[14]))
                        break
                if new_row[15] != "进口品" and new_row[15] != "非进口品":
                    if len(new_row[15]) == 0 or new_row[15] == "0":
                        new_row[15] = "非进口品"
                    elif new_row[15] == "1":
                        new_row[15] = "进口品"
                    else:
                        is_valid = False
                        err_msg = "'进口商品'数据存在非法输入，出现在第{}行。".format(line + 1)
                        current_app.logger.error("invalid '进口商品': {}".format(new_row[15]))
                        break
                if len(new_row[9]) == 0:
                    new_row[9] = "0"
                elif REG_INT_AND_FLOAT.match(new_row[9]) is None:
                    is_valid = False
                    err_msg = "'重量'数据存在非法输入，出现在第{}行。".format(line + 1)
                    current_app.logger.error("invalid '重量': {}".format(new_row[9]))
                    break
                if len(new_row[10]) == 0:
                    new_row[10] = "0"
                elif REG_INT_AND_FLOAT.match(new_row[10]) is None:
                    is_valid = False
                    err_msg = "'长度'数据存在非法输入，出现在第{}行。".format(line + 1)
                    current_app.logger.error("invalid '长度': {}".format(new_row[10]))
                    break
                if len(new_row[11]) == 0:
                    new_row[11] = "0"
                elif REG_INT_AND_FLOAT.match(new_row[11]) is None:
                    is_valid = False
                    err_msg = "'宽度'数据存在非法输入，出现在第{}行。".format(line + 1)
                    current_app.logger.error("invalid '宽度': {}".format(new_row[11]))
                    break
                if len(new_row[12]) == 0:
                    new_row[12] = "0"
                elif REG_INT_AND_FLOAT.match(new_row[12]) is None:
                    is_valid = False
                    err_msg = "'高度'数据存在非法输入，出现在第{}行。".format(line + 1)
                    current_app.logger.error("invalid '高度': {}".format(new_row[12]))
                    break
                if len(new_row[18]) == 0:
                    new_row[18] = "0"
                elif REG_INT.match(new_row[18]) is None:
                    is_valid = False
                    err_msg = "'实时可用库存'数据存在非法输入，出现在第{}行。".format(line + 1)
                    current_app.logger.error("invalid '实时可用库存': {}".format(new_row[18]))
                    break
                if len(new_row[19]) == 0:
                    new_row[19] = "1"
                elif REG_POSITIVE_INT.match(new_row[19]) is None:
                    is_valid = False
                    err_msg = "'最小订货单元'数据存在非法输入，出现在第{}行。".format(line + 1)
                    current_app.logger.error("invalid '最小订货单元': {}".format(new_row[19]))
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
                if get_lookup_table_k_sku_v_boolean(row[1]):
                    exist += 1
                else:
                    put_lookup_table_k_sku_v_boolean(row[1], True)
                    csv_writer.writerow(row)
            else:
                csv_writer.writerow(row)
            line += 1

    fw.close()
    shutil.move(csv_file + ".tmp", csv_file)
    return total - exist, exist
