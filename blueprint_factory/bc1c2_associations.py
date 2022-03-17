# -*- coding: utf-8 -*-
import os
import sys
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import lookup_table_brand_classification_1_2_association
from utils import lookup_table_classification_1_2_association
from utils import lookup_table_brand_classification_2_association
from utils import cost_count


# 返回关联查询的接口
@blueprint.route("/api/v1/associations/bc1c2", methods=["POST"])
@cost_count
def fetch_associations_bc1c2():
    payload = request.get_json()
    brand = payload["brand"].strip()
    classification_1 = payload.get("classification_1", "").strip()
    classification_2 = payload.get("classification_2", "").strip()
    product_series = payload.get("product_series", "").strip()

    response_object = {"status": "success"}
    response_object['classification_1_selections'] = []
    response_object['classification_2_selections'] = []
    response_object['product_series_selections'] = []
    response_object['supplier_name_selections'] = []

    if len(classification_1) == 0:
        response_object['classification_1_selections'] = \
            list(lookup_table_brand_classification_1_2_association[brand])
        return jsonify(response_object)
    else:
        if len(classification_2) == 0:
            response_object['classification_2_selections'] = \
                list(lookup_table_brand_classification_1_2_association[brand][classification_1])
            return jsonify(response_object)
        else:
            if len(product_series) == 0:
                response_object['product_series_selections'] = \
                    list(lookup_table_brand_classification_1_2_association[brand][classification_1][classification_2])
                return jsonify(response_object)
            else:
                response_object['supplier_name_selections'] = \
                    list(lookup_table_brand_classification_1_2_association[brand][classification_1][classification_2][product_series])
                return jsonify(response_object)


# 返回关联查询的接口
@blueprint.route("/api/v1/associations/c1c2", methods=["POST"])
@cost_count
def fetch_associations_c1c2():
    payload = request.get_json()
    classification_1 = payload["classification_1"].strip()

    response_object = {"status": "success"}
    response_object['classification_2_selections'] = \
        list(lookup_table_classification_1_2_association[classification_1])
    return jsonify(response_object)


# 返回关联查询的接口
@blueprint.route("/api/v1/associations/bc2", methods=["POST"])
@cost_count
def fetch_associations_bc2():
    payload = request.get_json()
    brand = payload["brand"].strip()

    response_object = {"status": "success"}
    response_object['classification_2_selections'] = \
        list(lookup_table_brand_classification_2_association[brand])
    return jsonify(response_object)
