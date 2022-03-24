# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

from flask import Blueprint
from flask import jsonify

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from db import db_connector
from utils import ROLE_TYPE_ORDINARY_USER
from utils import util_cost_count


option_blueprint = Blueprint(
    name="fotolei_pssa_option_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/options",
)


# 导出所有可供选择的选项列表的接口
@option_blueprint.route("/", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@util_cost_count
def list_all_options():
    response_object = {"status": "success"}

    # TODO: 优化SQL
    stmt = "SELECT DISTINCT brand FROM fotolei_pssa.products;"
    brand_options = db_connector.query(stmt)
    if len(brand_options) == 0:
        response_object["brand_options"] = []
    else:
        response_object["brand_options"] = [{"id": i, "brand": brand[0]} for i, brand in enumerate(brand_options)]

    stmt = "SELECT DISTINCT classification_1 FROM fotolei_pssa.products;"
    classification_1_options = db_connector.query(stmt)
    if len(classification_1_options) == 0:
        response_object["classification_1_options"] = []
    else:
        response_object["classification_1_options"] = [{"id": i, "classification-1": classification_1[0]} for i, classification_1 in enumerate(classification_1_options)]

    stmt = "SELECT DISTINCT classification_2 FROM fotolei_pssa.products;"
    classification_2_options = db_connector.query(stmt)
    if len(classification_2_options) == 0:
        response_object["classification_2_options"] = []
    else:
        response_object["classification_2_options"] = [{"id": i, "classification-2": classification_2[0]} for i, classification_2 in enumerate(classification_2_options)]

    stmt = "SELECT DISTINCT product_series FROM fotolei_pssa.products;"
    product_series_options = db_connector.query(stmt)
    if len(product_series_options) == 0:
        response_object["product_series_options"] = []
    else:
        response_object["product_series_options"] = [{"id": i, "product-series": product_series[0]} for i, product_series in enumerate(product_series_options)]

    stmt = "SELECT DISTINCT supplier_name FROM fotolei_pssa.products;"
    supplier_name_options = db_connector.query(stmt)
    if len(supplier_name_options) == 0:
        response_object["supplier_name_options"] = []
    else:
        response_object["supplier_name_options"] = [{"id": i, "supplier-name": supplier_name[0]} for i, supplier_name in enumerate(supplier_name_options)]

    return jsonify(response_object)
