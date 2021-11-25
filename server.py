# -*- coding: utf-8 -*-
import csv
import logging
logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
import os
import sys
sys.path.append(os.path.abspath("./db"))

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


# 载入库存数据报表的接口
# curl -X POST -H 'Content-Type: application/json' -d '{"file": "~/inventories/产品目录.csv"}' http://127.0.0.1:5000/api/v1/input
@app.route("/api/v1/input", methods=["POST"])
def load_data_infile():
    payload = request.get_json()
    csv_file = payload.get("file")
    logger.info("Load data from {}".format(csv_file))

    DBConnector.load_data_infile(
        """LOAD DATA LOCAL INFILE "{}" """.format(csv_file) +
        "INTO TABLE ggfilm.product_inventory " +
        "FIELDS TERMINATED BY ',' " +
        """ENCLOSED BY '"' """ +
        "LINES TERMINATED BY '\n' " +
        "IGNORE 1 LINES " +
        "(product_code, product_name, specification_code, " +
        "brand, classification_1, classification_2, " +
        "product_series, stop_status, product_weight, " +
        "product_length, product_width, product_hight, " +
        "is_combined, be_aggregated, is_import, " +
        "supplier_code, purchase_name, extra_info);"
    )

    with open(csv_file, "r") as fd:
        csv_reader = csv.reader(fd)
        for _ in csv_reader:
            pass
        stmt = "INSERT INTO ggfilm.product_inventory_summary (total) VALUES (%s);"
        DBConnector.insert(stmt, (csv_reader.line_num - 1,))
        logger.info("There {} records have been inserted!!!".format(csv_reader.line_num - 1))

    response_object = {"status": "success"}
    return jsonify("alive")


# 获取总库存量的接口
# curl -X GET -L http://127.0.0.1:5000/api/v1/inventories/total
@app.route("/api/v1/inventories/total", methods=["GET"])
def inventories_total():
    stmt = "SELECT SUM(total) FROM ggfilm.product_inventory_summary;"
    ret = DBConnector.query(stmt)
    response_object = {"status": "success"}
    if len(ret) == 0:
        response_object["inventories_total"] = "0"
    else:
        response_object["inventories_total"] = ret[0][0]
    return jsonify(response_object)


# 获取所有库存的接口, 带有翻页功能
# curl -X GET -L http://127.0.0.1:5000/api/v1/inventories?page.offset=0&page.limit=20
@app.route("/api/v1/inventories", methods=["GET"])
def inventories():
    page_offset = request.args.get("page.offset")
    page_limit = request.args.get("page.limit")

    stmt = "SELECT product_code, product_name, specification_code, \
        brand, classification_1, classification_2, \
        product_series, stop_status, product_weight, \
        product_length, product_width, product_hight, \
        is_combined, be_aggregated, is_import, \
        supplier_code, purchase_name, \
        DATE_FORMAT(create_time, '%Y-%m-%d %H:%i:%s') \
        FROM ggfilm.product_inventory ORDER BY 'id' DESC LIMIT {}, {};".format(
        page_offset, page_limit)
    inventories = DBConnector.query(stmt)

    response_object = {"status": "success"}
    if (inventories) == 0:
        response_object = {"status": "not found"}
        response_object["inventories"] = None
    else:
        response_object["inventories"] = inventories
    return jsonify(response_object)


if __name__ == "__main__":
    DBConnector = MySQLConnector.instance()
    DBConnector.init_conn("ggfilm")
    app.run(debug=True)
    DBConnector.release_conn()
    