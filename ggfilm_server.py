# -*- coding: utf-8 -*-
import atexit
import csv
import datetime
import hashlib
import logging
import pendulum
import os
import shelve
import shutil
import sys
import time
from collections import defaultdict
sys.path.append(os.path.abspath("./db"))
from db.mysqlcli import MySQLConnector
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SKU_LOOKUP_TABLE = defaultdict(bool)
DBConnector = MySQLConnector.instance()
DBConnector.init_conn("ggfilm")
_stmt = "SELECT specification_code FROM ggfilm.products;"
_rets = DBConnector.query(_stmt)
if type(_rets) is list and len(_rets) > 0:
    for ret in _rets:
        SKU_LOOKUP_TABLE[ret[0]] = True
    logger.info("Insert {} SKUs into SKU_LOOKUP_TABLE!!!".format(len(SKU_LOOKUP_TABLE)))

ggfilm_server = Flask(__name__)
ggfilm_server.config.from_object(__name__)
CORS(ggfilm_server, resources={r"/api/*": {"origins": "*"}})


# 探活接口
@ggfilm_server.route("/api/v1/keepalive", methods=["GET"])
def keepalive():
    return jsonify("alive")


# 载入"商品数据报表"的接口
@ggfilm_server.route("/api/v1/products/upload", methods=["POST"])
def upload_products():
    csv_files = request.files.getlist("file")
    csv_file_sha256 = generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/ggfilm-server/products/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    if not do_data_schema_validation_for_input_products(csv_file):
        response_object = {"status": "invalid input data schema"}
    else:
        RepetitionLookupTable = shelve.open("repetiation_lookup_table", flag='c', writeback=False)
        file_digest = generate_file_digest(csv_file)
        if not RepetitionLookupTable.get(file_digest, False):
            RepetitionLookupTable[file_digest] = True

            do_intelligent_calibration_for_input_products(csv_file)

            DBConnector.load_data_infile(
                """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
                "INTO TABLE ggfilm.products " +
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

            stmt = "SELECT specification_code FROM ggfilm.products;"
            rets = DBConnector.query(stmt)
            SKU_LOOKUP_TABLE.clear()
            for ret in rets:
                SKU_LOOKUP_TABLE[ret[0]] = True
            logger.info("Insert {} SKUs into SKU_LOOKUP_TABLE!!!".format(len(SKU_LOOKUP_TABLE)))

            with open(csv_file, "r", encoding='utf-8-sig') as fd:
                csv_reader = csv.reader(fd, delimiter=",")
                for _ in csv_reader:
                    pass
                stmt = "INSERT INTO ggfilm.product_summary (total) VALUES (%s);"
                DBConnector.insert(stmt, (csv_reader.line_num - 1,))

            response_object = {"status": "success"}
        else:
            response_object = {"status": "repetition"}
        RepetitionLookupTable.close()
    return jsonify(response_object)


# 载入"实时可用库存报表"的接口
@ggfilm_server.route("/api/v1/jitinventory/upload", methods=["POST"])
def upload_jit_inventory_data():
    csv_files = request.files.getlist("file")
    csv_file = "{}/ggfilm-server/jit_inventory/{}_{}".format(
        os.path.expanduser("~"), int(time.time()), csv_files[0].filename
    )
    csv_files[0].save(csv_file)

    sku_inventory_tuple_list = []
    not_inserted_sku_list = []
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        line = 0
        for row in csv_reader:
            if line > 0:
                line += 1
                if not SKU_LOOKUP_TABLE.get(row[0], False):
                    not_inserted_sku_list.append(row[0])
                else:
                    sku_inventory_tuple_list.append((row[1], row[0]))
            line += 1

    stmt = "UPDATE ggfilm.products SET jit_inventory = %s WHERE specification_code = %s;"
    DBConnector.batch_update(stmt, sku_inventory_tuple_list)

    response_object = {"status": "success"}
    if len(not_inserted_sku_list) > 0:
        logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))
        # 新增sku，需要向用户展示
        response_object["added_skus"] = not_inserted_sku_list
    else:
        response_object["added_skus"] = []
    return jsonify(response_object)


# 预下载"新增SKU数据表"的接口
@ggfilm_server.route("/api/v1/addedskus/prepare", methods=["POST"])
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


# 载入"库存数据报表"的接口
@ggfilm_server.route("/api/v1/inventories/upload", methods=["POST"])
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
        RepetitionLookupTable = shelve.open("repetiation_lookup_table", flag='c', writeback=False)
        file_digest = generate_file_digest(csv_file)
        if not RepetitionLookupTable.get(file_digest, False):
            not_inserted_sku_list = []
            with open(csv_file, "r", encoding='utf-8-sig') as fd:
                csv_reader = csv.reader(fd, delimiter=",")
                line = 0
                for row in csv_reader:
                    if line > 0:
                        if not SKU_LOOKUP_TABLE.get(row[2], False):
                            not_inserted_sku_list.append(row[2])
                    line += 1
            if len(not_inserted_sku_list) > 0:
                logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))
                response_object = {"status": "new SKUs"}
                response_object["added_skus"] = not_inserted_sku_list
            else:
                RepetitionLookupTable[file_digest] = True

                do_intelligent_calibration_for_input_inventories(csv_file)

                if len(import_date) == 0:
                    today = pendulum.today()
                    last_month = today.subtract(months=1)
                    import_date = last_month.strftime('%Y-%m')
                add_date_for_input_inventories(csv_file, import_date.strip())

                DBConnector.load_data_infile(
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
                    "ed_inventory_qty, ed_inventory_total);"
                )

                response_object = {"status": "success"}
        else:
            response_object = {"status": "repetition"}
        RepetitionLookupTable.close()
    return jsonify(response_object)


# 获取总商品量的接口
@ggfilm_server.route("/api/v1/products/total", methods=["GET"])
def get_products_total():
    stmt = "SELECT SUM(total) FROM ggfilm.product_summary;"
    ret = DBConnector.query(stmt)
    response_object = {"status": "success"}
    if type(ret) is list and len(ret) > 0:
        response_object["products_total"] = ret[0][0]
    else:
        response_object["products_total"] = "0"
    return jsonify(response_object)


# 获取所有商品的接口, 带有翻页功能
@ggfilm_server.route("/api/v1/products", methods=["GET"])
def list_products():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT product_code, specification_code, product_name, specification_name, \
brand, classification_1, classification_2, product_series, stop_status, \
is_combined, is_import, supplier_name, purchase_name, jit_inventory, moq \
FROM ggfilm.products ORDER BY 'id' DESC LIMIT {}, {};".format(
        page_offset, page_limit)
    products = DBConnector.query(stmt)

    response_object = {"status": "success"}
    if (products) == 0:
        response_object = {"status": "not found"}
        response_object["products"] = []
    else:
        response_object["products"] = products
    return jsonify(response_object)


# 获取所有库存的接口, 带有翻页功能
@ggfilm_server.route("/api/v1/inventories", methods=["GET"])
def list_inventories():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT specification_code, \
st_inventory_qty, purchase_qty, purchase_then_return_qty, sale_qty, \
sale_then_return_qty, others_qty, ed_inventory_qty, create_time \
FROM ggfilm.inventories ORDER BY 'id' DESC LIMIT {}, {};".format(
        page_offset, page_limit)
    inventories = DBConnector.query(stmt)

    response_object = {"status": "success"}
    if (inventories) == 0:
        response_object = {"status": "not found"}
        response_object["inventories"] = []
    else:
        response_object["inventories"] = inventories
    return jsonify(response_object)


# 导出所有可供选择的选项列表的接口
@ggfilm_server.route("/api/v1/alloptions", methods=["GET"])
def list_all_options():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT brand FROM ggfilm.products;"
    brand_options = DBConnector.query(stmt)
    if (brand_options) == 0:
        response_object["brand_options"] = []
    else:
        response_object["brand_options"] = [{"id": i, "brand": brand[0]} for i, brand in enumerate(brand_options)]

    stmt = "SELECT DISTINCT classification_1 FROM ggfilm.products;"
    classification_1_options = DBConnector.query(stmt)
    if (classification_1_options) == 0:
        response_object["classification_1_options"] = []
    else:
        response_object["classification_1_options"] = [{"id": i, "classification-1": classification_1[0]} for i, classification_1 in enumerate(classification_1_options)]

    stmt = "SELECT DISTINCT classification_2 FROM ggfilm.products;"
    classification_2_options = DBConnector.query(stmt)
    if (classification_2_options) == 0:
        response_object["classification_2_options"] = []
    else:
        response_object["classification_2_options"] = [{"id": i, "classification-2": classification_2[0]} for i, classification_2 in enumerate(classification_2_options)]

    stmt = "SELECT DISTINCT product_series FROM ggfilm.products;"
    product_series_options = DBConnector.query(stmt)
    if (product_series_options) == 0:
        response_object["product_series_options"] = []
    else:
        response_object["product_series_options"] = [{"id": i, "product-series": product_series[0]} for i, product_series in enumerate(product_series_options)]

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_options = DBConnector.query(stmt)
    if (supplier_name_options) == 0:
        response_object["supplier_name_options"] = []
    else:
        response_object["supplier_name_options"] = [{"id": i, "supplier-name": supplier_name[0]} for i, supplier_name in enumerate(supplier_name_options)]

    return jsonify(response_object)


# 导出所有可供选择的选项列表的接口
@ggfilm_server.route("/api/v1/allselections", methods=["GET"])
def list_all_selections():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT brand FROM ggfilm.products;"
    brand_selections = DBConnector.query(stmt)
    if (brand_selections) == 0:
        response_object["brand_selections"] = []
    else:
        response_object["brand_selections"] = [
            {"value": brand[0], "text": brand[0]} \
                for brand in brand_selections \
                    if len(brand[0].strip()) > 0
        ]

    stmt = "SELECT DISTINCT classification_1 FROM ggfilm.products;"
    classification_1_selections = DBConnector.query(stmt)
    if (classification_1_selections) == 0:
        response_object["classification_1_selections"] = []
    else:
        response_object["classification_1_selections"] = [
            {"value": classification_1_selection[0], "text": classification_1_selection[0]} \
                for classification_1_selection in classification_1_selections \
                    if len(classification_1_selection[0].strip()) > 0
        ]

    stmt = "SELECT DISTINCT classification_2 FROM ggfilm.products;"
    classification_2_selections = DBConnector.query(stmt)
    if (classification_2_selections) == 0:
        response_object["classification_2_selections"] = []
    else:
        response_object["classification_2_selections"] = [
            {"value": classification_2_selection[0], "text": classification_2_selection[0]} \
                for classification_2_selection in classification_2_selections \
                    if len(classification_2_selection[0].strip()) > 0
        ]

    stmt = "SELECT DISTINCT product_series FROM ggfilm.products;"
    product_series_selections = DBConnector.query(stmt)
    if (product_series_selections) == 0:
        response_object["product_series_selections"] = []
    else:
        response_object["product_series_selections"] = [
            {"value": product_series_selection[0], "text": product_series_selection[0]} \
                for product_series_selection in product_series_selections \
                    if len(product_series_selection[0].strip()) > 0
        ]

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_selections = DBConnector.query(stmt)
    if (supplier_name_selections) == 0:
        response_object["supplier_name_selections"] = []
    else:
        response_object["supplier_name_selections"] = [
            {"value": supplier_name_selection[0], "text": supplier_name_selection[0]} \
                for supplier_name_selection in supplier_name_selections \
                    if len(supplier_name_selection[0].strip()) > 0
        ]

    return jsonify(response_object)


# 导出所有可供选择的供应商列表的接口
@ggfilm_server.route("/api/v1/allselections/suppliers", methods=["GET"])
def list_all_supplier_selections():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_selections = DBConnector.query(stmt)
    if (supplier_name_selections) == 0:
        response_object["supplier_name_selections"] = []
    else:
        response_object["supplier_name_selections"] = [
            {"value": supplier_name_selection[0], "text": supplier_name_selection[0]} \
                for supplier_name_selection in supplier_name_selections \
                    if len(supplier_name_selection[0].strip()) > 0
        ]

    return jsonify(response_object)


# 导出销售报表（按分类汇总）的接口
@ggfilm_server.route("/api/v1/case1/download", methods=["POST"])
def export_report_file_case1():
    return jsonify("导出销售报表（按分类汇总）")


# 预下载"销售报表（按系列汇总）"的接口
@ggfilm_server.route("/api/v1/case2/prepare", methods=["POST"])
def prepare_report_file_case2():
    payload = request.get_json()
    # 1. 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    # 2. 按照“产品系列”进行分类汇总，没有系列名称的不参与汇总
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        response_object = {"status": "not found"}
        return jsonify(response_object)

    stmt = "SELECT specification_code, product_series, jit_inventory FROM ggfilm.products \
WHERE COALESCE(CHAR_LENGTH(product_series), 0) != 0;"
    rets = DBConnector.query(stmt)

    if type(rets) is list and len(rets) > 0:
        lookup_table = {}  # product_series -> [(specification_code, jit_inventory)]
        for ret in rets:
            if ret[1] in lookup_table.keys():
                lookup_table[ret[1]].append((ret[0], ret[2]))
            else:
                lookup_table[ret[1]] = [(ret[0], ret[2])]
        cache = {}
        for k, v in lookup_table.items():
            product_series = k
            cache[product_series] = {
                "st_inventory_qty": 0,
                "st_inventory_total": 0,
                "purchase_qty": 0,
                "purchase_total": 0,
                "purchase_then_return_qty": 0,
                "purchase_then_return_total": 0,
                "sale_qty": 0,
                "sale_total": 0,
                "sale_then_return_qty": 0,
                "sale_then_return_total": 0,
                "others_qty": 0,
                "others_total": 0,
                "ed_inventory_qty": 0,
                "ed_inventory_total": 0,
                "jit_inventory": 0,
            }
            for vv in v:
                specification_code = vv[0]
                jit_inventory = vv[1]
                cache[product_series]["jit_inventory"] += jit_inventory

                stmt = "SELECT * FROM ggfilm.inventories \
WHERE specification_code = '{}' AND \
create_time >= '{}' AND \
create_time <= '{}';".format(specification_code, st_date, ed_date)
                inner_rets = DBConnector.query(stmt)
                if type(inner_rets) is list and len(inner_rets) > 0:
                    cache[product_series]["st_inventory_qty"] += inner_rets[0][5]
                    cache[product_series]["st_inventory_total"] += inner_rets[0][6]
                    cache[product_series]["ed_inventory_qty"] += inner_rets[len(inner_rets) - 1][17]
                    cache[product_series]["ed_inventory_total"] += inner_rets[len(inner_rets) - 1][18]
                    purchase_qty = 0
                    for inner_ret in inner_rets:
                        purchase_qty += inner_ret[7]
                    cache[product_series]["purchase_qty"] += purchase_qty
                    purchase_total = 0
                    for inner_ret in inner_rets:
                        purchase_total += inner_ret[8]
                    cache[product_series]["purchase_total"] += purchase_total
                    purchase_then_return_qty = 0
                    for inner_ret in inner_rets:
                        purchase_then_return_qty += inner_ret[9]
                    cache[product_series]["purchase_then_return_qty"] += purchase_then_return_qty
                    purchase_then_return_total = 0
                    for inner_ret in inner_rets:
                        purchase_then_return_total += inner_ret[10]
                    cache[product_series]["purchase_then_return_total"] += purchase_then_return_total
                    sale_qty = 0
                    for inner_ret in inner_rets:
                        sale_qty += inner_ret[11]
                    cache[product_series]["sale_qty"] += sale_qty
                    sale_total = 0
                    for inner_ret in inner_rets:
                        sale_total += inner_ret[12]
                    cache[product_series]["sale_total"] += sale_total
                    sale_then_return_qty = 0
                    for inner_ret in inner_rets:
                        sale_then_return_qty += inner_ret[13]
                    cache[product_series]["sale_then_return_qty"] += sale_then_return_qty
                    sale_then_return_total = 0
                    for inner_ret in inner_rets:
                        sale_then_return_total += inner_ret[14]
                    cache[product_series]["sale_then_return_total"] += sale_then_return_total
                    others_qty = 0
                    for inner_ret in inner_rets:
                        others_qty += inner_ret[15]
                    cache[product_series]["others_qty"] += others_qty
                    others_total = 0
                    for inner_ret in inner_rets:
                        others_total += inner_ret[16]
                    cache[product_series]["others_total"] += others_total

        ts = int(time.time())
        csv_file_sha256 = generate_digest("销售报表（按系列汇总）_{}.csv".format(ts))
        csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
        output_file = "销售报表（按系列汇总）_{}.csv".format(ts)
        with open(csv_file, "w", encoding='utf-8-sig') as fd:
            csv_writer = csv.writer(fd, delimiter=",")
            csv_writer.writerow([
                "产品系列", "起始库存数量", "起始库存总额", "采购数量",
                "采购总额", "采购退货数量", "采购退货总额", "销售数量",
                "销售总额", "销售退货数量", "销售退货总额", "其他变更数量",
                "其他变更总额", "截止库存数量", "截止库存总额", "实时可用库存",
            ])

            for k, v in cache.items():
                csv_writer.writerow([
                    k,
                    v["st_inventory_qty"], v["st_inventory_total"],
                    v["purchase_qty"], v["purchase_total"],
                    v["purchase_then_return_qty"], v["purchase_then_return_total"],
                    v["sale_qty"], v["sale_total"],
                    v["sale_then_return_qty"], v["sale_then_return_total"],
                    v["others_qty"], v["others_total"],
                    v["ed_inventory_qty"], v["ed_inventory_total"],
                    v["jit_inventory"],
                ])

        response_object = {"status": "success"}
        response_object["output_file"] = output_file
        response_object["server_send_queue_file"] = csv_file_sha256
        return jsonify(response_object)
    else:
        response_object = {"status": "not found"}
        return jsonify(response_object)


# TODO: fix me
'''
预览效果

商品编号 | 规格编号	| 商品名称 | 规格名称 | 起始库存数量 | 采购数量	| 销售数量 | 截止库存数量 | 实时可用库存

其中
* 起始库存数量 = 时间段内第一个月的数量
* 采购数量 = 时间段内每一个月的数量的累加
* 销售数量 = 时间段内每一个月的数量的累加
* 截止库存数量 = 时间段内最后一个月的数量
'''
# 预览"销售报表（按单个SKU汇总）"的接口
@ggfilm_server.route("/api/v1/case3/preview", methods=["POST"])
def preview_report_file_case3():
    payload = request.get_json()
    # 1. 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    # 2.1. 如果specification_code（规格编号）不为空，直接用规格编号筛选出想要的数据
    # 2.2. 如果specification_code（规格编号）为空，则先用其他非空条件筛选出规格编号，再用规格编号筛选出想要的数据
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        response_object = {"status": "not found"}
        return jsonify(response_object)

    specification_code = payload.get("specification_code", "").strip()

    def inline():
        resp = {"status": "success"}
        stmt = "SELECT product_code, specification_code, \
product_name, specification_name, \
st_inventory_qty, purchase_qty, \
sale_qty, ed_inventory_qty, create_time \
FROM ggfilm.inventories \
WHERE specification_code = '{}' AND \
create_time >= '{}' AND \
create_time <= '{}' \
ORDER BY create_time ASC;".format(
            specification_code, st_date, ed_date
        )
        rets = DBConnector.query(stmt)
        if type(rets) is list and len(rets) > 0:
            resp["st_date"] = st_date
            resp["ed_date"] = ed_date
            resp["product_code"] = rets[0][0]
            resp["specification_code"] = rets[0][1]
            resp["product_name"] = rets[0][2]
            resp["specification_name"] = rets[0][3]
            resp["st_inventory_qty"] = rets[0][4]
            resp["ed_inventory_qty"] = rets[len(rets) - 1][7]
            purchase_qty = 0
            for ret in rets:
                purchase_qty += ret[5]
            resp["purchase_qty"] = purchase_qty
            sale_qty = 0
            for ret in rets:
                sale_qty += ret[6]
            resp["sale_qty"] = sale_qty

            stmt = "SELECT jit_inventory FROM ggfilm.products WHERE specification_code = '{}';".format(specification_code)
            rets = DBConnector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                resp["jit_inventory"] = rets[0][0]
            else:
                resp["jit_inventory"] = 0
        else:
            resp = {"status": "not found"}
        return resp

    if len(specification_code) > 0:
        response_object = inline()
        return jsonify(response_object)
    else:
        product_code = payload.get("product_code", "").strip()
        product_name = payload.get("product_name", "").strip()
        brand = payload.get("brand", "").strip()
        classification_1 = payload.get("classification_1", "").strip()
        classification_2 = payload.get("classification_2", "").strip()
        product_series = payload.get("product_series", "").strip()
        stop_status = payload.get("stop_status", "在用").strip()
        is_combined = payload.get("is_combined", "否").strip()
        be_aggregated = payload.get("be_aggregated", "参与").strip()
        is_import = payload.get("is_import", "非进口品").strip()
        supplier_name = payload.get("supplier_name", "").strip()

        stmt = "SELECT specification_code FROM ggfilm.products WHERE "
        selections = []
        if len(product_code) > 0:
            selections.append("product_code = '{}'".format(product_code))
        if len(product_name) > 0:
            selections.append("product_name = '{}'".format(product_name))
        if len(brand) > 0:
            selections.append("brand = '{}'".format(brand))
        if len(classification_1) > 0:
            selections.append("classification_1 = '{}'".format(classification_1))
        if len(classification_2) > 0:
            selections.append("classification_2 = '{}'".format(classification_2))
        if len(product_series) > 0:
            selections.append("product_series = '{}'".format(product_series))
        if stop_status != '全部':
            selections.append("stop_status = '{}'".format(stop_status))
        if is_combined != '全部':
            selections.append("is_combined = '{}'".format(is_combined))
        if be_aggregated != '全部':
            selections.append("be_aggregated = '{}'".format(be_aggregated))
        if is_import != '全部':
            selections.append("is_import = '{}'".format(is_import))
        if len(supplier_name) > 0:
            selections.append("supplier_name = '{}'".format(supplier_name))
        stmt += " AND ".join(selections)
        stmt += ";"
        rets = DBConnector.query(stmt)
        if type(rets) is list and len(rets) > 0:
            specification_code = rets[0][0]
            response_object = inline()
            return jsonify(response_object)
        else:
            response_object = {"status": "not found"}
            return jsonify(response_object)


# 预下载"销售报表（按单个SKU汇总）"的接口
@ggfilm_server.route("/api/v1/case3/prepare", methods=["POST"])
def prepare_report_file_case3():
    payload = request.get_json()
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        response_object = {"status": "not found"}
        return jsonify(response_object)

    specification_code = payload.get("specification_code", "").strip()

    stmt = "SELECT * FROM ggfilm.products WHERE specification_code = '{}';".format(specification_code)
    rets = DBConnector.query(stmt)
    cache = {}
    cache["product_code"] = rets[0][1]
    cache["product_name"] = rets[0][2]
    cache["specification_code"] = rets[0][3]
    cache["specification_name"] = rets[0][4]
    cache["brand"] = rets[0][5]
    cache["classification_1"] = rets[0][6]
    cache["classification_2"] = rets[0][7]
    cache["product_series"] = rets[0][8]
    cache["stop_status"] = rets[0][9]
    cache["product_weight"] = rets[0][10]
    cache["product_length"] = rets[0][11]
    cache["product_width"] = rets[0][12]
    cache["product_height"] = rets[0][13]
    cache["is_combined"] = rets[0][14]
    cache["is_import"] = rets[0][16]
    cache["supplier_name"] = rets[0][17]
    cache["purchase_name"] = rets[0][18]
    cache["jit_inventory"] = rets[0][19]

    stmt = "SELECT * FROM ggfilm.inventories \
WHERE specification_code = '{}' AND \
create_time >= '{}' AND \
create_time <= '{}' \
ORDER BY create_time ASC;".format(
        specification_code, st_date, ed_date
    )
    rets = DBConnector.query(stmt)
    cache["st_inventory_qty"] = rets[0][5]
    cache["st_inventory_total"] = rets[0][6]
    cache["ed_inventory_qty"] = rets[len(rets) - 1][17]
    cache["ed_inventory_total"] = rets[len(rets) - 1][18]
    purchase_qty = 0
    for ret in rets:
        purchase_qty += ret[7]
    cache["purchase_qty"] = purchase_qty
    purchase_total = 0
    for ret in rets:
        purchase_total += ret[8]
    cache["purchase_total"] = purchase_total
    purchase_then_return_qty = 0
    for ret in rets:
        purchase_then_return_qty += ret[9]
    cache["purchase_then_return_qty"] = purchase_then_return_qty
    purchase_then_return_total = 0
    for ret in rets:
        purchase_then_return_total += ret[10]
    cache["purchase_then_return_total"] = purchase_then_return_total
    sale_qty = 0
    for ret in rets:
        sale_qty += ret[11]
    cache["sale_qty"] = sale_qty
    sale_total = 0
    for ret in rets:
        sale_total += ret[12]
    cache["sale_total"] = sale_total
    sale_then_return_qty = 0
    for ret in rets:
        sale_then_return_qty += ret[13]
    cache["sale_then_return_qty"] = sale_then_return_qty
    sale_then_return_total = 0
    for ret in rets:
        sale_then_return_total += ret[14]
    cache["sale_then_return_total"] = sale_then_return_total
    others_qty = 0
    for ret in rets:
        others_qty += ret[15]
    cache["others_qty"] = others_qty
    others_total = 0
    for ret in rets:
        others_total += ret[16]
    cache["others_total"] = others_total

    ts = int(time.time())
    csv_file_sha256 = generate_digest("销售报表（按单个SKU汇总）_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "销售报表（按单个SKU汇总）_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "商品编号", "规格编号", "商品名称", "规格名称",
            "品牌", "分类1", "分类2", "产品系列",
            "STOP状态", "重量/g", "长度/cm", "宽度/cm", "高度/cm",
            "组合商品", "进口商品", "供应商名称", "采购名称",
            "起始库存数量", "起始库存总额", "采购数量", "采购总额",
            "采购退货数量", "采购退货总额", "销售数量", "销售总额",
            "销售退货数量", "销售退货总额", "其他变更数量", "其他变更总额",
            "截止库存数量", "截止库存总额", "实时可用库存",
        ])
        csv_writer.writerow([
            cache["product_code"], cache["specification_code"], cache["product_name"], cache["specification_name"],
            cache["brand"], cache["classification_1"], cache["classification_2"], cache["product_series"],
            cache["stop_status"], cache["product_weight"], cache["product_length"], cache["product_width"], cache["product_height"],
            cache["is_combined"], cache["is_import"], cache["supplier_name"], cache["purchase_name"],
            cache["st_inventory_qty"], cache["st_inventory_total"], cache["purchase_qty"], cache["purchase_total"],
            cache["purchase_then_return_qty"], cache["purchase_then_return_total"], cache["sale_qty"], cache["sale_total"],
            cache["sale_then_return_qty"], cache["sale_then_return_total"], cache["others_qty"], cache["others_total"],
            cache["ed_inventory_qty"], cache["ed_inventory_total"], cache["jit_inventory"],
        ])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)


'''
预览效果

商品编号 | 规格编号	| 商品名称 | 规格名称 | 起始库存数量 | 采购数量	| 销售数量 | 截止库存数量 | 实时可用库存 | 库销比

其中
* 起始库存数量 = 时间段内第一个月的数量
* 采购数量 = 时间段内每一个月的数量的累加
* 销售数量 = 时间段内每一个月的数量的累加
* 截止库存数量 = 时间段内最后一个月的数量
'''
# 预览"滞销品报表"的接口
@ggfilm_server.route("/api/v1/case4/preview", methods=["POST"])
def export_report_file_case4():
    payload = request.get_json()
    # 1. 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    # 2. 先用其他非空条件筛选出规格编号，再用规格编号筛选出想要的数据
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        response_object = {"status": "not found"}
        return jsonify(response_object)

    st_datetime = datetime.datetime.strptime(st_date, "%Y-%m").date()
    ed_datetime = datetime.datetime.strptime(ed_date, "%Y-%m").date()
    time_quantum_x = 0
    if ed_datetime.month - st_datetime.month < 0:
        time_quantum_x = ed_datetime.month - st_datetime.month + 12
    else:
        time_quantum_x = ed_datetime.month - st_datetime.month

    brand = payload.get("brand", "").strip()
    classification_1 = payload.get("classification_1", "").strip()
    classification_2 = payload.get("classification_2", "").strip()
    product_series = payload.get("product_series", "").strip()
    stop_status = payload.get("stop_status", "在用").strip()
    is_combined = payload.get("is_combined", "否").strip()
    be_aggregated = payload.get("be_aggregated", "参与").strip()
    is_import = payload.get("is_import", "全部").strip()
    supplier_name = payload.get("supplier_name", "").strip()
    threshold_ssr = int(payload.get("threshold_ssr", "4"))
    reduced_btn_option = payload.get("reduced_btn_option", "open")

    stmt = "SELECT * FROM ggfilm.products WHERE "
    selections = []
    if len(brand) > 0:
        selections.append("brand = '{}'".format(brand))
    if len(classification_1) > 0:
        selections.append("classification_1 = '{}'".format(classification_1))
    if len(classification_2) > 0:
        selections.append("classification_2 = '{}'".format(classification_2))
    if len(product_series) > 0:
        selections.append("product_series = '{}'".format(product_series))
    if stop_status != '全部':
        selections.append("stop_status = '{}'".format(stop_status))
    if is_combined != '全部':
        selections.append("is_combined = '{}'".format(is_combined))
    if be_aggregated != '全部':
        selections.append("be_aggregated = '{}'".format(be_aggregated))
    if is_import != '全部':
        selections.append("is_import = '{}'".format(is_import))
    if len(supplier_name) > 0:
        selections.append("supplier_name = '{}'".format(supplier_name))
    stmt += " AND ".join(selections)
    stmt += ";"

    preview_table = []

    rets = DBConnector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            specification_code = ret[3]
            jit_inventory = ret[19]

            stmt = "SELECT * FROM ggfilm.inventories \
WHERE specification_code = '{}' AND \
create_time >= '{}' AND \
create_time <= '{}' \
ORDER BY create_time ASC;".format(
                specification_code, st_date, ed_date
            )
            inner_rets = DBConnector.query(stmt)
            if type(inner_rets) is list and len(inner_rets) > 0:
                sale_qty_x_months = 0
                for inner_ret in inner_rets:
                    sale_qty_x_months += inner_ret[11]
                if reduced_btn_option == "open":
                    reduced_months = 0
                    for inner_ret in inner_rets:
                        if inner_ret[5] == 0 and inner_ret[17] == 0:
                            if inner_ret[7] <= 10 and inner_ret[7] <= inner_ret[11]:
                                reduced_months += 1
                            elif inner_ret[7] > 10 and inner_ret[7] > inner_ret[11]:
                                reduced_months += 1
                    if time_quantum_x != reduced_months:
                        sale_qty_x_months = int(sale_qty_x_months * (time_quantum_x / (time_quantum_x - reduced_months)))

                if (sale_qty_x_months > 0 and (jit_inventory / sale_qty_x_months) > threshold_ssr) or \
                        (sale_qty_x_months == 0 and jit_inventory > 0):
                    # 滞销了
                    cache = {}
                    cache["product_code"] = inner_rets[0][1]
                    cache["specification_code"] = inner_rets[0][3]
                    cache["product_name"] = inner_rets[0][2]
                    cache["specification_name"] = inner_rets[0][4]
                    cache["brand"] = ret[5]
                    cache["classification_1"] = ret[6]
                    cache["classification_2"] = ret[7]
                    cache["product_series"] = ret[8]
                    cache["stop_status"] = ret[9]
                    cache["product_weight"] = ret[10]
                    cache["product_length"] = ret[11]
                    cache["product_width"] = ret[12]
                    cache["product_height"] = ret[13]
                    cache["is_combined"] = ret[14]
                    cache["is_import"] = ret[16]
                    cache["supplier_name"] = ret[17]
                    cache["purchase_name"] = ret[18]
                    cache["st_inventory_qty"] = inner_rets[0][5]
                    cache["st_inventory_total"] = inner_rets[0][6]
                    cache["purchase_qty"] = sum([inner_ret[7] for inner_ret in inner_rets])
                    cache["purchase_total"] = sum([inner_ret[8] for inner_ret in inner_rets])
                    cache["purchase_then_return_qty"] = sum([inner_ret[9] for inner_ret in inner_rets])
                    cache["purchase_then_return_total"] = sum([inner_ret[10] for inner_ret in inner_rets])
                    cache["sale_qty"] = sale_qty_x_months
                    cache["sale_total"] = sum([inner_ret[12] for inner_ret in inner_rets])
                    cache["sale_then_return_qty"] = sum([inner_ret[13] for inner_ret in inner_rets])
                    cache["sale_then_return_total"] = sum([inner_ret[14] for inner_ret in inner_rets])
                    cache["others_qty"] = sum([inner_ret[15] for inner_ret in inner_rets])
                    cache["others_total"] = sum([inner_ret[16] for inner_ret in inner_rets])
                    cache["ed_inventory_qty"] = inner_rets[len(inner_rets) - 1][17]
                    cache["ed_inventory_total"] = inner_rets[len(inner_rets) - 1][18]
                    cache["jit_inventory"] = jit_inventory
                    if sale_qty_x_months == 0 and jit_inventory > 0:
                        cache["ssr"] = "*"
                    else:
                        cache["ssr"] = float("{:.3f}".format(jit_inventory / sale_qty_x_months))
                    preview_table.append(cache)
        response_object = {"status": "success"}
        response_object["preview_table"] = preview_table
        return jsonify(response_object)
    else:
        response_object = {"status": "not found"}
        return jsonify(response_object)


# 预下载"滞销品报表"的接口
@ggfilm_server.route("/api/v1/case4/prepare", methods=["POST"])
def prepare_report_file_case4():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = generate_digest("滞销品报表_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "滞销品报表_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "商品编号", "规格编号", "商品名称", "规格名称",
            "品牌", "分类1", "分类2", "产品系列",
            "STOP状态", "重量/g", "长度/cm", "宽度/cm", "高度/cm",
            "组合商品", "进口商品", "供应商名称", "采购名称",
            "起始库存数量", "起始库存总额", "采购数量", "采购总额",
            "采购退货数量", "采购退货总额", "销售数量", "销售总额",
            "销售退货数量", "销售退货总额", "其他变更数量", "其他变更总额",
            "截止库存数量", "截止库存总额", "实时可用库存", "库销比",
        ])
        for item in preview_table:
            csv_writer.writerow([
                item["product_code"], item["specification_code"], item["product_name"], item["specification_name"],
                item["brand"], item["classification_1"], item["classification_2"], item["product_series"],
                item["stop_status"], item["product_weight"], item["product_length"], item["product_width"], item["product_height"],
                item["is_combined"], item["is_import"], item["supplier_name"], item["purchase_name"],
                item["st_inventory_qty"], item["st_inventory_total"], item["purchase_qty"], item["purchase_total"],
                item["purchase_then_return_qty"], item["purchase_then_return_total"], item["sale_qty"], item["sale_total"],
                item["sale_then_return_qty"], item["sale_then_return_total"], item["others_qty"], item["others_total"],
                item["ed_inventory_qty"], item["ed_inventory_total"], item["jit_inventory"], item["ssr"],
            ])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)


'''
预览效果

商品编号 | 品牌 | 商品名称 | 规格名称 | 供应商 | X个月销量 | Y个月销量 | 库存量 | 库存/X个月销量 | 库存/Y个月销量 |
库存/X个月折算销量 | 库存/Y个月折算销量	| 拟定进货量 | 单个重量/g | 小计重量/kg | 单个体积/cm³ | 小计体积/m³
'''
# 预览"采购辅助分析报表"的接口
@ggfilm_server.route("/api/v1/case5/preview", methods=["POST"])
def preview_report_file_case5():
    way = request.args.get("way", "1")
    payload = request.get_json()
    supplier_name = payload.get("supplier_name", "")
    time_quantum_x = int(payload.get("time_quantum_x", "6"))
    threshold_x = int(payload.get("threshold_x", "2"))
    time_quantum_y = int(payload.get("time_quantum_y", "12"))
    threshold_y = int(payload.get("threshold_y", "1"))
    projected_purchase = int(payload.get("projected_purchase", "12"))
    reduced_btn_option = payload.get("reduced_btn_option", "open")
    stop_status = payload.get("stop_status", "全部")
    be_aggregated = payload.get("be_aggregated", "全部")

    # 1. “供应商”选项为空，则为全部供应商（包括没有供应商的商品条目）
    # 2. way == 2时，不考虑“STOP状态”选项+“是否参与统计”选项
    stmt = ""
    if way == "1":
        if len(supplier_name) > 0:
            stmt = "SELECT specification_code, product_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products WHERE supplier_name = '{}'".format(supplier_name)
            if stop_status != "全部":
                stmt = "{} AND stop_status = '{}'".format(stmt, stop_status)
            if be_aggregated != "全部":
                stmt = "{} AND be_aggregated = '{}'".format(stmt, be_aggregated)
        else:
            stmt = "SELECT specification_code, product_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products"
            if stop_status != "全部":
                stmt = "{} WHERE stop_status = '{}'".format(stmt, stop_status)
            if stop_status != "全部" and be_aggregated != "全部":
                stmt = "{} AND be_aggregated = '{}'".format(stmt, be_aggregated)
            elif stop_status == "全部" and be_aggregated != "全部":
                stmt = "{} WHERE be_aggregated = '{}'".format(stmt, be_aggregated)
        stmt = "{};".format(stmt)
    elif way == "2":
        if len(supplier_name) > 0:
            stmt = "SELECT specification_code, product_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products WHERE supplier_name = '{}';".format(supplier_name)
        else:
            stmt = "SELECT specification_code, product_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products;"

    preview_table = []
    specification_code_list = []
    cache = {}

    rets = DBConnector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            specification_code = ret[0]
            specification_code_list.append(specification_code)
            cache[specification_code] = {}
            cache[specification_code]["product_code"] = ret[1]
            cache[specification_code]["brand"] = ret[2]
            cache[specification_code]["product_name"] = ret[3]
            cache[specification_code]["specification_name"] = ret[4]
            cache[specification_code]["supplier_name"] = ret[5]
            cache[specification_code]["inventory"] = ret[6]
            cache[specification_code]["weight"] = ret[7]
            cache[specification_code]["volume"] = ret[8] * ret[9] * ret[10]
            cache[specification_code]["moq"] = ret[11]
    if len(specification_code_list) > 0:
        for specification_code in specification_code_list:
            # TODO: 先不考虑进销存条目不足指定月数的情况
            stmt = "SELECT st_inventory_qty, ed_inventory_qty, sale_qty, purchase_qty \
FROM ggfilm.inventories WHERE specification_code = '{}' \
ORDER BY create_time DESC LIMIT {};".format(specification_code, time_quantum_y)
            inner_rets = DBConnector.query(stmt)
            if type(inner_rets) is list and len(inner_rets) > 0:
                # 计算X个月销量 + Y个月销量
                cache[specification_code]["sale_qty_x_months"] = 0
                cache[specification_code]["sale_qty_y_months"] = 0
                for inner_ret in inner_rets[time_quantum_y - time_quantum_x:]:
                    cache[specification_code]["sale_qty_x_months"] += inner_ret[2]
                for inner_ret in inner_rets:
                    cache[specification_code]["sale_qty_y_months"] += inner_ret[2]
                # 计算X个月折算销量 + Y个月折算销量
                if reduced_btn_option == "open":
                    reduced_months = 0
                    for inner_ret in inner_rets[time_quantum_y - time_quantum_x:]:
                        if inner_ret[0] == 0 and inner_ret[1] == 0:
                            if inner_ret[3] <= 10 and inner_ret[3] <= inner_ret[2]:
                                reduced_months += 1
                            elif inner_ret[3] > 10 and inner_ret[3] > inner_ret[2]:
                                reduced_months += 1

                    if time_quantum_x != reduced_months:
                        cache[specification_code]["reduced_sale_qty_x_months"] = int(cache[specification_code]["sale_qty_x_months"] * (time_quantum_x / (time_quantum_x - reduced_months)))
                    else:
                        cache[specification_code]["reduced_sale_qty_x_months"] = cache[specification_code]["sale_qty_x_months"]
                    reduced_months = 0
                    for inner_ret in inner_rets:
                        if inner_ret[0] == 0 and inner_ret[1] == 0:
                            reduced_months += 1
                    if time_quantum_y != reduced_months:
                        cache[specification_code]["reduced_sale_qty_y_months"] = int(cache[specification_code]["sale_qty_y_months"] * (time_quantum_y / (time_quantum_y - reduced_months)))
                    else:
                        cache[specification_code]["reduced_sale_qty_y_months"] = cache[specification_code]["sale_qty_y_months"]
                else:
                    cache[specification_code]["reduced_sale_qty_x_months"] = cache[specification_code]["sale_qty_x_months"]
                    cache[specification_code]["reduced_sale_qty_y_months"] = cache[specification_code]["sale_qty_y_months"]
                # 计算库存/X个月销量 + 库存/Y个月销量 + 库存/X个月折算销量 + 库存/Y个月折算销量
                if cache[specification_code]["inventory"] == 0:
                    cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = "0/{}".format(
                        cache[specification_code]["sale_qty_x_months"])
                    cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = "0/{}".format(
                        cache[specification_code]["reduced_sale_qty_x_months"])
                    cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = "0/{}".format(
                        cache[specification_code]["sale_qty_y_months"])
                    cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = "0/{}".format(
                        cache[specification_code]["reduced_sale_qty_y_months"])
                else:
                    if cache[specification_code]["sale_qty_x_months"] == 0:
                        cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["sale_qty_x_months"]))
                    if cache[specification_code]["reduced_sale_qty_x_months"] == 0:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["reduced_sale_qty_x_months"]))
                    if cache[specification_code]["sale_qty_y_months"] == 0:
                        cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["sale_qty_y_months"]))
                    if cache[specification_code]["reduced_sale_qty_y_months"] == 0:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["reduced_sale_qty_y_months"]))
                # 计算拟定进货量
                if reduced_btn_option == "open":
                    if type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"]) is str or \
                        (type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"]) is float and \
                            cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] <= threshold_x) or \
                                type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"]) is str or \
                                    (type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"]) is float and \
                                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] <= threshold_y):
                        cache[specification_code]["projected_purchase"] = \
                            int((cache[specification_code]["reduced_sale_qty_y_months"] / time_quantum_y) * 12) - cache[specification_code]["inventory"]
                    else:
                        cache[specification_code]["projected_purchase"] = 0
                else:
                    if type(cache[specification_code]["inventory_divided_by_sale_qty_x_months"]) is str or \
                        (type(cache[specification_code]["inventory_divided_by_sale_qty_x_months"]) is float and \
                            cache[specification_code]["inventory_divided_by_sale_qty_x_months"] <= threshold_x) or \
                                type(cache[specification_code]["inventory_divided_by_sale_qty_y_months"]) is str or \
                                    (type(cache[specification_code]["inventory_divided_by_sale_qty_y_months"]) is float and \
                                        cache[specification_code]["inventory_divided_by_sale_qty_y_months"] <= threshold_y):
                        cache[specification_code]["projected_purchase"] = \
                            int((cache[specification_code]["sale_qty_y_months"] / time_quantum_y) * 12) - cache[specification_code]["inventory"]
                    else:
                        cache[specification_code]["projected_purchase"] = 0
                if cache[specification_code]["projected_purchase"] > 0 and cache[specification_code]["moq"] > 1:
                    '''
                    比如： MOQ是8，拟定进货量算出来是22，那么是算16还是算24（MOQ的倍数，8，16，24，）？
                    以20%为基准，（22 - 16） / 8 ≥ 20%，那么向上取是24
                    比如： MOQ是8，拟定进货量算出来是17，那么是算16还是算24（MOQ的倍数，8，16，24，）？
                    以20%为基准，（17 - 16） / 8 ＜ 20%，那么向下取是16
                    '''
                    x = cache[specification_code]["projected_purchase"]
                    y = cache[specification_code]["moq"]
                    if x <= y:
                        x = y
                    else:
                        if (x - x % y) / y >= 0.2:
                            x = (x - x % y) + y
                        else:
                            x = x - x % y
                    cache[specification_code]["projected_purchase"] = x
                cache[specification_code]["weight_total"] = float("{:.3f}".format((cache[specification_code]["weight"] * cache[specification_code]["projected_purchase"]) / 1e3))
                cache[specification_code]["volume_total"] = float("{:.3f}".format((cache[specification_code]["volume"] * cache[specification_code]["projected_purchase"]) / 1e3))

        for _, v in cache.items():
            if len(v.keys()) == 20:
                preview_table.append(v)
        response_object = {"status": "success"}
        response_object["preview_table"] = preview_table
    else:
        response_object = {"status": "not found"}
    return jsonify(response_object)


# 预下载"采购辅助分析报表"的接口
@ggfilm_server.route("/api/v1/case5/prepare", methods=["POST"])
def prepare_report_file_case5():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = generate_digest("采购辅助分析报表_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "采购辅助分析报表_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "商品编号", "品牌", "商品名称", "规格名称", "供应商",
            "X个月销量", "X个月折算销量", "Y个月销量", "Y个月折算销量",
            "库存量", "库存/X个月销量", "库存/Y个月销量", "拟定进货量",
            "单个重量/g", "小计重量/kg", "单个体积/cm³", "小计体积/m³"
        ])
        for item in preview_table:
            csv_writer.writerow([
                item["product_code"], item["brand"], item["product_name"], item["specification_name"], item["supplier_name"],
                item["sale_qty_x_months"], item["reduced_sale_qty_x_months"], item["sale_qty_y_months"], item["reduced_sale_qty_y_months"],
                item["inventory"], item["inventory_divided_by_sale_qty_x_months"], item["inventory_divided_by_sale_qty_y_months"], item["projected_purchase"],
                item["weight"], item["weight_total"], item["volume"], item["volume_total"],
            ])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)


# 载入用于计算体积、重量的需求表的接口
@ggfilm_server.route("/api/v1/case6/upload", methods=["POST"])
def upload_csv_file_for_case6():
    csv_files = request.files.getlist("file")
    csv_file_sha256 = generate_digest("{}_{}".format(int(time.time()), csv_files[0].filename))
    csv_file = "{}/ggfilm-server/recev_queue/{}".format(
        os.path.expanduser("~"), csv_file_sha256
    )
    csv_files[0].save(csv_file)

    demand_table = []
    with open(csv_file, "r", encoding='utf-8-sig') as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        line = 0
        for row in csv_reader:
            if line > 0:
                demand_table.append(
                    {
                        "specification_code": row[0].strip(),
                        "quantity": row[1].strip()
                    }
                )
            line += 1

    response_object = {"status": "success"}
    response_object["demand_table"] = demand_table
    return jsonify(response_object)


'''
预览效果

规格编号 | 商品名称 | 规格名称 | 数量 | 长度/cm | 宽度/cm | 高度/cm | 体积合计/m³ | 重量/g | 重量合计/kg
'''
# 预览"体积、重量计算汇总单"的接口
@ggfilm_server.route("/api/v1/case6/preview", methods=["POST"])
def preview_report_file_case6():
    payload = request.get_json()
    demand_table = payload.get("demand_table", [])

    preview_table = []
    for item in demand_table:
        stmt = "SELECT product_name, specification_name, \
product_weight, product_length, product_width, product_height \
FROM ggfilm.products WHERE specification_code = '{}';".format(item["specification_code"])
        rets = DBConnector.query(stmt)
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

    response_object = {"status": "success"}
    response_object["preview_table"] = preview_table
    response_object["preview_summary_table"] = preview_summary_table
    return jsonify(response_object)


# 预下载"体积、重量计算汇总单"的接口
@ggfilm_server.route("/api/v1/case6/prepare", methods=["POST"])
def prepare_report_file_case6():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])
    preview_summary_table = payload.get("preview_summary_table", {})

    ts = int(time.time())
    csv_file_sha256 = generate_digest("体积、重量计算汇总单_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "体积、重量计算汇总单_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "规格编号", "商品名称", "规格名称", "数量",
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

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)


# 下载文件接口
@ggfilm_server.route("/api/v1/download/<path:filename>", methods=["GET"])
def export_report_file_case3(filename):
    return send_from_directory(directory="{}/ggfilm-server/send_queue".format(os.path.expanduser("~")), path=filename)


def generate_file_digest(f: str):
    sha256_hash = hashlib.sha256()
    with open(f, "rb") as fin:
        for byte_block in iter(lambda: fin.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_digest(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def do_data_schema_validation_for_input_products(csv_file: str):
    data_schema = [
        "商品编号", "规格编号", "商品名称", "规格名称",
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
    return is_valid


def do_intelligent_calibration_for_input_products(csv_file: str):
    # 1. 表格里面存在中文逗号，程序需要做下智能矫正
    fr = open(csv_file, "r", encoding='utf-8-sig')
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    for line in fr.readlines():
        line = line.replace("，", ",")
        fw.write(line)
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)

    # 2.1. 表格里面存在很多空行（但是有占位符），程序需要做下智能矫正
    # 2.2. 表格里面存在很多只有逗号的行，程序需要做下智能矫正
    # 2.3. “品牌”，“分类1”，“分类2”，“产品系列”，“供应商名称”，“采购名称”存在“0”这种输入，程序需要做下智能矫正
    # 2.4. “STOP状态”，“组合商品”，“参与统计”，“进口商品”存在“0”或”1“这种输入，程序需要做下智能矫正
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
                if len(new_row[8]) == 0 or new_row[8] == "0":
                    new_row[8] == "停用"
                elif new_row[8] == "1":
                    new_row[8] == "在用"
                if len(new_row[13]) == 0 or new_row[13] == "0":
                    new_row[13] == "否"
                elif new_row[13] == "1":
                    new_row[13] == "是"
                if len(new_row[14]) == 0 or new_row[14] == "0":
                    new_row[14] == "不参与"
                elif new_row[14] == "1":
                    new_row[14] == "参与"
                if len(new_row[15]) == 0 or new_row[15] == "0":
                    new_row[15] == "非进口品"
                elif new_row[15] == "1":
                    new_row[15] == "进口品"
                csv_writer.writerow(new_row)
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)


def do_data_schema_validation_for_input_inventories(csv_file: str):
    data_schema = [
        "商品编号", "商品名称", "规格编号", "规格名称",
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
    return is_valid


def do_intelligent_calibration_for_input_inventories(csv_file: str):
    # 表格里面某些数据行存在多余的逗号，程序需要做下智能矫正
    fr = open(csv_file, "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")
    line = 0
    for row in csv_reader:
        if line == 0:
            csv_writer.writerow(row)
        else:
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


def add_date_for_input_inventories(csv_file: str, import_date: str):
    fr = open(csv_file, "r", encoding='utf-8-sig')
    csv_reader = csv.reader(fr, delimiter=",")
    fw = open(csv_file + ".tmp", "w", encoding='utf-8-sig')
    csv_writer = csv.writer(fw, delimiter=",")
    line = 0
    for row in csv_reader:
        if line == 0:
            new_row = ["年月"] + row
            csv_writer.writerow(new_row)
        else:
            new_row = [import_date] + row
            csv_writer.writerow(new_row)
        line += 1
    fw.close()
    fr.close()
    shutil.move(csv_file + ".tmp", csv_file)


def all_done():
    DBConnector.release_conn()


atexit.register(all_done)
