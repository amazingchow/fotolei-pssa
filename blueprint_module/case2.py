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

商品编码 | 规格编码	| 商品名称 | 规格名称 | 起始库存数量 | 采购数量	| 销售数量 | 截止库存数量 | 实时可用库存

其中
* 起始库存数量 = 时间段内第一个月的数量
* 采购数量 = 时间段内每一个月的数量的累加
* 销售数量 = 时间段内每一个月的数量的累加
* 截止库存数量 = 时间段内最后一个月的数量
'''


# 预览"销售报表（按系列汇总）"的接口
@blueprint.route("/api/v1/case2/preview", methods=["POST"])
@cost_count
def preview_report_file_case2():
    payload = request.get_json()
    # 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        response_object = {"status": "not found"}
        return jsonify(response_object)

    stmt = "SELECT specification_code, product_series, jit_inventory FROM ggfilm.products WHERE COALESCE(CHAR_LENGTH(product_series), 0) != 0;"
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0:
        lookup_table = {}  # product_series -> [(specification_code, jit_inventory)]
        for ret in rets:
            if ret[1] in lookup_table.keys():
                lookup_table[ret[1]].append((ret[0], ret[2]))
            else:
                lookup_table[ret[1]] = [(ret[0], ret[2])]

        cache = {}
        for k, v in lookup_table.items():
            product_series = k
            cache[product_series] = {
                "product_series": product_series,
                "st_inventory_qty": 0,
                "st_inventory_total": 0,
                "purchase_qty": 0,
                "purchase_total": 0,
                "purchase_then_return_qty": 0,
                "purchase_then_return_total": 0,
                "sale_qty": 0,
                "sale_total": 0,
                "sale_then_return_qty": 0,
                "sale_then_return_total": 0,
                "others_qty": 0,
                "others_total": 0,
                "ed_inventory_qty": 0,
                "ed_inventory_total": 0,
                "jit_inventory": 0,
            }
            do_update = False

            for vv in v:
                specification_code = vv[0]
                jit_inventory = vv[1]
                cache[product_series]["jit_inventory"] += jit_inventory

                stmt = "SELECT * FROM ggfilm.inventories WHERE specification_code = '{}' AND create_time >= '{}' AND create_time <= '{}';".format(
                    specification_code, st_date, ed_date
                )
                inner_rets = db_connector.query(stmt)
                if type(inner_rets) is list and len(inner_rets) > 0:
                    do_update = True

                    cache[product_series]["st_inventory_qty"] += inner_rets[0][5]
                    cache[product_series]["st_inventory_total"] += inner_rets[0][6]
                    cache[product_series]["ed_inventory_qty"] += inner_rets[len(inner_rets) - 1][17]
                    cache[product_series]["ed_inventory_total"] += inner_rets[len(inner_rets) - 1][18]
                    cache[product_series]["purchase_qty"] += sum([inner_ret[7] for inner_ret in inner_rets])
                    cache[product_series]["purchase_total"] += sum([inner_ret[8] for inner_ret in inner_rets])
                    cache[product_series]["purchase_then_return_qty"] += sum([inner_ret[9] for inner_ret in inner_rets])
                    cache[product_series]["purchase_then_return_total"] += sum([inner_ret[10] for inner_ret in inner_rets])
                    cache[product_series]["sale_qty"] += sum([inner_ret[11] for inner_ret in inner_rets])
                    cache[product_series]["sale_total"] += sum([inner_ret[12] for inner_ret in inner_rets])
                    cache[product_series]["sale_then_return_qty"] += sum([inner_ret[13] for inner_ret in inner_rets])
                    cache[product_series]["sale_then_return_total"] += sum([inner_ret[14] for inner_ret in inner_rets])
                    cache[product_series]["others_qty"] += sum([inner_ret[15] for inner_ret in inner_rets])
                    cache[product_series]["others_total"] += sum([inner_ret[16] for inner_ret in inner_rets])
            if not do_update:
                del cache[product_series]

        if len(cache.keys()) == 0:
            response_object = {"status": "not found"}
            return jsonify(response_object)

        preview_table = []
        for k, v in cache.items():
            preview_table.append(v)

        response_object = {"status": "success"}
        response_object["preview_table"] = preview_table
        return jsonify(response_object)
    else:
        response_object = {"status": "not found"}
        return jsonify(response_object)


# 预下载"销售报表（按系列汇总）"的接口
@blueprint.route("/api/v1/case2/prepare", methods=["POST"])
@cost_count
def prepare_report_file_case2():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = generate_digest("销售报表（按系列汇总）_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "销售报表（按系列汇总）_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "产品系列", "起始库存数量", "起始库存总额", "采购数量",
            "采购总额", "采购退货数量", "采购退货总额", "销售数量",
            "销售总额", "销售退货数量", "销售退货总额", "其他变更数量",
            "其他变更总额", "截止库存数量", "截止库存总额", "实时可用库存",
        ])

        for item in preview_table:
            csv_writer.writerow([
                item["product_series"], item["st_inventory_qty"], item["st_inventory_total"], item["purchase_qty"],
                item["purchase_total"], item["purchase_then_return_qty"], item["purchase_then_return_total"], item["sale_qty"],
                item["sale_total"], item["sale_then_return_qty"], item["sale_then_return_total"], item["others_qty"],
                item["others_total"], item["ed_inventory_qty"], item["ed_inventory_total"], item["jit_inventory"],
            ])

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)
