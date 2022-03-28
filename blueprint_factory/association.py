# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../utils"))

from flask import Blueprint
from flask import jsonify
from flask import request

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from .decorator_factory import cost_count
from utils import get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name
from utils import get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c1
from utils import get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c2
from utils import get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_product_series
from utils import get_lookup_table_k_brand_v_brand_c2
from utils import get_lookup_table_k_c1_v_c1_c2
from utils import ROLE_TYPE_ORDINARY_USER


association_blueprint = Blueprint(
    name="fotolei_pssa_association_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/associations",
)


# 返回关联查询的接口
@association_blueprint.route("/bc1c2", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
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
            list(get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c1(brand))
        return jsonify(response_object)
    else:
        if len(classification_2) == 0:
            response_object['classification_2_selections'] = \
                list(get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_c2(brand, classification_1))
            return jsonify(response_object)
        else:
            if len(product_series) == 0:
                response_object['product_series_selections'] = \
                    list(get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name_keys_product_series(brand, classification_1, classification_2))
                return jsonify(response_object)
            else:
                response_object['supplier_name_selections'] = \
                    list(get_lookup_table_k_brand_k_c1_k_c2_k_product_series_v_supplier_name(brand, classification_1, classification_2, product_series))
                return jsonify(response_object)


# 返回关联查询的接口
@association_blueprint.route("/c1c2", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def fetch_associations_c1c2():
    payload = request.get_json()
    classification_1 = payload["classification_1"].strip()

    response_object = {"status": "success"}
    response_object['classification_2_selections'] = \
        list(get_lookup_table_k_c1_v_c1_c2(classification_1))
    return jsonify(response_object)


# 返回关联查询的接口
@association_blueprint.route("/bc2", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def fetch_associations_bc2():
    payload = request.get_json()
    brand = payload["brand"].strip()

    response_object = {"status": "success"}
    response_object['classification_2_selections'] = \
        list(get_lookup_table_k_brand_v_brand_c2(brand))
    return jsonify(response_object)
