# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath("../db"))
sys.path.append(os.path.abspath("../utils"))

import csv
import shelve
import time

from collections import defaultdict

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import session

from .decorator_factory import has_logged_in
from .decorator_factory import restrict_access
from .decorator_factory import cost_count
from .decorator_factory import record_action
from db import db_connector
from utils import ACTION_TYPE_EXPORT
from utils import ACTION_TYPE_UPDATE_ONE
from utils import get_lookup_table_k_brand_v_brand_c2
from utils import get_lookup_table_k_brand_v_brand_c2_keys
from utils import get_lookup_table_k_c1_v_c1_c2
from utils import get_lookup_table_k_c1_v_c1_c2_keys
from utils import REG_POSITIVE_INT
from utils import ROLE_TYPE_ORDINARY_USER
from utils import ROLE_TYPE_SUPER_ADMIN
from utils import util_generate_digest


case1_blueprint = Blueprint(
    name="fotolei_pssa_case1_blueprint",
    import_name=__name__,
    url_prefix="/api/v1/case1",
)


# 获取自定义UI
@case1_blueprint.route("/ui/fetch", methods=["GET"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def fetch_ui():
    customize_report_forms_ui = shelve.open("{}/fotolei-pssa/tmp-files/customize_report_forms_ui".format(
        os.path.expanduser("~")), flag='c', writeback=False)
    ui = dict()
    for k, v in customize_report_forms_ui.items():
        ui[k] = v
    customize_report_forms_ui.close()
    response_object = {"status": "success"}
    response_object["ui"] = ui
    return jsonify(response_object)


# 保存自定义UI
@case1_blueprint.route("/ui/save", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_SUPER_ADMIN)
@record_action(action=ACTION_TYPE_UPDATE_ONE)
@cost_count
def save_ui():
    payload = request.get_json()
    classification1_tags = payload.get("classification1_tags", [])
    classification1_classification2_tags = payload.get("classification1_classification2_tags", [])
    classification1_topk_tags = payload.get("classification1_topk_tags", [])
    brand_tags = payload.get("brand_tags", [])
    brand_topk_tag = payload.get("brand_topk_tag", '')
    brand_classification2_tags = payload.get("brand_classification2_tags", [])

    customize_report_forms_ui = shelve.open("{}/fotolei-pssa/tmp-files/customize_report_forms_ui".format(
        os.path.expanduser("~")), flag='c', writeback=False)
    customize_report_forms_ui["classification1_tags"] = classification1_tags
    customize_report_forms_ui["classification1_classification2_tags"] = classification1_classification2_tags
    customize_report_forms_ui["classification1_topk_tags"] = classification1_topk_tags
    customize_report_forms_ui["brand_tags"] = brand_tags
    customize_report_forms_ui["brand_topk_tag"] = brand_topk_tag
    customize_report_forms_ui["brand_classification2_tags"] = brand_classification2_tags
    customize_report_forms_ui.close()

    session["op_object"] = "销售报表（按分类汇总）输出格式"
    response_object = {"status": "success"}
    return jsonify(response_object)


'''
预览效果

202X年XX月~202X年XX月
-------------------------------------------------------------------
总销售额		          占比
-------------------------------------------------------------------
龟龟销售额
-------------------------------------------------------------------
2店销售额
-------------------------------------------------------------------
数码类目销售额
-------------------------------------------------------------------
背带
数码/包&收纳
数码/快挂
-------------------------------------------------------------------
传统类目销售额
-------------------------------------------------------------------
暗房冲洗设备
胶片
页片
相纸
彩色药水
黑白药水
底片收纳保护
翻拍器
放大机类
胶片相机
机械快门线/纽
-------------------------------------------------------------------
各品牌销售额
-------------------------------------------------------------------
巅峰设计
cam-in
poilotfoto
-------------------------------------------------------------------
各品牌-分类2销售额
-------------------------------------------------------------------
伊尔福-黑白药水
伊尔福-相纸
'''


# 预览"销售报表（按分类汇总）"的接口
@case1_blueprint.route("/preview", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@cost_count
def preview_report_file_case1():
    payload = request.get_json()
    # 起始日期和截止日期用于过滤掉时间条件不符合的记录项
    st_date = payload.get("st_date", "").strip()
    ed_date = payload.get("ed_date", "").strip()
    if (st_date > ed_date):
        response_object = {"status": "not found"}
        return jsonify(response_object)

    ui_classification1_tags = payload.get("ui_classification1_tags", [])
    ui_classification1_tags = [tag.lower() for tag in ui_classification1_tags]
    for tag in ui_classification1_tags:
        if tag not in get_lookup_table_k_c1_v_c1_c2_keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 参与统计的分类1：{}不存在！".format(tag)
            return jsonify(response_object)

    ui_classification1_classification2_tags = payload.get("ui_classification1_classification2_tags", [])
    ui_classification1_classification2_lookup_table = defaultdict(list)
    for tag in ui_classification1_classification2_tags:
        c1_tag, c2_tag = tag.split("|")
        c1_tag, c2_tag = c1_tag.lower(), c2_tag.lower()
        if c1_tag not in ui_classification1_tags:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 参与统计的分类1|分类2 - 分类1：{}不存在！".format(c1_tag)
            return jsonify(response_object)
        if tag.lower() not in get_lookup_table_k_c1_v_c1_c2(c1_tag):
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 参与统计的分类1|分类2 - 分类2：{}不存在！".format(c2_tag)
            return jsonify(response_object)
        ui_classification1_classification2_lookup_table[c1_tag].append(c2_tag)

    ui_classification1_topk_tags = payload.get("ui_classification1_topk_tags", [])
    ui_classification1_topk_lookup_table = defaultdict(int)
    for tag in ui_classification1_topk_tags:
        c1_tag, topk_tag = tag.split("|")
        c1_tag = c1_tag.lower()
        if c1_tag not in ui_classification1_tags:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 销售top必选（分类1）- 分类1：{}不存在！".format(c1_tag)
            return jsonify(response_object)
        if not topk_tag.startswith("top"):
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 销售top必选（分类1）- topk：{}格式不正确！".format(topk_tag)
            return jsonify(response_object)
        topk = topk_tag.lstrip("top")
        if REG_POSITIVE_INT.match(topk) is None:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 销售top必选（分类1）- topk：{}格式不正确！".format(topk_tag)
            return jsonify(response_object)
        if int(topk) > len(get_lookup_table_k_c1_v_c1_c2(c1_tag)):
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 销售top必选（分类1）- topk：{}超过最大值top{}".format(
                topk_tag, len(get_lookup_table_k_c1_v_c1_c2(c1_tag)))
            return jsonify(response_object)
        ui_classification1_topk_lookup_table[c1_tag] = int(topk)

    ui_brand_tags = payload.get("ui_brand_tags", [])
    ui_brand_tags = [tag.lower() for tag in ui_brand_tags]
    for tag in ui_brand_tags:
        if tag not in get_lookup_table_k_brand_v_brand_c2_keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 参与统计的品牌：{}不存在！".format(tag)
            return jsonify(response_object)

    ui_brand_topk_tag = payload.get("ui_brand_topk_tag", "")
    if not ui_brand_topk_tag.startswith("top"):
        response_object = {"status": "invalid tag"}
        response_object["err_msg"] = "输入ui参数错误 - 销售top必选（品牌）- topk：{}格式不正确！".format(ui_brand_topk_tag)
        return jsonify(response_object)
    brand_topk = ui_brand_topk_tag.lstrip("top")
    if REG_POSITIVE_INT.match(brand_topk) is None:
        response_object = {"status": "invalid tag"}
        response_object["err_msg"] = "输入ui参数错误 - 销售top必选（品牌）- topk：{}格式不正确！".format(ui_brand_topk_tag)
        return jsonify(response_object)
    if int(brand_topk) > len(get_lookup_table_k_brand_v_brand_c2_keys()):
        response_object = {"status": "invalid tag"}
        response_object["err_msg"] = "输入ui参数错误 - 销售top必选（分类1）- topk：{}超过最大值top{}".format(
            ui_brand_topk_tag, len(get_lookup_table_k_brand_v_brand_c2_keys()))
        return jsonify(response_object)

    ui_brand_classification2_tags = payload.get("ui_brand_classification2_tags", [])
    ui_brand_classification2_tags_table = []
    for tag in ui_brand_classification2_tags:
        brand_tag, c2_tag = tag.split("|")
        brand_tag, c2_tag = brand_tag.lower(), c2_tag.lower()
        if brand_tag not in get_lookup_table_k_brand_v_brand_c2_keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 参与统计的品牌|分类2 - 品牌：{}不存在！".format(brand_tag)
            return jsonify(response_object)
        if tag not in get_lookup_table_k_brand_v_brand_c2(brand_tag):
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "输入ui参数错误 - 参与统计的品牌|分类2 - 分类2：{}不存在！".format(c2_tag)
            return jsonify(response_object)
        ui_brand_classification2_tags_table.append((brand_tag, c2_tag))

    response_object = {"status": "success"}
    preview_table = []
    preview_table.append(["{} ~ {}销售报表".format(st_date, ed_date), "", "占比"])
    # 计算202X年XX月~202X年XX月的总销售额
    stmt = "SELECT SUM(sale_total) as sum_sale_total, SUM(sale_then_return_total) as sum_sale_then_return_total \
FROM fotolei_pssa.inventories WHERE extra_is_combined = '否' AND create_time >= '{}' AND create_time <= '{}';".format(
        st_date, ed_date
    )
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0 and rets[0][0] is not None and rets[0][1] is not None:
        sum_sale_total = rets[0][0]
        sum_sale_then_return_total = rets[0][1]
        preview_table.append(["总销售额", "{:.2f}".format(sum_sale_total - sum_sale_then_return_total), "100%"])
        if "传统耗材" in ui_classification1_tags:
            topk = ui_classification1_topk_lookup_table["传统耗材"]
            # 计算龟龟销售额
            stmt = "SELECT sale_total, sale_then_return_total, extra_classification_2 \
FROM fotolei_pssa.inventories WHERE extra_classification_1 = '传统耗材' AND extra_is_combined = '否' AND create_time >= '{}' AND create_time <= '{}';".format(
                st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                sum_sale_total_for_c1 = sum([ret[0] for ret in rets])
                sum_sale_then_return_total_for_c1 = sum([ret[1] for ret in rets])
                sum_sale_total_for_c1 = sum_sale_total_for_c1 - sum_sale_then_return_total_for_c1
                sum_sale_total_for_c1_percent = sum_sale_total_for_c1 / sum_sale_total * 100
                preview_table.append(["龟龟销售额", "{:.2f}".format(sum_sale_total_for_c1), "{:.2f}%".format(sum_sale_total_for_c1_percent)])
                # 计算传统类目销售额
                preview_table.append(["传统类目销售额", "{:.2f}".format(sum_sale_total_for_c1), "{:.2f}%".format(sum_sale_total_for_c1_percent)])
                tmp_table = []
                if topk <= len(ui_classification1_classification2_lookup_table["传统耗材"]):
                    # 如果选中的待计算项目 >= topk，则直接处理待计算项目
                    for c2_tag in ui_classification1_classification2_lookup_table["传统耗材"]:
                        # 计算分类1为传统耗材，分类2为'c2_tag'的销售额
                        sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_then_return_total_for_c1_c2 = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_total_for_c1_c2 = sum_sale_total_for_c1_c2 - sum_sale_then_return_total_for_c1_c2
                        sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                        tmp_table.append((c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent))
                    tmp_table.sort(key=lambda x: x[1], reverse=True)
                else:
                    # 如果选中的待计算项目 < topk，待计算项目必须被处理且出现在结果中，空位用topk来填充
                    # 获取所有‘分类1‘等于‘传统耗材’的分类2
                    all_c2_tags = []
                    for item in get_lookup_table_k_c1_v_c1_c2_keys("传统耗材"):
                        all_c2_tags.append(item.split("|")[1].strip())
                    for c2_tag in all_c2_tags:
                        sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_then_return_total_for_c1_c2 = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_total_for_c1_c2 = sum_sale_total_for_c1_c2 - sum_sale_then_return_total_for_c1_c2
                        sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                        tmp_table.append((c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent))
                    tmp_table.sort(key=lambda x: x[1], reverse=True)
                    if len(tmp_table) < topk:
                        topk = len(tmp_table)
                    tmp_table = tmp_table[:topk]
                    tmp_tags_table = [item[0] for item in tmp_table]
                    for c2_tag in ui_classification1_classification2_lookup_table["传统耗材"]:
                        found_c2_tag = False
                        for x in tmp_tags_table:
                            if c2_tag == x:
                                found_c2_tag = True
                                break
                        if found_c2_tag:
                            continue
                        sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_then_return_total_for_c1_c2 = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_total_for_c1_c2 = sum_sale_total_for_c1_c2 - sum_sale_then_return_total_for_c1_c2
                        sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                        if sum_sale_total_for_c1_c2 <= tmp_table[topk - 1][1]:
                            tmp_table[topk - 1] = (c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent)
                        elif sum_sale_total_for_c1_c2 >= tmp_table[0][1]:
                            tmp_table[0] = (c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent)
                        else:
                            for i in range(topk - 2, 0, -1):
                                if sum_sale_total_for_c1_c2 <= tmp_table[i][1]:
                                    tmp_table[i] = (c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent)
                                    break
                for item in tmp_table:
                    preview_table.append([item[0], "{:.2f}".format(item[1]), "{:.2f}%".format(item[2])])
        if "数码" in ui_classification1_tags:
            topk = ui_classification1_topk_lookup_table["数码"]
            # 计算2店销售额
            stmt = "SELECT sale_total, sale_then_return_total, extra_classification_2 \
FROM fotolei_pssa.inventories WHERE extra_classification_1 = '数码' AND extra_is_combined = '否' AND create_time >= '{}' AND create_time <= '{}';".format(
                st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                sum_sale_total_for_c1 = sum([ret[0] for ret in rets])
                sum_sale_then_return_total_for_c1 = sum([ret[1] for ret in rets])
                sum_sale_total_for_c1 = sum_sale_total_for_c1 - sum_sale_then_return_total_for_c1
                sum_sale_total_for_c1_percent = sum_sale_total_for_c1 / sum_sale_total * 100
                preview_table.append(["2店销售额", "{:.2f}".format(sum_sale_total_for_c1), "{:.2f}%".format(sum_sale_total_for_c1_percent)])
                # 计算数码类目销售额
                preview_table.append(["数码类目销售额", "{:.2f}".format(sum_sale_total_for_c1), "{:.2f}%".format(sum_sale_total_for_c1_percent)])
                tmp_table = []
                if topk <= len(ui_classification1_classification2_lookup_table["数码"]):
                    # 如果选中的待计算项目 >= topk，则直接处理待计算项目
                    for c2_tag in ui_classification1_classification2_lookup_table["数码"]:
                        # 计算分类1为数码，分类2为'c2_tag'的销售额
                        sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_then_return_total_for_c1_c2 = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_total_for_c1_c2 = sum_sale_total_for_c1_c2 - sum_sale_then_return_total_for_c1_c2
                        sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                        tmp_table.append((c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent))
                    tmp_table.sort(key=lambda x: x[1], reverse=True)
                else:
                    # 如果选中的待计算项目 < topk，待计算项目必须被处理且出现在结果中，空位用topk来填充
                    # 获取所有‘分类1‘等于‘数码’的分类2
                    all_c2_tags = []
                    for item in get_lookup_table_k_c1_v_c1_c2_keys("数码"):
                        all_c2_tags.append(item.split("|")[1].strip())
                    for c2_tag in all_c2_tags:
                        sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_then_return_total_for_c1_c2 = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_total_for_c1_c2 = sum_sale_total_for_c1_c2 - sum_sale_then_return_total_for_c1_c2
                        sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                        tmp_table.append((c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent))
                    tmp_table.sort(key=lambda x: x[1], reverse=True)
                    if len(tmp_table) < topk:
                        topk = len(tmp_table)
                    tmp_table = tmp_table[:topk]
                    tmp_tags_table = [item[0] for item in tmp_table]
                    for c2_tag in ui_classification1_classification2_lookup_table["数码"]:
                        found_c2_tag = False
                        for x in tmp_tags_table:
                            if c2_tag == x:
                                found_c2_tag = True
                                break
                        if found_c2_tag:
                            continue
                        sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_then_return_total_for_c1_c2 = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == c2_tag])
                        sum_sale_total_for_c1_c2 = sum_sale_total_for_c1_c2 - sum_sale_then_return_total_for_c1_c2
                        sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                        if sum_sale_total_for_c1_c2 <= tmp_table[topk - 1][1]:
                            tmp_table[topk - 1] = (c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent)
                        elif sum_sale_total_for_c1_c2 >= tmp_table[0][1]:
                            tmp_table[0] = (c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent)
                        else:
                            for i in range(topk - 2, 0, -1):
                                if sum_sale_total_for_c1_c2 <= tmp_table[i][1]:
                                    tmp_table[i] = (c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent)
                                    break
                for item in tmp_table:
                    preview_table.append([item[0], "{:.2f}".format(item[1]), "{:.2f}%".format(item[2])])
        # 计算各品牌销售额
        preview_table.append(["品牌销售额", "", ""])
        tmp_table = []
        if int(brand_topk) <= len(ui_brand_tags):
            # 如果选中的待计算项目 >= topk，则直接处理待计算项目
            for brand_tag in ui_brand_tags:
                stmt = "SELECT SUM(sale_total) as sum_sale_total, SUM(sale_then_return_total) as sum_sale_then_return_total \
FROM fotolei_pssa.inventories WHERE extra_brand = '{}' AND extra_is_combined = '否' AND create_time >= '{}' AND create_time <= '{}';".format(
                    brand_tag, st_date, ed_date
                )
                rets = db_connector.query(stmt)
                if type(rets) is list and len(rets) > 0 and rets[0][0] is not None and rets[0][1] is not None:
                    sum_sale_total_for_brand = rets[0][0]
                    sum_sale_then_return_total_for_brand = rets[0][1]
                    sum_sale_total_for_brand = sum_sale_total_for_brand - sum_sale_then_return_total_for_brand
                    sum_sale_total_for_brand_percent = sum_sale_total_for_brand / sum_sale_total * 100
                    tmp_table.append((brand_tag, sum_sale_total_for_brand, sum_sale_total_for_brand_percent))
            tmp_table.sort(key=lambda x: x[1], reverse=True)
        else:
            topk = int(brand_topk)
            # 如果选中的待计算项目 < topk，待计算项目必须被处理且出现在结果中，空位用topk来填充
            stmt = "SELECT sale_total, sale_then_return_total, extra_brand \
FROM fotolei_pssa.inventories WHERE extra_is_combined = '否' AND create_time >= '{}' AND create_time <= '{}';".format(
                st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                # 获取所有‘品牌‘
                all_brand_tags = []
                for item in get_lookup_table_k_brand_v_brand_c2_keys():
                    all_brand_tags.append(item)
                for brand_tag in all_brand_tags:
                    sum_sale_total_for_brand = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == brand_tag])
                    sum_sale_then_return_total_for_brand = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == brand_tag])
                    sum_sale_total_for_brand = sum_sale_total_for_brand - sum_sale_then_return_total_for_brand
                    sum_sale_total_for_brand_percent = sum_sale_total_for_brand / sum_sale_total * 100
                    tmp_table.append((brand_tag, sum_sale_total_for_brand, sum_sale_total_for_brand_percent))
                tmp_table.sort(key=lambda x: x[1], reverse=True)
                if len(tmp_table) < topk:
                    topk = len(tmp_table)
                tmp_table = tmp_table[:topk]
                tmp_tags_table = [item[0] for item in tmp_table]
                for brand_tag in ui_brand_tags:
                    found_brand_tag = False
                    for x in tmp_tags_table:
                        if brand_tag == x:
                            found_brand_tag = True
                            break
                    if found_brand_tag:
                        continue
                    sum_sale_total_for_brand = sum([ret[0] for ret in rets if len(ret[2]) > 0 and ret[2] == brand_tag])
                    sum_sale_then_return_total_for_brand = sum([ret[1] for ret in rets if len(ret[2]) > 0 and ret[2] == brand_tag])
                    sum_sale_total_for_brand = sum_sale_total_for_brand - sum_sale_then_return_total_for_brand
                    sum_sale_total_for_brand_percent = sum_sale_total_for_brand / sum_sale_total * 100
                    if sum_sale_total_for_brand <= tmp_table[topk - 1][1]:
                        tmp_table[topk - 1] = (brand_tag, sum_sale_total_for_brand, sum_sale_total_for_brand_percent)
                    elif sum_sale_total_for_brand >= tmp_table[0][1]:
                        tmp_table[0] = (brand_tag, sum_sale_total_for_brand, sum_sale_total_for_brand_percent)
                    else:
                        for i in range(topk - 2, 0, -1):
                            if sum_sale_total_for_brand <= tmp_table[i][1]:
                                tmp_table[i] = (brand_tag, sum_sale_total_for_brand, sum_sale_total_for_brand_percent)
                                break
        for item in tmp_table:
            preview_table.append([item[0], "{:.2f}".format(item[1]), "{:.2f}%".format(item[2])])

        # 计算各品牌-分类2销售额
        if len(ui_brand_classification2_tags_table) > 0:
            preview_table.append(["品牌-分类2销售额", "", ""])
            tmp_table = []
            for brand_tag_classification2_tag in ui_brand_classification2_tags_table:
                stmt = "SELECT SUM(sale_total) as sum_sale_total, SUM(sale_then_return_total) as sum_sale_then_return_total \
FROM fotolei_pssa.inventories WHERE extra_brand = '{}' AND extra_classification_2 = '{}' AND create_time >= '{}' AND create_time <= '{}';".format(
                    brand_tag_classification2_tag[0], brand_tag_classification2_tag[1], st_date, ed_date
                )
                rets = db_connector.query(stmt)
                if type(rets) is list and len(rets) > 0 and rets[0][0] is not None and rets[0][1] is not None:
                    sum_sale_total_for_brand_classification2 = rets[0][0]
                    sum_sale_then_return_total_for_brand_classification2 = rets[0][1]
                    sum_sale_total_for_brand_classification2 = sum_sale_total_for_brand_classification2 - sum_sale_then_return_total_for_brand_classification2
                    sum_sale_total_for_brand_classification2_percent = sum_sale_total_for_brand_classification2 / sum_sale_total * 100
                    tmp_table.append(("{}-{}".format(
                        brand_tag_classification2_tag[0], brand_tag_classification2_tag[1]),
                        sum_sale_total_for_brand_classification2, sum_sale_total_for_brand_classification2_percent
                    ))
            tmp_table.sort(key=lambda x: x[1], reverse=True)
            for item in tmp_table:
                preview_table.append([item[0], "{:.2f}".format(item[1]), "{:.2f}%".format(item[2])])

        # 把“2店销售额”提到“龟龟销售额”后面:
        gui_gui_idx = -1
        er_dian_idx = -1
        for i in range(len(preview_table)):
            if preview_table[i][0] == "龟龟销售额":
                gui_gui_idx = i
            elif preview_table[i][0] == "2店销售额":
                er_dian_idx = i
        if gui_gui_idx != -1 and er_dian_idx != -1:
            er_dian = preview_table[er_dian_idx]
            preview_table = preview_table[:er_dian_idx] + preview_table[er_dian_idx + 1:]
            preview_table.insert(gui_gui_idx + 1, er_dian)

        response_object["preview_table"] = preview_table
        return jsonify(response_object)
    else:
        response_object = {"status": "not found"}
        return jsonify(response_object)


# 预下载"销售报表（按分类汇总）"的接口
@case1_blueprint.route("/prepare", methods=["POST"])
@has_logged_in
@restrict_access(access_level=ROLE_TYPE_ORDINARY_USER)
@record_action(action=ACTION_TYPE_EXPORT)
@cost_count
def prepare_report_file_case1():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = util_generate_digest("销售报表（按分类汇总）_{}.csv".format(ts))
    csv_file = "{}/fotolei-pssa/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "销售报表（按分类汇总）_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        for row in preview_table:
            csv_writer.writerow(row)

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256

    session["op_object"] = output_file
    return jsonify(response_object)
