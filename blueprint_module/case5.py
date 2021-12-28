# -*- coding: utf-8 -*-
import csv
import os
import sys
import time
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import db_connector
from utils import cost_count
from utils import generate_digest


'''
预览效果

规格编码 | 品牌 | 商品名称 | 规格名称 | 供应商 | X个月销量 | Y个月销量 | 库存量 | 库存/X个月销量 | 库存/Y个月销量 |
库存/X个月折算销量 | 库存/Y个月折算销量	| 拟定进货量 | 单个重量/g | 小计重量/kg | 单个体积/cm³ | 小计体积/m³
'''


# 预览"采购辅助分析报表"的接口
@blueprint.route("/api/v1/case5/preview", methods=["POST"])
@cost_count
def preview_report_file_case5():
    way = request.args.get("way", "1")
    payload = request.get_json()
    supplier_name = payload.get("supplier_name", "").lower()
    time_quantum_x = int(payload.get("time_quantum_x", "6"))
    threshold_x = int(payload.get("threshold_x", "2"))
    time_quantum_y = int(payload.get("time_quantum_y", "12"))
    threshold_y = int(payload.get("threshold_y", "1"))
    projected_purchase = int(payload.get("projected_purchase", "12"))
    reduced_btn_option = payload.get("reduced_btn_option", True)
    stop_status = payload.get("stop_status", "全部")
    be_aggregated = payload.get("be_aggregated", "全部")

    # 1. “供应商”选项为空，则为全部供应商（包括没有供应商的商品条目）
    # 2. way == 2时，不考虑“STOP状态”选项+“是否参与统计”选项
    stmt = ""
    if way == "1":
        if len(supplier_name) > 0:
            stmt = "SELECT specification_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products WHERE supplier_name = '{}'".format(supplier_name)
            if stop_status != "全部":
                stmt = "{} AND stop_status = '{}'".format(stmt, stop_status)
            if be_aggregated != "全部":
                stmt = "{} AND be_aggregated = '{}'".format(stmt, be_aggregated)
        else:
            stmt = "SELECT specification_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products"
            if stop_status != "全部":
                stmt = "{} WHERE stop_status = '{}'".format(stmt, stop_status)
            if stop_status != "全部" and be_aggregated != "全部":
                stmt = "{} AND be_aggregated = '{}'".format(stmt, be_aggregated)
            elif stop_status == "全部" and be_aggregated != "全部":
                stmt = "{} WHERE be_aggregated = '{}'".format(stmt, be_aggregated)
        stmt = "{};".format(stmt)
    elif way == "2":
        if len(supplier_name) > 0:
            stmt = "SELECT specification_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products WHERE supplier_name = '{}';".format(supplier_name)
        else:
            stmt = "SELECT specification_code, brand, product_name, specification_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq \
FROM ggfilm.products;"

    preview_table = []
    specification_code_list = []
    cache = {}
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        for ret in rets:
            specification_code = ret[0]
            specification_code_list.append(specification_code)
            cache[specification_code] = {}
            cache[specification_code]["specification_code"] = specification_code
            cache[specification_code]["brand"] = ret[1]
            cache[specification_code]["product_name"] = ret[2]
            cache[specification_code]["specification_name"] = ret[3]
            cache[specification_code]["supplier_name"] = ret[4]
            cache[specification_code]["inventory"] = ret[5]
            cache[specification_code]["weight"] = ret[6]
            cache[specification_code]["volume"] = ret[7] * ret[8] * ret[9]
            cache[specification_code]["moq"] = ret[10]
    if len(specification_code_list) > 0:
        for specification_code in specification_code_list:
            # TODO: 先不考虑进销存条目不足指定月数的情况
            stmt = "SELECT st_inventory_qty, ed_inventory_qty, sale_qty, purchase_qty \
FROM ggfilm.inventories WHERE specification_code = '{}' \
ORDER BY create_time DESC LIMIT {};".format(specification_code, time_quantum_y)
            inner_rets = db_connector.query(stmt)
            if type(inner_rets) is list and len(inner_rets) > 0:
                # 计算X个月销量 + Y个月销量
                cache[specification_code]["sale_qty_x_months"] = 0
                cache[specification_code]["sale_qty_y_months"] = 0
                for inner_ret in inner_rets[time_quantum_y - time_quantum_x:]:
                    cache[specification_code]["sale_qty_x_months"] += inner_ret[2]
                for inner_ret in inner_rets:
                    cache[specification_code]["sale_qty_y_months"] += inner_ret[2]
                # 计算X个月折算销量 + Y个月折算销量
                if reduced_btn_option:
                    reduced_months = 0
                    for inner_ret in inner_rets[time_quantum_y - time_quantum_x:]:
                        if inner_ret[0] == 0 and inner_ret[1] == 0:
                            if inner_ret[3] <= 10 and inner_ret[3] <= inner_ret[2]:
                                reduced_months += 1
                            elif inner_ret[3] > 10 and inner_ret[3] > inner_ret[2]:
                                reduced_months += 1

                    if time_quantum_x != reduced_months:
                        cache[specification_code]["reduced_sale_qty_x_months"] = int(cache[specification_code]["sale_qty_x_months"] * (time_quantum_x / (time_quantum_x - reduced_months)))
                    else:
                        cache[specification_code]["reduced_sale_qty_x_months"] = cache[specification_code]["sale_qty_x_months"]
                    reduced_months = 0
                    for inner_ret in inner_rets:
                        if inner_ret[0] == 0 and inner_ret[1] == 0:
                            reduced_months += 1
                    if time_quantum_y != reduced_months:
                        cache[specification_code]["reduced_sale_qty_y_months"] = int(cache[specification_code]["sale_qty_y_months"] * (time_quantum_y / (time_quantum_y - reduced_months)))
                    else:
                        cache[specification_code]["reduced_sale_qty_y_months"] = cache[specification_code]["sale_qty_y_months"]
                else:
                    cache[specification_code]["reduced_sale_qty_x_months"] = cache[specification_code]["sale_qty_x_months"]
                    cache[specification_code]["reduced_sale_qty_y_months"] = cache[specification_code]["sale_qty_y_months"]
                # 计算库存/X个月销量 + 库存/Y个月销量 + 库存/X个月折算销量 + 库存/Y个月折算销量
                if cache[specification_code]["inventory"] == 0:
                    cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = "0/{}".format(
                        cache[specification_code]["sale_qty_x_months"])
                    cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = "0/{}".format(
                        cache[specification_code]["reduced_sale_qty_x_months"])
                    cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = "0/{}".format(
                        cache[specification_code]["sale_qty_y_months"])
                    cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = "0/{}".format(
                        cache[specification_code]["reduced_sale_qty_y_months"])
                else:
                    if cache[specification_code]["sale_qty_x_months"] == 0:
                        cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["sale_qty_x_months"]))
                    if cache[specification_code]["reduced_sale_qty_x_months"] == 0:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["reduced_sale_qty_x_months"]))
                    if cache[specification_code]["sale_qty_y_months"] == 0:
                        cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["sale_qty_y_months"]))
                    if cache[specification_code]["reduced_sale_qty_y_months"] == 0:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = "{}/0".format(
                            cache[specification_code]["inventory"])
                    else:
                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = \
                            float("{:.3f}".format(cache[specification_code]["inventory"] / cache[specification_code]["reduced_sale_qty_y_months"]))
                # 计算拟定进货量
                if reduced_btn_option:
                    if type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"]) is str or \
                        (type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"]) is float and \
                            cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] <= threshold_x) or \
                                type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"]) is str or \
                                    (type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"]) is float and \
                                        cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] <= threshold_y):
                        cache[specification_code]["projected_purchase"] = \
                            int((cache[specification_code]["reduced_sale_qty_y_months"] / time_quantum_y) * projected_purchase) - cache[specification_code]["inventory"]
                    else:
                        cache[specification_code]["projected_purchase"] = 0
                else:
                    if type(cache[specification_code]["inventory_divided_by_sale_qty_x_months"]) is str or \
                        (type(cache[specification_code]["inventory_divided_by_sale_qty_x_months"]) is float and \
                            cache[specification_code]["inventory_divided_by_sale_qty_x_months"] <= threshold_x) or \
                                type(cache[specification_code]["inventory_divided_by_sale_qty_y_months"]) is str or \
                                    (type(cache[specification_code]["inventory_divided_by_sale_qty_y_months"]) is float and \
                                        cache[specification_code]["inventory_divided_by_sale_qty_y_months"] <= threshold_y):
                        cache[specification_code]["projected_purchase"] = \
                            int((cache[specification_code]["sale_qty_y_months"] / time_quantum_y) * projected_purchase) - cache[specification_code]["inventory"]
                    else:
                        cache[specification_code]["projected_purchase"] = 0
                if cache[specification_code]["projected_purchase"] > 0 and cache[specification_code]["moq"] > 1:
                    '''
                    比如： MOQ是8，拟定进货量算出来是22，那么是算16还是算24（MOQ的倍数，8，16，24，）？
                    以20%为基准，（22 - 16） / 8 ≥ 20%，那么向上取是24
                    比如： MOQ是8，拟定进货量算出来是17，那么是算16还是算24（MOQ的倍数，8，16，24，）？
                    以20%为基准，（17 - 16） / 8 ＜ 20%，那么向下取是16
                    '''
                    x = cache[specification_code]["projected_purchase"]
                    y = cache[specification_code]["moq"]
                    if x <= y:
                        x = y
                    else:
                        if (x - x % y) / y >= 0.2:
                            x = (x - x % y) + y
                        else:
                            x = x - x % y
                    cache[specification_code]["projected_purchase"] = x
                cache[specification_code]["weight_total"] = float("{:.3f}".format((cache[specification_code]["weight"] * cache[specification_code]["projected_purchase"]) / 1e3))
                cache[specification_code]["volume_total"] = float("{:.3f}".format((cache[specification_code]["volume"] * cache[specification_code]["projected_purchase"]) / 1e3))

        for _, v in cache.items():
            if len(v.keys()) == 20:
                preview_table.append(v)
        if len(preview_table) > 0:
            response_object = {"status": "success"}
            response_object["preview_table"] = preview_table
            return jsonify(response_object)
        else:
            response_object = {"status": "not found"}
            return jsonify(response_object)
    else:
        response_object = {"status": "not found"}
        return jsonify(response_object)


# 预下载"采购辅助分析报表"的接口
@blueprint.route("/api/v1/case5/prepare", methods=["POST"])
@cost_count
def prepare_report_file_case5():
    payload = request.get_json()
    time_quantum_x = int(payload.get("time_quantum_x", "6"))
    time_quantum_y = int(payload.get("time_quantum_y", "12"))
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = generate_digest("采购辅助分析报表_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "采购辅助分析报表_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "规格编码", "品牌", "商品名称", "规格名称", "供应商",
            "{}个月销量".format(time_quantum_x), "{}个月折算销量".format(time_quantum_x),
            "{}个月销量".format(time_quantum_y), "{}个月折算销量".format(time_quantum_y),
            "库存量", "库存/{}个月销量".format(time_quantum_x),
            "库存/{}个月销量".format(time_quantum_y), "拟定进货量",
            "单个重量/g", "小计重量/kg", "单个体积/cm³", "小计体积/m³"
        ])
        for item in preview_table:
            csv_writer.writerow([
                item["specification_code"], item["brand"], item["product_name"], item["specification_name"], item["supplier_name"],
                item["sale_qty_x_months"], item["reduced_sale_qty_x_months"], item["sale_qty_y_months"], item["reduced_sale_qty_y_months"],
                item["inventory"], item["inventory_divided_by_sale_qty_x_months"], item["inventory_divided_by_sale_qty_y_months"], item["projected_purchase"],
                item["weight"], item["weight_total"], item["volume"], item["volume_total"],
            ])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)
