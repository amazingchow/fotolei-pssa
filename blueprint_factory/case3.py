# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import time

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask import session
from flask_api import status as StatusCode

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from .decorator_factory import cost_count
from .decorator_factory import record_action
from db import db_connector
from utils import ACTION_TYPE_EXPORT
from utils import ROLE_TYPE_ORDINARY_USER
from utils import util_generate_digest


case3_blueprint = Blueprint(
    name="fotolei_pssa_case3_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/case3",
)


'''
预览效果

商品编码 | 规格编码	| 商品名称 | 规格名称 | 起始库存数量 | 采购数量	| 销售数量 | 截止库存数量 | 实时可用库存

其中
* 起始库存数量 = 时间段内第一个月的数量
* 采购数量 = 时间段内每一个月的数量的累加
* 销售数量 = 时间段内每一个月的数量的累加
* 截止库存数量 = 时间段内最后一个月的数量
'''


# 预览"销售报表（按单个SKU汇总）"的接口
@case3_blueprint.route("/preview", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def preview_report_file_case3():
    payload = request.get_json()
    # 1. 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    # 2.1. 如果specification_code（规格编码）不为空，直接用规格编码筛选出想要的数据
    # 2.2. 如果specification_code（规格编码）为空，则先用其他非空条件筛选出规格编码，再用规格编码筛选出想要的数据
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        return make_response(
            jsonify({"message": "invalid st_date and ed_date"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    specification_code = payload.get("specification_code", "").strip()
    specification_code_list = []

    def inline():
        resp = {"message": ""}
        resp["preview_table"] = []
        for scode in specification_code_list:
            cache = {}

            stmt = "SELECT * FROM fotolei_pssa.inventories WHERE specification_code = '{}' AND create_time >= '{}' AND create_time <= '{}' ORDER BY create_time ASC;".format(
                scode, st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                cache["st_inventory_qty"] = rets[0][5]
                cache["st_inventory_total"] = rets[0][6]
                cache["purchase_qty"] = sum([ret[7] for ret in rets])
                cache["purchase_total"] = sum([ret[8] for ret in rets])
                cache["purchase_then_return_qty"] = sum([ret[9] for ret in rets])
                cache["purchase_then_return_total"] = sum([ret[10] for ret in rets])
                cache["sale_qty"] = sum([ret[11] for ret in rets])
                cache["sale_total"] = sum([ret[12] for ret in rets])
                cache["sale_then_return_qty"] = sum([ret[13] for ret in rets])
                cache["sale_then_return_total"] = sum([ret[14] for ret in rets])
                cache["others_qty"] = sum([ret[15] for ret in rets])
                cache["others_total"] = sum([ret[16] for ret in rets])
                cache["ed_inventory_qty"] = rets[len(rets) - 1][17]
                cache["ed_inventory_total"] = rets[len(rets) - 1][18]

                stmt = "SELECT * FROM fotolei_pssa.products WHERE specification_code = '{}';".format(scode)
                inner_rets = db_connector.query(stmt)
                cache["product_code"] = inner_rets[0][1]
                cache["product_name"] = inner_rets[0][2]
                cache["specification_code"] = inner_rets[0][3]
                cache["specification_name"] = inner_rets[0][4]
                cache["brand"] = inner_rets[0][5]
                cache["classification_1"] = inner_rets[0][6]
                cache["classification_2"] = inner_rets[0][7]
                cache["product_series"] = inner_rets[0][8]
                cache["stop_status"] = inner_rets[0][9]
                cache["product_weight"] = inner_rets[0][10]
                cache["product_length"] = inner_rets[0][11]
                cache["product_width"] = inner_rets[0][12]
                cache["product_height"] = inner_rets[0][13]
                cache["is_combined"] = inner_rets[0][14]
                cache["is_import"] = inner_rets[0][16]
                cache["supplier_name"] = inner_rets[0][17]
                cache["purchase_name"] = inner_rets[0][18]
                cache["jit_inventory"] = inner_rets[0][19]

                resp["preview_table"].append(cache)
        return resp

    if len(specification_code) > 0:
        specification_code_list.append(specification_code)
        response_object = inline()
        if len(response_object["preview_table"]) == 0:
            return make_response(
                jsonify(response_object),
                StatusCode.HTTP_404_NOT_FOUND
            )
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_200_OK
        )

    product_code = payload.get("product_code", "").strip()
    product_name = payload.get("product_name", "").strip()
    brand = payload.get("brand", "").strip().lower()
    classification_1 = payload.get("classification_1", "").strip().lower()
    classification_2 = payload.get("classification_2", "").strip().lower()
    product_series = payload.get("product_series", "").strip().lower()
    stop_status = payload.get("stop_status", "全部").strip()
    is_combined = payload.get("is_combined", "全部").strip()
    be_aggregated = payload.get("be_aggregated", "全部").strip()
    is_import = payload.get("is_import", "全部").strip()
    supplier_name = payload.get("supplier_name", "").strip().lower()

    # TODO: 优化SQL
    stmt = "SELECT specification_code FROM fotolei_pssa.products"
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

    if len(selections) == 0:
        stmt += ";"
    elif len(selections) == 1:
        stmt += " WHERE {};".format(selections[0])
    else:
        stmt += " WHERE {};".format(" AND ".join(selections))
    
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            specification_code_list.append(ret[0])
        response_object = inline()
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_200_OK
        )

    return make_response(
        jsonify({"message": ""}),
        StatusCode.HTTP_404_NOT_FOUND
    )


# 预下载"销售报表（按单个SKU汇总）"的接口
@case3_blueprint.route("/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_EXPORT)
@cost_count
def prepare_report_file_case3():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("销售报表（按单个SKU汇总）_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "销售报表（按单个SKU汇总）_{}.csv".format(ts)
    with open(csv_file, "w", encoding="utf-8-sig") as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "商品编码", "规格编码", "商品名称", "规格名称",
            "品牌", "分类1", "分类2", "产品系列",
            "STOP状态", "重量/g", "长度/cm", "宽度/cm", "高度/cm",
            "组合商品", "进口商品", "供应商名称", "采购名称",
            "起始库存数量", "起始库存总额", "采购数量", "采购总额",
            "采购退货数量", "采购退货总额", "销售数量", "销售总额",
            "销售退货数量", "销售退货总额", "其他变更数量", "其他变更总额",
            "截止库存数量", "截止库存总额", "实时可用库存",
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
                item["ed_inventory_qty"], item["ed_inventory_total"], item["jit_inventory"],
            ])

    session["op_object"] = output_file

    response_object = {"message": ""}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )
