# -*- coding: utf-8 -*-
import atexit
import csv
import hashlib
import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
import os
import sys
sys.path.append(os.path.abspath("./db"))
import time

from collections import defaultdict
SKU_LOOKUP_TABLE = defaultdict(bool)
from db.mysqlcli import MySQLConnector
DBConnector = MySQLConnector.instance()
DBConnector.init_conn("ggfilm")
_stmt = "SELECT specification_code FROM ggfilm.products;"
_rets = DBConnector.query(_stmt)
if type(_rets) is list and len(_rets) > 0:
    for ret in _rets:
        SKU_LOOKUP_TABLE[ret[0]] = True
    logger.info("Insert {} SKUs into SKU_LOOKUP_TABLE!!!".format(len(SKU_LOOKUP_TABLE)))
atexit.register(lambda: DBConnector.release_conn())

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

ggfilm_server = Flask(__name__)
ggfilm_server.config.from_object(__name__)
CORS(ggfilm_server, resources={r"/api/*": {"origins": "*"}})


# 探活接口
# curl -X GET -L http://127.0.0.1:5000/api/v1/keepalive
@ggfilm_server.route("/api/v1/keepalive", methods=["GET"])
def keepalive():
    return jsonify("alive")


# 载入商品数据报表的接口
@ggfilm_server.route("/api/v1/products/upload", methods=["POST"])
def upload_products():
    csv_files = request.files.getlist("file")
    csv_file = "{}/ggfilm-server/products/{}_{}".format(
        os.path.expanduser("~"), int(time.time()), csv_files[0].filename
    )
    csv_files[0].save(csv_file)
    logger.info("Load data from {}".format(csv_file))

    DBConnector.load_data_infile(
        """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
        "INTO TABLE ggfilm.products " +
        "FIELDS TERMINATED BY ',' " +
        """ENCLOSED BY '"' """ +
        "LINES TERMINATED BY '\n' " +
        "IGNORE 1 LINES " +
        "(product_code, specification_code, product_name, specification_name, " +
        "brand, classification_1, classification_2, product_series, stop_status, " +
        "product_weight, product_length, product_width, product_hight, " +
        "is_combined, be_aggregated, is_import, " +
        "supplier_name, purchase_name, jit_inventory);"
    )

    stmt = "SELECT specification_code FROM ggfilm.products;"
    rets = DBConnector.query(stmt)
    SKU_LOOKUP_TABLE.clear()
    for ret in rets:
        SKU_LOOKUP_TABLE[ret[0]] = True
    logger.info("Insert {} SKUs into SKU_LOOKUP_TABLE!!!".format(len(SKU_LOOKUP_TABLE)))

    with open(csv_file, "r") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        for _ in csv_reader:
            pass
        stmt = "INSERT INTO ggfilm.product_summary (total) VALUES (%s);"
        DBConnector.insert(stmt, (csv_reader.line_num - 1,))
        logger.info("There {} records have been inserted!!!".format(csv_reader.line_num - 1))

    response_object = {"status": "success"}
    return jsonify(response_object)


# 载入即时库存报表的接口
@ggfilm_server.route("/api/v1/jitinventory/upload", methods=["POST"])
def upload_jit_inventory_data():
    csv_files = request.files.getlist("file")
    csv_file = "{}/ggfilm-server/jit_inventory/{}_{}".format(
        os.path.expanduser("~"), int(time.time()), csv_files[0].filename
    )
    csv_files[0].save(csv_file)
    logger.info("Load data from {}".format(csv_file))

    sku_inventory_tuple_list = []
    not_inserted_sku_list = []
    with open(csv_file, "r") as fd:
        csv_reader = csv.reader(fd, delimiter=",")
        line = 0
        for row in csv_reader:
            if line == 0:
                line += 1
            else:
                line += 1
                if not SKU_LOOKUP_TABLE.get(row[0], False):
                    not_inserted_sku_list.append(row[0])
                else:
                    sku_inventory_tuple_list.append((row[1], row[0]))
    logger.info("Update for {} SKUs".format(len(sku_inventory_tuple_list)))
    logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))

    stmt = "UPDATE ggfilm.products SET jit_inventory = %s WHERE specification_code = %s;"
    DBConnector.batch_update(stmt, sku_inventory_tuple_list)

    response_object = {"status": "success"}
    if len(not_inserted_sku_list) > 0:
        # 新增sku，需要向用户展示
        response_object["added_skus"] = not_inserted_sku_list
    else:
        response_object["added_skus"] = []
    return jsonify(response_object)


# 下载新增SKU数据表的接口
# curl -X POST -H 'Content-Type: application/json' -d '{"added_skus": ["xxx", "yyy", "zzz"]}' http://127.0.0.1:5000/api/v1/addedskus/download
@ggfilm_server.route("/api/v1/addedskus/download", methods=["POST"])
def export_added_skus_csv_file():
    payload = request.get_json()
    added_skus = payload.get("added_skus")
    logger.info("Added SKUs {}".format(len(added_skus)))

    ts = int(time.time())
    csv_file = "{}/ggfilm-server/added_skus/新增SKU_{}.csv".format(os.path.expanduser("~"), ts)
    output_file = "~/ggfilm-client/added_skus/新增SKU_{}.csv".format(ts)
    with open(csv_file, "w") as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow(["新增SKU"])
        for sku in added_skus:
            csv_writer.writerow([sku])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    return jsonify(response_object)


# 载入库存数据报表的接口
@ggfilm_server.route("/api/v1/inventories/upload", methods=["POST"])
def upload_inventories():
    csv_files = request.files.getlist("file")
    csv_file = "{}/ggfilm-server/inventories/{}_{}".format(
        os.path.expanduser("~"), int(time.time()), csv_files[0].filename
    )
    csv_files[0].save(csv_file)
    logger.info("Load data from {}".format(csv_file))

    DBConnector.load_data_infile(
        """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
        "INTO TABLE ggfilm.inventories " +
        "FIELDS TERMINATED BY ',' " +
        """ENCLOSED BY '"' """ +
        "LINES TERMINATED BY '\n' " +
        "IGNORE 1 LINES " +
        "(product_code, product_name, specification_code, " +
        "specification_name, st_inventory_qty, st_inventory_total, " +
        "purchase_qty, purchase_total, purchase_then_return_qty, " +
        "purchase_then_return_total, sale_qty, sale_total, " +
        "sale_then_return_qty, sale_then_return_total, others_qty, " +
        "others_total, ed_inventory_qty, ed_inventory_total);"
    )

    response_object = {"status": "success"}
    return jsonify(response_object)


# 获取总商品量的接口
# curl -X GET -L http://127.0.0.1:5000/api/v1/products/total
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
# curl -X GET -L http://127.0.0.1:5000/api/v1/products?page.offset=0&page.limit=20
@ggfilm_server.route("/api/v1/products", methods=["GET"])
def list_products():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT product_code, specification_code, product_name, specification_name, \
        brand, classification_1, classification_2, product_series, stop_status, \
        product_weight, product_length, product_width, product_hight, \
        is_combined, be_aggregated, is_import, \
        supplier_name, purchase_name, jit_inventory \
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
# curl -X GET -L http://127.0.0.1:5000/api/v1/inventories?page.offset=0&page.limit=20
@ggfilm_server.route("/api/v1/inventories", methods=["GET"])
def inventories():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT product_code, product_name, specification_code, \
        specification_name, st_inventory_qty, st_inventory_total, \
        purchase_qty, purchase_total, purchase_then_return_qty, \
        purchase_then_return_total, sale_qty, sale_total, \
        sale_then_return_qty, sale_then_return_total, others_qty, \
        others_total, ed_inventory_qty, ed_inventory_total, \
        DATE_FORMAT(create_time, '%Y-%m-%d') \
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
@ggfilm_server.route("/api/v1/allselections", methods=["GET"])
def list_all_selections():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT brand FROM ggfilm.products;"
    brand_selections = DBConnector.query(stmt)
    if (brand_selections) == 0:
        response_object["brand_selections"] = []
    else:
        response_object["brand_selections"] = [{"id": i, "brand": brand[0]} for i, brand in enumerate(brand_selections)]

    stmt = "SELECT DISTINCT classification_1 FROM ggfilm.products;"
    classification_1_selections = DBConnector.query(stmt)
    if (classification_1_selections) == 0:
        response_object["classification_1_selections"] = []
    else:
        response_object["classification_1_selections"] = [{"id": i, "classification-1": classification_1[0]} for i, classification_1 in enumerate(classification_1_selections)]

    stmt = "SELECT DISTINCT classification_2 FROM ggfilm.products;"
    classification_2_selections = DBConnector.query(stmt)
    if (classification_2_selections) == 0:
        response_object["classification_2_selections"] = []
    else:
        response_object["classification_2_selections"] = [{"id": i, "classification-2": classification_2[0]} for i, classification_2 in enumerate(classification_2_selections)]

    stmt = "SELECT DISTINCT product_series FROM ggfilm.products;"
    product_series_selections = DBConnector.query(stmt)
    if (product_series_selections) == 0:
        response_object["product_series_selections"] = []
    else:
        response_object["product_series_selections"] = [{"id": i, "product-series": product_series[0]} for i, product_series in enumerate(product_series_selections)]

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_selections = DBConnector.query(stmt)
    if (supplier_name_selections) == 0:
        response_object["supplier_name_selections"] = []
    else:
        response_object["supplier_name_selections"] = [{"id": i, "supplier-name": supplier_name[0]} for i, supplier_name in enumerate(supplier_name_selections)]

    return jsonify(response_object)


# 导出所有可供选择的选项列表的接口
@ggfilm_server.route("/api/v1/allselections/slist", methods=["GET"])
def list_all_selections_for_slist():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT brand FROM ggfilm.products;"
    brand_selections = DBConnector.query(stmt)
    if (brand_selections) == 0:
        response_object["brand_selections"] = []
    else:
        response_object["brand_selections"] = [{"value": brand[0], "text": brand[0]} for brand in brand_selections]

    stmt = "SELECT DISTINCT classification_1 FROM ggfilm.products;"
    classification_1_selections = DBConnector.query(stmt)
    if (classification_1_selections) == 0:
        response_object["classification_1_selections"] = []
    else:
        response_object["classification_1_selections"] = [{"value": classification_1_selection[0], "text": classification_1_selection[0]} for classification_1_selection in classification_1_selections]

    stmt = "SELECT DISTINCT classification_2 FROM ggfilm.products;"
    classification_2_selections = DBConnector.query(stmt)
    if (classification_2_selections) == 0:
        response_object["classification_2_selections"] = []
    else:
        response_object["classification_2_selections"] = [{"value": classification_2_selection[0], "text": classification_2_selection[0]} for classification_2_selection in classification_2_selections]

    stmt = "SELECT DISTINCT product_series FROM ggfilm.products;"
    product_series_selections = DBConnector.query(stmt)
    if (product_series_selections) == 0:
        response_object["product_series_selections"] = []
    else:
        response_object["product_series_selections"] = [{"value": product_series_selection[0], "text": product_series_selection[0]} for product_series_selection in product_series_selections]

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_selections = DBConnector.query(stmt)
    if (supplier_name_selections) == 0:
        response_object["supplier_name_selections"] = []
    else:
        response_object["supplier_name_selections"] = [{"value": supplier_name_selection[0], "text": supplier_name_selection[0]} for supplier_name_selection in supplier_name_selections]

    return jsonify(response_object)


# 导出销售报表（按分类汇总）的接口
@ggfilm_server.route("/api/v1/export/case1", methods=["POST"])
def export_report_file_case1():
    return jsonify("导出销售报表（按分类汇总）")


# 导出销售报表（按系列汇总）的接口
@ggfilm_server.route("/api/v1/export/case2", methods=["POST"])
def export_report_file_case2():
    return jsonify("导出销售报表（按系列汇总）")


# 预览销售报表（按单个SKU汇总）的接口
'''
预览效果

商品编码 | 规格编码	| 商品名称 | 规格名称 | 起始库存数量 | 采购数量	| 销售数量 | 截止库存数量 | 实时库存

其中
* 起始库存数量 = 时间段内第一个月的数量
* 采购数量 = 时间段内每一个月的数量的累加
* 销售数量 = 时间段内每一个月的数量的累加
* 截止库存数量 = 时间段内最后一个月的数量
'''
@ggfilm_server.route("/api/v1/export/case3/preview", methods=["POST"])
def preview_export_report_file_case3():
    payload = request.get_json()
    # 1. 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    # 2.1. 如果specification_code（规格编码）不为空，直接用规格编码筛选出想要的数据
    # 2.2. 如果specification_code（规格编码）为空，则先用其他非空条件筛选出规格编码，再用规格编码筛选出想要的数据
    st_date = payload.get("st_date").strip()
    st_year, st_month = st_date.split("-")[0], st_date.split("-")[1]
    ed_date = payload.get("ed_date").strip()
    ed_year, ed_month = ed_date.split("-")[0], ed_date.split("-")[1]

    specification_code = payload.get("specification_code").strip()

    def inline():
        resp = {"status": "success"}
        stmt = "SELECT product_code, specification_code, \
            product_name, specification_name, \
            st_inventory_qty, purchase_qty, \
            sale_qty, ed_inventory_qty, \
            DATE_FORMAT(create_time, '%Y-%m-%d') \
            FROM ggfilm.inventories \
            WHERE specification_code = {} AND \
            Month(create_time) >= {} AND \
            Year(create_time) >= {} AND \
            Month(create_time) <= {} AND \
            Year(create_time) <= {} \
            ORDER BY create_time ASC;".format(
                specification_code, st_month, st_year, ed_month, ed_year
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
        product_code = payload.get("product_code").strip()
        product_name = payload.get("product_name").strip()
        brand = payload.get("brand").strip()
        classification_1 = payload.get("classification_1").strip()
        classification_2 = payload.get("classification_2").strip()
        product_series = payload.get("product_series").strip()
        stop_status = payload.get("stop_status").strip()
        is_combined = payload.get("is_combined").strip()
        be_aggregated = payload.get("be_aggregated").strip()
        is_import = payload.get("is_import").strip()
        supplier_name = payload.get("supplier_name").strip()

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
        if len(stop_status) > 0:
            selections.append("stop_status = '{}'".format(stop_status))
        if len(is_combined) > 0:
            selections.append("is_combined = '{}'".format(is_combined))
        if len(be_aggregated) > 0:
            selections.append("be_aggregated = '{}'".format(be_aggregated))
        if len(is_import) > 0:
            selections.append("is_import = '{}'".format(is_import))
        if len(supplier_name) > 0:
            selections.append("supplier_name = '{}'".format(supplier_name))
        stmt += " AND ".join(selections)
        stmt += ";"
        logger.debug(stmt)
        rets = DBConnector.query(stmt)
        if type(rets) is list and len(rets) > 0:
            specification_code = rets[0][0]
            response_object = inline()
            return jsonify(response_object)
        else:
            response_object = {"status": "not found"}
            return jsonify(response_object)


# 预导出销售报表（按单个SKU汇总）的接口
@ggfilm_server.route("/api/v1/export/case3/prepare", methods=["POST"])
def prepare_export_report_file_case3():
    payload = request.get_json()
    st_date = payload.get("st_date").strip()
    st_year, st_month = st_date.split("-")[0], st_date.split("-")[1]
    ed_date = payload.get("ed_date").strip()
    ed_year, ed_month = ed_date.split("-")[0], ed_date.split("-")[1]
    specification_code = payload.get("specification_code").strip()

    stmt = "SELECT * FROM ggfilm.products WHERE specification_code = '{}' LIMIT 1;".format(specification_code)
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
    cache["product_hight"] = rets[0][13]
    cache["is_combined"] = rets[0][14]
    cache["is_import"] = rets[0][16]
    cache["supplier_name"] = rets[0][17]
    cache["purchase_name"] = rets[0][18]
    cache["jit_inventory"] = rets[0][19]

    stmt = "SELECT * FROM ggfilm.inventories \
        WHERE specification_code = {} AND \
        Month(create_time) >= {} AND \
        Year(create_time) >= {} AND \
        Month(create_time) <= {} AND \
        Year(create_time) <= {} \
        ORDER BY create_time ASC;".format(
            specification_code, st_month, st_year, ed_month, ed_year
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
    with open(csv_file, "w") as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "商品编码", "规格编码", "商品名称", "规格名称",
            "品牌", "分类1", "分类2", "产品系列",
            "STOP状态", "重量/g", "长度/cm", "宽度/cm", "高度/cm",
            "组合商品", "进口产品", "供应商名称", "采购名称",
            "起始库存数量", "起始库存总额", "采购数量", "采购总额",
            "采购退货数量", "采购退货总额", "销售数量", "销售总额",
            "销售退货数量", "销售退货总额", "其他变更数量", "其他变更总额",
            "截止库存数量", "截止库存总额", "实时库存",
        ])
        csv_writer.writerow([
            cache["product_code"], cache["specification_code"], cache["product_name"], cache["specification_name"],
            cache["brand"], cache["classification_1"], cache["classification_2"], cache["product_series"],
            cache["stop_status"], cache["product_weight"], cache["product_length"], cache["product_width"], cache["product_hight"],
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


# 导出销售报表（按单个SKU汇总）的接口
@ggfilm_server.route("/api/v1/export/case3/<path:filename>", methods=["GET"])
def export_report_file_case3(filename):
    return send_from_directory(directory="{}/ggfilm-server/send_queue".format(os.path.expanduser("~")), path=filename)


# 导出滞销品报表的接口
@ggfilm_server.route("/api/v1/export/case4", methods=["POST"])
def export_report_file_case4():
    return jsonify("导出滞销品报表")


# 导出进口产品采购单的接口
@ggfilm_server.route("/api/v1/export/case5", methods=["POST"])
def export_report_file_case5():
    return jsonify("导出进口产品采购单")


# 导出体积、重量计算汇总单的接口
@ggfilm_server.route("/api/v1/export/case6", methods=["POST"])
def export_report_file_case6():
    return jsonify("导出体积、重量计算汇总单")


def generate_digest(s:str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
