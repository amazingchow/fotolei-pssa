# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import cost_count


# 导出所有可供选择的选项列表的接口
@blueprint.route("/api/v1/alloptions", methods=["GET"])
@cost_count
def list_all_options():
    response_object = {"status": "success"}

    stmt = "SELECT DISTINCT brand FROM ggfilm.products;"
    brand_options = db_connector.query(stmt)
    if len(brand_options) == 0:
        response_object["brand_options"] = []
    else:
        response_object["brand_options"] = [{"id": i, "brand": brand[0]} for i, brand in enumerate(brand_options)]

    stmt = "SELECT DISTINCT classification_1 FROM ggfilm.products;"
    classification_1_options = db_connector.query(stmt)
    if len(classification_1_options) == 0:
        response_object["classification_1_options"] = []
    else:
        response_object["classification_1_options"] = [{"id": i, "classification-1": classification_1[0]} for i, classification_1 in enumerate(classification_1_options)]

    stmt = "SELECT DISTINCT classification_2 FROM ggfilm.products;"
    classification_2_options = db_connector.query(stmt)
    if len(classification_2_options) == 0:
        response_object["classification_2_options"] = []
    else:
        response_object["classification_2_options"] = [{"id": i, "classification-2": classification_2[0]} for i, classification_2 in enumerate(classification_2_options)]

    stmt = "SELECT DISTINCT product_series FROM ggfilm.products;"
    product_series_options = db_connector.query(stmt)
    if len(product_series_options) == 0:
        response_object["product_series_options"] = []
    else:
        response_object["product_series_options"] = [{"id": i, "product-series": product_series[0]} for i, product_series in enumerate(product_series_options)]

    stmt = "SELECT DISTINCT supplier_name FROM ggfilm.products;"
    supplier_name_options = db_connector.query(stmt)
    if len(supplier_name_options) == 0:
        response_object["supplier_name_options"] = []
    else:
        response_object["supplier_name_options"] = [{"id": i, "supplier-name": supplier_name[0]} for i, supplier_name in enumerate(supplier_name_options)]

    return jsonify(response_object)
