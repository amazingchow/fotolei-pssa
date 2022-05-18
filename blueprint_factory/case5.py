# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import pendulum
import shelve
import time

from flask import current_app
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
from utils import util_generate_digest
from utils import util_get_all_months_between_two_months
from utils import util_remove_duplicates_for_list


case5_blueprint = Blueprint(
    name="fotolei_pssa_case5_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/case5",
)


'''
预览效果

规格编码 | 品牌 | 分类1 | 分类2 | 商品名称 | 规格名称 | 采购名称 | 供应商 | X个月销量 | Y个月销量 | 库存量 | 库存/X个月销量 | 库存/Y个月销量 |
库存/X个月折算销量 | 库存/Y个月折算销量	| 拟定进货量 | 单价 | 金额 | 单个重量/g | 小计重量/kg | 单个体积/cm³ | 小计体积/m³
'''


# 预览"采购辅助分析报表"的接口
@case5_blueprint.route("/preview", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def preview_report_file_case5():
    screening_way = request.args.get("way", "1")
    payload = request.get_json()
    supplier_name = payload.get("supplier_name", "").lower()

    supplier_name_list_from_screening_way1 = []
    if screening_way == "2":
        if len(supplier_name) == 0:
            supplier_name_list_from_screening_way1 = payload.get("supplier_name_list_from_screening_way1", [])
            if len(supplier_name_list_from_screening_way1) == 0:
                return make_response(
                    jsonify({"message": "invalid operation"}),
                    StatusCode.HTTP_400_BAD_REQUEST
                )

    # 过去X个月
    time_quantum_in_month_x = int(payload.get("time_quantum_x", "6"))
    # 过去X个月的库销比
    threshold_x = float(payload.get("threshold_x", "2.0"))
    # 过去Y个月
    time_quantum_in_month_y = int(payload.get("time_quantum_y", "12"))
    # 过去Y个月的库销比
    threshold_y = float(payload.get("threshold_y", "1.0"))
    # 拟定进货（月数）
    projected_purchase_months = int(payload.get("projected_purchase", "12"))
    # 断货折算
    reduced_btn_option = payload.get("reduced_btn_option", True)
    stop_status = payload.get("stop_status", "全部")
    be_aggregated = payload.get("be_aggregated", "全部")

    today = pendulum.today()
    the_past_x_month = today.subtract(months=time_quantum_in_month_x).strftime("%Y-%m")
    the_past_y_month = today.subtract(months=time_quantum_in_month_y).strftime("%Y-%m")

    # “供应商”选项为空，则为全部供应商（包括没有供应商的商品条目）
    stmt = "SELECT specification_code, brand, product_name, specification_name, purchase_name, supplier_name, \
jit_inventory, product_weight, product_length, product_width, product_height, moq, unit_price, classification_1, classification_2 FROM fotolei_pssa.products"
    conds = []
    if len(supplier_name) > 0:
        conds.append("supplier_name = '{}'".format(supplier_name))
    else:
        if screening_way == "2":
            conds.append("supplier_name IN ('{}')".format("', '".join(supplier_name_list_from_screening_way1)))
    if stop_status != "全部":
        conds.append("stop_status = '{}'".format(stop_status))
    if be_aggregated != "全部":
        conds.append("be_aggregated = '{}'".format(be_aggregated))
    stmt_suffix = " AND ".join(conds)
    if len(stmt_suffix) > 0:
        stmt = stmt + " WHERE " + stmt_suffix + " AND is_combined = '否';"
    else:
        stmt = stmt + " WHERE is_combined = '否';"

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
            cache[specification_code]["classification_1"] = ret[13]
            cache[specification_code]["classification_2"] = ret[14]
            cache[specification_code]["product_name"] = ret[2]
            cache[specification_code]["specification_name"] = ret[3]
            cache[specification_code]["purchase_name"] = ret[4]
            cache[specification_code]["supplier_name"] = ret[5]
            cache[specification_code]["inventory"] = ret[6]
            cache[specification_code]["weight"] = ret[7]
            cache[specification_code]["volume"] = ret[8] * ret[9] * ret[10]
            cache[specification_code]["moq"] = ret[11]
            cache[specification_code]["unit_price"] = ret[12]

    if len(specification_code_list) > 0:
        inventories_import_date_record_table = shelve.open("{}/fotolei-pssa/tmp-files/inventories_import_date_record_table".format(
            os.path.expanduser("~")), flag="c", writeback=False)
        real_specification_code_list = []
        for specification_code in specification_code_list:
            v = inventories_import_date_record_table.get(specification_code, [])
            if len(v) == 0:
                # 从未录过进销存报表的商品, 直接忽略
                del cache[specification_code]
            else:
                real_specification_code_list.append(specification_code)

        if screening_way == "1":
            current_app.logger.info("筛选1, 满足条件的SKU数量等于{}".format(len(real_specification_code_list)))
        else:
            current_app.logger.info("筛选2, 满足条件的SKU数量等于{}".format(len(real_specification_code_list)))

        for specification_code in real_specification_code_list:
            v = inventories_import_date_record_table.get(specification_code, [])

            process_sale_qty(cache, specification_code, the_past_x_month, time_quantum_in_month_x, True, reduced_btn_option, v[0])
            process_sale_qty(cache, specification_code, the_past_y_month, time_quantum_in_month_y, False, reduced_btn_option, v[0])
            if cache[specification_code]["sale_qty_x_months"] == 0 and cache[specification_code]["sale_qty_y_months"] == 0:
                if screening_way == "1":
                    if cache[specification_code]["inventory"] > 0:
                        del cache[specification_code]
                        continue
                    else:
                        cache[specification_code]["projected_purchase"] = 0
                        cache[specification_code]["price_total"] = 0.0
                        cache[specification_code]["weight_total"] = 0.0
                        cache[specification_code]["volume_total"] = 0.0
                else:
                    cache[specification_code]["projected_purchase"] = 0
                    cache[specification_code]["price_total"] = 0.0
                    cache[specification_code]["weight_total"] = 0.0
                    cache[specification_code]["volume_total"] = 0.0
            else:
                # 计算拟定进货量
                x1 = 0.0
                x2 = 0.0
                x3 = 0
                x4 = 0
                if reduced_btn_option:
                    if type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"]) is float:
                        x1 = cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"]
                        x3 = cache[specification_code]["reduced_sale_qty_x_months"]
                    if type(cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"]) is float:
                        x2 = cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"]
                        x4 = cache[specification_code]["reduced_sale_qty_y_months"]
                else:
                    if type(cache[specification_code]["inventory_divided_by_sale_qty_x_months"]) is float:
                        x1 = cache[specification_code]["inventory_divided_by_sale_qty_x_months"]
                        x3 = cache[specification_code]["sale_qty_x_months"]
                    if type(cache[specification_code]["inventory_divided_by_sale_qty_y_months"]) is float:
                        x2 = cache[specification_code]["inventory_divided_by_sale_qty_y_months"]
                        x4 = cache[specification_code]["sale_qty_y_months"]
                if screening_way == "1":
                    if x4 > 0 and x2 <= threshold_y:
                        tmp = int((x4 / time_quantum_in_month_y) * projected_purchase_months)
                        cache[specification_code]["projected_purchase"] = tmp - cache[specification_code]["inventory"]
                        if cache[specification_code]["projected_purchase"] < 0:
                            cache[specification_code]["projected_purchase"] = 0
                    elif x3 > 0 and x1 <= threshold_x:
                        tmp = int((x3 / time_quantum_in_month_x) * projected_purchase_months)
                        cache[specification_code]["projected_purchase"] = tmp - cache[specification_code]["inventory"]
                        if cache[specification_code]["projected_purchase"] < 0:
                            cache[specification_code]["projected_purchase"] = 0
                    else:
                        del cache[specification_code]
                        continue
                else:
                    tmp = int((x4 / time_quantum_in_month_y) * projected_purchase_months)
                    cache[specification_code]["projected_purchase"] = tmp - cache[specification_code]["inventory"]
                    if cache[specification_code]["projected_purchase"] <= 0:
                        tmp = int((x3 / time_quantum_in_month_x) * projected_purchase_months)
                        cache[specification_code]["projected_purchase"] = tmp - cache[specification_code]["inventory"]
                        if cache[specification_code]["projected_purchase"] < 0:
                            cache[specification_code]["projected_purchase"] = 0
                if cache[specification_code]["projected_purchase"] == 0:
                    cache[specification_code]["price_total"] = 0.0
                    cache[specification_code]["weight_total"] = 0.0
                    cache[specification_code]["volume_total"] = 0.0
                else:
                    if cache[specification_code]["moq"] > 1:
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
                    cache[specification_code]["price_total"] = float("{:.2f}".format(cache[specification_code]["unit_price"] * cache[specification_code]["projected_purchase"]))
                    cache[specification_code]["weight_total"] = float("{:.3f}".format((cache[specification_code]["weight"] * cache[specification_code]["projected_purchase"]) / 1e3))
                    cache[specification_code]["volume_total"] = float("{:.3f}".format((cache[specification_code]["volume"] * cache[specification_code]["projected_purchase"]) / 1e6))
        inventories_import_date_record_table.close()

        preview_table = []
        for _, v in cache.items():
            if v["inventory"] < 0:
                v["inventory_divided_by_sale_qty_x_months"] = "#DIV/0!"
                v["inventory_divided_by_reduced_sale_qty_x_months"] = "#DIV/0!"
                v["inventory_divided_by_sale_qty_y_months"] = "#DIV/0!"
                v["inventory_divided_by_reduced_sale_qty_y_months"] = "#DIV/0!"
            preview_table.append(v)
            if screening_way == "1" and len(supplier_name) == 0:
                supplier_name_list_from_screening_way1.append(v["supplier_name"])
                supplier_name_list_from_screening_way1 = util_remove_duplicates_for_list(supplier_name_list_from_screening_way1)
        if screening_way == "1":
            current_app.logger.info("筛选1, 输出的SKU数量等于{}".format(len(preview_table)))
        else:
            current_app.logger.info("筛选2, 输出的SKU数量等于{}".format(len(preview_table)))

        if len(preview_table) > 0:
            if len(supplier_name) == 0:
                preview_table.sort(key=lambda x: x["supplier_name"], reverse=False)

        role = session.get("role", ROLE_TYPE_ORDINARY_USER)
        if role > ROLE_TYPE_ADMIN:
            # 针对普通用户，对敏感数据(起始库存总额、采购总额、采购退货总额、其他变更总额、截止库存总额、单价、金额)做脱敏处理
            for idx in range(len(preview_table)):
                preview_table[idx]["unit_price"] = "*"
                preview_table[idx]["price_total"] = "*"

        response_object = {"message": ""}
        response_object["preview_table"] = preview_table
        response_object["supplier_name_list_from_screening_way1"] = supplier_name_list_from_screening_way1
        return make_response(
            jsonify(response_object),
            StatusCode.HTTP_200_OK
        )

    return make_response(
        jsonify({"message": ""}),
        StatusCode.HTTP_404_NOT_FOUND
    )


# 预下载"采购辅助分析报表"的接口
@case5_blueprint.route("/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_EXPORT)
@cost_count
def prepare_report_file_case5():
    payload = request.get_json()
    time_quantum_x = int(payload.get("time_quantum_x", "6"))
    time_quantum_y = int(payload.get("time_quantum_y", "12"))
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("采购辅助分析报表_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "采购辅助分析报表_{}.csv".format(ts)
    with open(csv_file, "w", encoding="utf-8-sig") as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        csv_writer.writerow([
            "规格编码", "品牌", "分类1", "分类2",
            "商品名称", "规格名称", "采购名称", "供应商",
            "{}个月销量".format(time_quantum_x), "{}个月折算销量".format(time_quantum_x),
            "{}个月销量".format(time_quantum_y), "{}个月折算销量".format(time_quantum_y),
            "库存量",
            "库存/{}个月销量".format(time_quantum_x), "库存/{}个月折算销量".format(time_quantum_x),
            "库存/{}个月销量".format(time_quantum_y), "库存/{}个月折算销量".format(time_quantum_y),
            "拟定进货量", "单价", "金额", "单个重量/g", "小计重量/kg", "单个体积/cm³", "小计体积/m³",
            "备注",
        ])
        for item in preview_table:
            csv_writer.writerow([
                item["specification_code"], item["brand"], item["classification_1"], item["classification_2"],
                item["product_name"], item["specification_name"], item["purchase_name"], item["supplier_name"],
                item["sale_qty_x_months"], item["reduced_sale_qty_x_months"],
                item["sale_qty_y_months"], item["reduced_sale_qty_y_months"],
                item["inventory"],
                item["inventory_divided_by_sale_qty_x_months"], item["inventory_divided_by_reduced_sale_qty_x_months"],
                item["inventory_divided_by_sale_qty_y_months"], item["inventory_divided_by_reduced_sale_qty_y_months"],
                item["projected_purchase"], item["unit_price"], item["price_total"], item["weight"], item["weight_total"], item["volume"], item["volume_total"],
                item["remark"],
            ])

    session["op_object"] = output_file

    response_object = {"message": ""}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return make_response(
        jsonify(response_object),
        StatusCode.HTTP_200_OK
    )


def process_sale_qty(g_cache, specification_code, the_past_m_month, the_time_quantum, is_the_past_x_month, reduced_btn_option, first_import_date):
    stmt = "SELECT st_inventory_qty, ed_inventory_qty, purchase_qty, sale_qty, sale_then_return_qty, create_time \
FROM fotolei_pssa.inventories WHERE specification_code = '{}' AND create_time >= '{}' \
ORDER BY create_time ASC;".format(specification_code, the_past_m_month)
    rets = db_connector.query(stmt)
    if type(rets) is list:
        if len(rets) == 0:
            # 这段时间无任何进销存数据，但库存不一定为零
            if is_the_past_x_month:
                g_cache[specification_code]["sale_qty_x_months"] = 0
                g_cache[specification_code]["reduced_sale_qty_x_months"] = 0
                g_cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                if g_cache[specification_code]["inventory"] <= 0:
                    g_cache[specification_code]["remark"] = "过去{}个月无进销存数据，当前库存为零".format(the_time_quantum)
                else:
                    g_cache[specification_code]["remark"] = "过去{}个月无进销存数据".format(the_time_quantum)
            else:
                g_cache[specification_code]["sale_qty_y_months"] = 0
                g_cache[specification_code]["reduced_sale_qty_y_months"] = 0
                g_cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                if len(g_cache[specification_code].get("remark", "")) > 0:
                    if g_cache[specification_code]["inventory"] <= 0:
                        g_cache[specification_code]["remark"] = g_cache[specification_code]["remark"] + "/过去{}个月无进销存数据，当前库存为零".format(the_time_quantum)
                    else:
                        g_cache[specification_code]["remark"] = g_cache[specification_code]["remark"] + "/过去{}个月无进销存数据".format(the_time_quantum)
                else:
                    if g_cache[specification_code]["inventory"] <= 0:
                        g_cache[specification_code]["remark"] = "过去{}个月无进销存数据，当前库存为零".format(the_time_quantum)
                    else:
                        g_cache[specification_code]["remark"] = "过去{}个月无进销存数据".format(the_time_quantum)
        else:
            # Tips: 数据是倒排的, 2021-11 -> 2021-10 -> ... -> 2020-12
            # 计算M个月销量
            if is_the_past_x_month:
                g_cache[specification_code]["sale_qty_x_months"] = sum(ret[3] for ret in rets) - sum(ret[4] for ret in rets)
                if g_cache[specification_code]["sale_qty_x_months"] <= 0:
                    if g_cache[specification_code]["sale_qty_x_months"] == 0:
                        if g_cache[specification_code]["inventory"] <= 0:
                            g_cache[specification_code]["remark"] = "过去{}个月销量为零，当前库存为零".format(the_time_quantum)
                        else:
                            g_cache[specification_code]["remark"] = "过去{}个月销量为零".format(the_time_quantum)
                    else:
                        if g_cache[specification_code]["inventory"] <= 0:
                            g_cache[specification_code]["remark"] = "过去{}个月销量为负，当前库存为零".format(the_time_quantum)
                        else:
                            g_cache[specification_code]["remark"] = "过去{}个月销量为负".format(the_time_quantum)
                    g_cache[specification_code]["sale_qty_x_months"] = 0
                    g_cache[specification_code]["reduced_sale_qty_x_months"] = 0
                    g_cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                    g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                    return
            else:
                g_cache[specification_code]["sale_qty_y_months"] = sum(ret[3] for ret in rets) - sum(ret[4] for ret in rets)
                if g_cache[specification_code]["sale_qty_y_months"] <= 0:
                    if g_cache[specification_code]["sale_qty_y_months"] == 0:
                        if len(g_cache[specification_code].get("remark", "")) > 0:
                            if g_cache[specification_code]["inventory"] <= 0:
                                g_cache[specification_code]["remark"] = g_cache[specification_code]["remark"] + "/过去{}个月销量为零，当前库存为零".format(the_time_quantum)
                            else:
                                g_cache[specification_code]["remark"] = g_cache[specification_code]["remark"] + "/过去{}个月销量为零".format(the_time_quantum)
                        else:
                            if g_cache[specification_code]["inventory"] <= 0:
                                g_cache[specification_code]["remark"] = "过去{}个月销量为零，当前库存为零".format(the_time_quantum)
                            else:
                                g_cache[specification_code]["remark"] = "过去{}个月销量为零".format(the_time_quantum)
                    else:
                        if len(g_cache[specification_code].get("remark", "")) > 0:
                            if g_cache[specification_code]["inventory"] <= 0:
                                g_cache[specification_code]["remark"] = g_cache[specification_code]["remark"] + "/过去{}个月销量为负，当前库存为零".format(the_time_quantum)
                            else:
                                g_cache[specification_code]["remark"] = g_cache[specification_code]["remark"] + "/过去{}个月销量为负".format(the_time_quantum)
                        else:
                            if g_cache[specification_code]["inventory"] <= 0:
                                g_cache[specification_code]["remark"] = "过去{}个月销量为负，当前库存为零".format(the_time_quantum)
                            else:
                                g_cache[specification_code]["remark"] = "过去{}个月销量为负".format(the_time_quantum)
                    g_cache[specification_code]["sale_qty_y_months"] = 0
                    g_cache[specification_code]["reduced_sale_qty_y_months"] = 0
                    g_cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                    g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = "{}/0".format(g_cache[specification_code]["inventory"])
                    return

            if len(g_cache[specification_code].get("remark", "")) == 0:
                g_cache[specification_code]["remark"] = ""

            # M个月销量为正，计算M个月折算销量
            if reduced_btn_option:
                # the_past_m_month : 过去M个月的那个月份, 比如2021-07
                # first_import_date : 对于某个产品, 第一次导入进销存数据的月份, 比如2020-10或2021-09
                # first_import_date可能早于the_past_m_month, 也可能晚于the_past_m_month
                # NOTE: 开始核心计算部分
                all_months = []
                if first_import_date <= the_past_m_month:
                    # first_import_date早于the_past_m_month的情况, 不用做特殊处理
                    all_months = util_get_all_months_between_two_months(the_past_m_month, pendulum.today().strftime("%Y-%m"))
                else:
                    # first_import_date晚于the_past_m_month的情况, 要做特殊处理
                    all_months = util_get_all_months_between_two_months(first_import_date, pendulum.today().strftime("%Y-%m"))

                reduced_months = 0
                # 计算断货折算月份
                i = 0
                j = 0
                while j < len(all_months):
                    if i == 0:
                        # 判断下捞出来的进销存数据首个月的起始库存是否为零，如果不为零，那之前的月份不该算进断货月份
                        while all_months[j] < rets[i][5]:
                            if rets[i][0] <= 0:
                                reduced_months += 1
                            j += 1
                        if rets[i][0] <= 0 and rets[i][1] <= 0:
                            if (rets[i][2] > 0 and rets[i][2] <= 10) and (rets[i][2] <= (rets[i][3] - rets[i][4])):
                                reduced_months += 1
                            elif (rets[i][2] > 10) and (rets[i][2] > (rets[i][3] - rets[i][4])):
                                reduced_months += 1
                        i += 1
                        if i == len(rets):
                            i = len(rets) - 1
                        j += 1
                    else:
                        if all_months[j] < rets[i][5]:
                            if rets[i][0] <= 0:
                                reduced_months += 1
                            j += 1
                        elif all_months[j] == rets[i][5]:
                            if rets[i][0] == 0 and rets[i][1] == 0:
                                if (rets[i][2] > 0 and rets[i][2] <= 10) and (rets[i][2] <= (rets[i][3] - rets[i][4])):
                                    reduced_months += 1
                                elif (rets[i][2] > 10) and (rets[i][2] > (rets[i][3] - rets[i][4])):
                                    reduced_months += 1
                            i += 1
                            if i == len(rets):
                                i = len(rets) - 1
                            j += 1
                        elif all_months[j] > rets[i][5]:
                            if rets[i][1] <= 0:
                                reduced_months += 1
                            j += 1
                # NOTE: 结束核心计算部分
                current_app.logger.info("specification code: {}, reduced months: {}".format(specification_code, reduced_months))
                if is_the_past_x_month:
                    g_cache[specification_code]["reduced_sale_qty_x_months"] = int(g_cache[specification_code]["sale_qty_x_months"] * (len(all_months) / (len(all_months) - reduced_months)))
                else:
                    g_cache[specification_code]["reduced_sale_qty_y_months"] = int(g_cache[specification_code]["sale_qty_y_months"] * (len(all_months) / (len(all_months) - reduced_months)))
            else:
                if is_the_past_x_month:
                    g_cache[specification_code]["reduced_sale_qty_x_months"] = g_cache[specification_code]["sale_qty_x_months"]
                else:
                    g_cache[specification_code]["reduced_sale_qty_y_months"] = g_cache[specification_code]["sale_qty_y_months"]

            # 计算库存/M个月销量 + 库存/M个月折算销量
            if g_cache[specification_code]["inventory"] <= 0:
                if is_the_past_x_month:
                    g_cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = 0.0
                    g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = 0.0
                else:
                    g_cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = 0.0
                    g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = 0.0
                    g_cache[specification_code]["remark"] = "过去{}个月销量为正，但是当前库存为零".format(the_time_quantum)
            else:
                if is_the_past_x_month:
                    g_cache[specification_code]["inventory_divided_by_sale_qty_x_months"] = \
                        float("{:.3f}".format(g_cache[specification_code]["inventory"] / g_cache[specification_code]["sale_qty_x_months"]))
                    g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_x_months"] = \
                        float("{:.3f}".format(g_cache[specification_code]["inventory"] / g_cache[specification_code]["reduced_sale_qty_x_months"]))
                else:
                    g_cache[specification_code]["inventory_divided_by_sale_qty_y_months"] = \
                        float("{:.3f}".format(g_cache[specification_code]["inventory"] / g_cache[specification_code]["sale_qty_y_months"]))
                    g_cache[specification_code]["inventory_divided_by_reduced_sale_qty_y_months"] = \
                        float("{:.3f}".format(g_cache[specification_code]["inventory"] / g_cache[specification_code]["reduced_sale_qty_y_months"]))
    return
