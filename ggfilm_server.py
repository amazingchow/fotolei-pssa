# -*- coding: utf-8 -*-
import atexit
import csv
import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s")
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

from flask import Flask, jsonify, request
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
def import_products_csv_file():
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
def import_jit_inventory_csv_file():
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
def import_inventories_csv_file():
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
def products_total():
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
def products():
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


# 导出销售报表（按单个SKU汇总）的接口
@ggfilm_server.route("/api/v1/export/case3", methods=["POST"])
def export_report_file_case3():
    return jsonify("导出销售报表（按单个SKU汇总）")


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
