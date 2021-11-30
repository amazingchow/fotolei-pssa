# -*- coding: utf-8 -*-
import csv
import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
import os
import sys
sys.path.append(os.path.abspath("./db"))

from collections import defaultdict
SKU_LOOKUP_TABLE = defaultdict(bool)
from db.mysqlcli import MySQLConnector
DBConnector = object()
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# 探活接口
# curl -X GET -L http://127.0.0.1:5000/api/v1/keepalive
@app.route("/api/v1/keepalive", methods=["GET"])
def keepalive():
    return jsonify("alive")


# 载入商品数据报表的接口
# curl -X POST -H 'Content-Type: application/json' -d '{"file": "~/products/产品目录.csv"}' http://127.0.0.1:5000/api/v1/products/import
@app.route("/api/v1/products/import", methods=["POST"])
def import_products_csv_file():
    payload = request.get_json()
    csv_file = payload.get("file")
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
# curl -X POST -H 'Content-Type: application/json' -d '{"file": "~/jit-inventory/实时库存.csv"}' http://127.0.0.1:5000/api/v1/jitinventory/import
@app.route("/api/v1/jitinventory/import", methods=["POST"])
def import_jit_inventory_csv_file():
    payload = request.get_json()
    csv_file = payload.get("file")
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
                    sku_inventory_tuple_list.append((row[0], row[1]))
    logger.info("Update for {} SKUs".format(len(sku_inventory_tuple_list)))
    logger.info("There are {} SKUs not inserted".format(len(not_inserted_sku_list)))

    response_object = {"status": "success"}
    if len(not_inserted_sku_list) > 0:
        # 新增sku，需要向用户展示
        response_object["added_skus"] = not_inserted_sku_list
    else:
        response_object["added_skus"] = []
    return jsonify(response_object)


# 下载新增SKU数据表的接口
# curl -X POST -H 'Content-Type: application/json' -d '{"added_skus": ["xxx", "yyy", "zzz"]}' http://127.0.0.1:5000/api/v1/addedskus/download
@app.route("/api/v1/addedskus/download", methods=["POST"])
def export_added_skus_csv_file():
    payload = request.get_json()
    added_skus = payload.get("added_skus")
    logger.info("Added SKUs {}".format(len(added_skus)))
    response_object = {"status": "success"}
    return jsonify(response_object)


# 载入库存数据报表的接口
# curl -X POST -H 'Content-Type: application/json' -d '{"file": "~/inventories/产品目录.csv"}' http://127.0.0.1:5000/api/v1/inventories/import
@app.route("/api/v1/inventories/import", methods=["POST"])
def import_inventories_csv_file():
    payload = request.get_json()
    csv_file = payload.get("file")
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
@app.route("/api/v1/products/total", methods=["GET"])
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
@app.route("/api/v1/products", methods=["GET"])
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
        response_object["products"] = None
    else:
        response_object["products"] = products
    return jsonify(response_object)


# 获取所有库存的接口, 带有翻页功能
# curl -X GET -L http://127.0.0.1:5000/api/v1/inventories?page.offset=0&page.limit=20
@app.route("/api/v1/inventories", methods=["GET"])
def inventories():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT product_code, product_name, specification_code, \
        specification_name, st_inventory_qty, st_inventory_total, \
        purchase_qty, purchase_total, purchase_then_return_qty, \
        purchase_then_return_total, sale_qty, sale_total, \
        sale_then_return_qty, sale_then_return_total, others_qty, \
        others_total, ed_inventory_qty, ed_inventory_total \
        FROM ggfilm.inventories ORDER BY 'id' DESC LIMIT {}, {};".format(
        page_offset, page_limit)
    inventories = DBConnector.query(stmt)

    response_object = {"status": "success"}
    if (inventories) == 0:
        response_object = {"status": "not found"}
        response_object["inventories"] = None
    else:
        response_object["inventories"] = inventories
    return jsonify(response_object)


# 导出销售报表（按分类汇总）的接口
@app.route("/api/v1/export/case1", methods=["POST"])
def export_report_file_case1():
    return jsonify("导出销售报表（按分类汇总）")


# 导出销售报表（按系列汇总）的接口
@app.route("/api/v1/export/case2", methods=["POST"])
def export_report_file_case2():
    return jsonify("导出销售报表（按系列汇总）")


# 导出销售报表（按单个SKU汇总）的接口
@app.route("/api/v1/export/case3", methods=["POST"])
def export_report_file_case3():
    return jsonify("导出销售报表（按单个SKU汇总）")


# 导出滞销品报表的接口
@app.route("/api/v1/export/case4", methods=["POST"])
def export_report_file_case4():
    return jsonify("导出滞销品报表")


# 导出进口产品采购单的接口
@app.route("/api/v1/export/case5", methods=["POST"])
def export_report_file_case5():
    return jsonify("导出进口产品采购单")


# 导出体积、重量计算汇总单的接口
@app.route("/api/v1/export/case6", methods=["POST"])
def export_report_file_case6():
    return jsonify("导出体积、重量计算汇总单")


if __name__ == "__main__":
    DBConnector = MySQLConnector.instance()
    DBConnector.init_conn("ggfilm")

    stmt = "SELECT specification_code FROM ggfilm.products;"
    rets = DBConnector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            SKU_LOOKUP_TABLE[ret[0]] = True
        logger.info("Insert {} SKUs into SKU_LOOKUP_TABLE!!!".format(len(SKU_LOOKUP_TABLE)))

    app.run(debug=True)
    DBConnector.release_conn()
    