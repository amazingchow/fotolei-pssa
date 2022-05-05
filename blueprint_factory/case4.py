# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import shelve
import time

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request
from flask import session
from flask_api import status as StatusCode

from .decorator_factory import cost_count
from .decorator_factory import has_logged_in
from .decorator_factory import record_action
from .decorator_factory import restrict_access
from db import db_connector
from utils import ACTION_TYPE_EXPORT
from utils import ROLE_TYPE_ADMIN
from utils import ROLE_TYPE_ORDINARY_USER
from utils import util_calc_month_num
from utils import util_generate_digest


case4_blueprint = Blueprint(
    name="fotolei_pssa_case4_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/case4",
)


'''
预览效果

商品编码 | 规格编码	| 商品名称 | 规格名称 | 品牌 | 分类1 | 分类2 | 起始库存数量 | 采购数量	| 销售数量 | 截止库存数量 | 实时可用库存 | 库销比

其中
* 起始库存数量 = 时间段内第一个月的数量
* 采购数量 = 时间段内每一个月的数量的累加
* 销售数量 = 时间段内每一个月的数量的累加
* 截止库存数量 = 时间段内最后一个月的数量
'''


# 预览"滞销品报表"的接口
@case4_blueprint.route("/preview", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def preview_report_file_case4():
    payload = request.get_json()
    # 1. 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    # 2. 先用其他非空条件筛选出规格编码，再用规格编码筛选出想要的数据
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if st_date > ed_date:
        return make_response(
            jsonify({"message": "无效的输入日期"}),
            StatusCode.HTTP_400_BAD_REQUEST
        )

    time_quantum_x = util_calc_month_num(st_date, ed_date)

    brand = payload.get("brand", "").strip().lower()
    classification_1 = payload.get("classification_1", "").strip().lower()
    classification_2 = payload.get("classification_2", "").strip().lower()
    product_series = payload.get("product_series", "").strip().lower()
    stop_status = payload.get("stop_status", "全部").strip()
    is_combined = payload.get("is_combined", "全部").strip()
    be_aggregated = payload.get("be_aggregated", "全部").strip()
    is_import = payload.get("is_import", "全部").strip()
    supplier_name = payload.get("supplier_name", "").strip().lower()
    threshold_ssr = float(payload.get("threshold_ssr", "4"))
    reduced_btn_option = payload.get("reduced_btn_option", True)

    # TODO: 优化SQL
    stmt = "SELECT * FROM fotolei_pssa.products"
    selections = []
    if len(brand) > 0:
        selections.append("brand = '{}'".format(brand))
    if len(classification_1) > 0:
        selections.append("classification_1 = '{}'".format(classification_1))
    if len(classification_2) > 0:
        selections.append("classification_2 = '{}'".format(classification_2))
    if len(product_series) > 0:
        selections.append("product_series = '{}'".format(product_series))
    if stop_status != "全部":
        selections.append("stop_status = '{}'".format(stop_status))
    if is_combined != "全部":
        selections.append("is_combined = '{}'".format(is_combined))
    if be_aggregated != "全部":
        selections.append("be_aggregated = '{}'".format(be_aggregated))
    if is_import != "全部":
        selections.append("is_import = '{}'".format(is_import))
    if len(supplier_name) > 0:
        selections.append("supplier_name = '{}'".format(supplier_name))
    if len(selections) > 0:
        stmt += " WHERE " + " AND ".join(selections)
    stmt += ";"

    preview_table = []

    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        inventories_import_date_record_table = shelve.open("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table".format(
            os.path.expanduser("~")), flag="c", writeback=False)

        for ret in rets:
            specification_code = ret[3]
            jit_inventory = ret[19]

            v = inventories_import_date_record_table.get(specification_code, [])
            if len(v) == 0:
                # 从未录过进销存报表的商品, 直接忽略
                continue
            first_import_date = v[0]
            if first_import_date > ed_date:
                continue

            stmt = "SELECT * FROM fotolei_pssa.inventories WHERE specification_code = '{}' AND create_time >= '{}' AND create_time <= '{}' ORDER BY create_time ASC;".format(
                specification_code, st_date, ed_date
            )
            inner_rets = db_connector.query(stmt)
            if type(inner_rets) is list and len(inner_rets) > 0:
                is_unsalable = False
                if jit_inventory > 0:
                    sale_qty_x_months = sum(inner_ret[11] - inner_ret[13] for inner_ret in inner_rets)
                    if sale_qty_x_months > 0:
                        if reduced_btn_option:
                            reduced_months = 0
                            time_quantum_x_update = time_quantum_x
                            if first_import_date <= st_date:
                                reduced_months = time_quantum_x - len(inner_rets)
                            else:
                                time_quantum_x_update = util_calc_month_num(first_import_date, ed_date)
                                reduced_months = time_quantum_x_update - len(inner_rets)

                            for inner_ret in inner_rets:
                                if inner_ret[5] == 0 and inner_ret[17] == 0:
                                    if (inner_ret[7] > 0 and inner_ret[7] <= 10) and (inner_ret[7] <= (inner_ret[11] - inner_ret[13])):
                                        reduced_months += 1
                                    elif (inner_ret[7] > 10) and (inner_ret[7] > (inner_ret[11] - inner_ret[13])):
                                        reduced_months += 1
                            if time_quantum_x_update == reduced_months:
                                sale_qty_x_months = int(sale_qty_x_months * (time_quantum_x_update / len(inner_rets)))
                            else:
                                sale_qty_x_months = int(sale_qty_x_months * (time_quantum_x_update / (time_quantum_x_update - reduced_months)))
                        if (jit_inventory / sale_qty_x_months) > threshold_ssr:
                            is_unsalable = True
                    else:
                        is_unsalable = True
                if is_unsalable:
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
                    cache["sale_qty"] = sum([inner_ret[11] for inner_ret in inner_rets])
                    cache["sale_total"] = sum([inner_ret[12] for inner_ret in inner_rets])
                    cache["sale_then_return_qty"] = sum([inner_ret[13] for inner_ret in inner_rets])
                    cache["sale_then_return_total"] = sum([inner_ret[14] for inner_ret in inner_rets])
                    cache["others_qty"] = sum([inner_ret[15] for inner_ret in inner_rets])
                    cache["others_total"] = sum([inner_ret[16] for inner_ret in inner_rets])
                    cache["ed_inventory_qty"] = inner_rets[len(inner_rets) - 1][17]
                    cache["ed_inventory_total"] = inner_rets[len(inner_rets) - 1][18]
                    cache["jit_inventory"] = jit_inventory
                    if sale_qty_x_months <= 0:
                        cache["ssr"] = "{}/{}".format(jit_inventory, sale_qty_x_months)
                    else:
                        cache["ssr"] = float("{:.3f}".format(jit_inventory / sale_qty_x_months))
                    preview_table.append(cache)

        inventories_import_date_record_table.close()

        role = session.get("role", ROLE_TYPE_ORDINARY_USER)
        if role > ROLE_TYPE_ADMIN:
            # 针对普通用户，对敏感数据(起始库存总额、采购总额、采购退货总额、其他变更总额、截止库存总额、单价、金额)做脱敏处理
            for idx in range(len(preview_table)):
                preview_table[idx]["st_inventory_total"] = "*"
                preview_table[idx]["purchase_total"] = "*"
                preview_table[idx]["purchase_then_return_total"] = "*"
                preview_table[idx]["others_total"] = "*"
                preview_table[idx]["ed_inventory_total"] = "*"

        response_object = {"message": "", "preview_table": preview_table}
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_200_OK
        )

    return make_response(
        jsonify({"message": ""}),
        StatusCode.HTTP_404_NOT_FOUND
    )


# 预下载"滞销品报表"的接口
@case4_blueprint.route("/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_EXPORT)
@cost_count
def prepare_report_file_case4():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("滞销品报表_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "滞销品报表_{}.csv".format(ts)
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

    session["op_object"] = output_file

    response_object = {"message": ""}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )
