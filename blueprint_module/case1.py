# -*- coding: utf-8 -*-
import csv
import os
import sys
import time
from collections import defaultdict
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import reg_positive_int
from utils import db_connector
from utils import lookup_table_classification_1_2_association
from utils import lookup_table_brand_classification_2_association
from utils import cost_count
from utils import generate_digest


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
@blueprint.route("/api/v1/case1/preview", methods=["POST"])
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
    for tag in ui_classification1_tags:
        if tag not in lookup_table_classification_1_2_association.keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的分类1：{}不存在！".format(tag)
            return jsonify(response_object)

    ui_classification1_classification2_tags = payload.get("ui_classification1_classification2_tags", [])
    ui_classification1_classification2_lookup_table = defaultdict(list)
    for tag in ui_classification1_classification2_tags:
        c1_tag, c2_tag = tag.split("|")
        if c1_tag not in ui_classification1_tags:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的分类1|分类2 - 分类1：{}不存在！".format(c1_tag)
            return jsonify(response_object)
        if tag not in lookup_table_classification_1_2_association[c1_tag]:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的分类1|分类2 - 分类2：{}不存在！".format(c2_tag)
            return jsonify(response_object)
        ui_classification1_classification2_lookup_table[c1_tag].append(c2_tag)

    ui_classification1_topk_tags = payload.get("ui_classification1_topk_tags", [])
    for tag in ui_classification1_topk_tags:
        c1_tag, topk_tag = tag.split("|")
        if c1_tag not in ui_classification1_tags:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "销售top必选（分类1）- 分类1：{}不存在！".format(c1_tag)
            return jsonify(response_object)
        if not topk_tag.startswith("top"):
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "销售top必选（分类1）- topk：{}格式不正确！".format(topk_tag)
            return jsonify(response_object)
        topk = topk_tag.lstrip("top")
        if reg_positive_int.match(topk) is None:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "销售top必选（分类1）- topk：{}格式不正确！".format(topk_tag)
            return jsonify(response_object)

    ui_brand_tags = payload.get("ui_brand_tags", [])
    for tag in ui_brand_tags:
        if tag not in lookup_table_brand_classification_2_association.keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的品牌：{}不存在！".format(tag)
            return jsonify(response_object)

    ui_brand_topk_tag = payload.get("ui_brand_topk_tag", "")
    if not ui_brand_topk_tag.startswith("top"):
        response_object = {"status": "invalid tag"}
        response_object["err_msg"] = "销售top必选（品牌）- topk：{}格式不正确！".format(ui_brand_topk_tag)
        return jsonify(response_object)
    topk = ui_brand_topk_tag.lstrip("top")
    if reg_positive_int.match(topk) is None:
        response_object = {"status": "invalid tag"}
        response_object["err_msg"] = "销售top必选（品牌）- topk：{}格式不正确！".format(ui_brand_topk_tag)
        return jsonify(response_object)

    ui_brand_classification2_tags = payload.get("ui_brand_classification2_tags", [])
    ui_brand_classification2_tags_table = []
    for tag in ui_brand_classification2_tags:
        brand_tag, c2_tag = tag.split("|")
        if brand_tag not in lookup_table_brand_classification_2_association.keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的品牌|分类2 - 品牌：{}不存在！".format(brand_tag)
            return jsonify(response_object)
        if tag not in lookup_table_brand_classification_2_association[brand_tag]:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的品牌|分类2 - 分类2：{}不存在！".format(c2_tag)
            return jsonify(response_object)
        ui_brand_classification2_tags_table.append((brand_tag, c2_tag))

    response_object = {"status": "success"}
    preview_table = []
    preview_table.append(["{} ~ {}销售报表".format(st_date, ed_date), "", "占比"])
    # 计算202X年XX月~202X年XX月的总销售额
    stmt = "SELECT SUM(sale_total) as sum_sale_total FROM ggfilm.inventories WHERE create_time >= '{}' AND create_time <= '{}';".format(
        st_date, ed_date
    )
    rets = db_connector.query(stmt)
    if type(rets) is list and len(rets) > 0 and rets[0][0] is not None:
        sum_sale_total = rets[0][0]
        preview_table.append(["总销售额", "{}".format(sum_sale_total), "100%"])
        if "传统耗材" in ui_classification1_classification2_lookup_table.keys():
            # 计算龟龟销售额
            stmt = "SELECT sale_total, extra_classification_2 FROM ggfilm.inventories WHERE extra_classification_1 = '传统耗材' AND create_time >= '{}' AND create_time <= '{}';".format(
                st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                sum_sale_total_for_c1 = sum([ret[0] for ret in rets])
                sum_sale_total_for_c1_percent = sum_sale_total_for_c1 / sum_sale_total * 100
                preview_table.append(["龟龟销售额", "{}".format(sum_sale_total_for_c1), "{:.2f}%".format(sum_sale_total_for_c1_percent)])
                # 计算传统类目销售额
                # preview_table.append(["传统类目销售额", "{}".format(sum_sale_total_for_c1), "{:.2f}%".format(sum_sale_total_for_c1_percent)])
                preview_table.append(["传统类目销售额", "", ""])
                tmp_table = []
                for c2_tag in ui_classification1_classification2_lookup_table["传统耗材"]:
                    # 计算分类1为传统耗材，分类2为'c2_tag'的销售额
                    sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[1]) > 0 and ret[1].strip() == c2_tag])
                    sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                    tmp_table.append((c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent))
                tmp_table.sort(key=lambda x: x[1], reverse=True)
                for item in tmp_table:
                    preview_table.append([item[0], "{}".format(item[1]), "{:.2f}%".format(item[2])])
        if "数码" in ui_classification1_classification2_lookup_table.keys():
            # 计算2店销售额
            stmt = "SELECT sale_total, extra_classification_2 FROM ggfilm.inventories WHERE extra_classification_1 = '数码' AND create_time >= '{}' AND create_time <= '{}';".format(
                st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0:
                sum_sale_total_for_c2 = sum([ret[0] for ret in rets])
                sum_sale_total_for_c2_percent = sum_sale_total_for_c2 / sum_sale_total * 100
                preview_table.append(["2店销售额", "{}".format(sum_sale_total_for_c2), "{:.2f}%".format(sum_sale_total_for_c2_percent)])
                # 计算数码类目销售额
                # preview_table.append(["数码类目销售额", "{}".format(sum_sale_total_for_c2), "{:.2f}%".format(sum_sale_total_for_c2_percent)])
                preview_table.append(["数码类目销售额", "", ""])
                tmp_table = []
                for c2_tag in ui_classification1_classification2_lookup_table["数码"]:
                    # 计算分类1为数码，分类2为'c2_tag'的销售额
                    # TODO: 去除extra_classification_2的空格
                    sum_sale_total_for_c1_c2 = sum([ret[0] for ret in rets if len(ret[1]) > 0 and ret[1].strip() == c2_tag])
                    sum_sale_total_for_c1_c2_percent = sum_sale_total_for_c1_c2 / sum_sale_total * 100
                    tmp_table.append((c2_tag, sum_sale_total_for_c1_c2, sum_sale_total_for_c1_c2_percent))
                tmp_table.sort(key=lambda x: x[1], reverse=True)
                for item in tmp_table:
                    preview_table.append([item[0], "{}".format(item[1]), "{:.2f}%".format(item[2])])
        # 计算各品牌销售额
        preview_table.append(["品牌销售额", "", ""])
        tmp_table = []
        for brand_tag in ui_brand_tags:
            stmt = "SELECT SUM(sale_total) as sum_sale_total FROM ggfilm.inventories WHERE extra_brand = '{}' AND create_time >= '{}' AND create_time <= '{}';".format(
                brand_tag, st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0 and rets[0][0] is not None:
                sum_sale_total_for_brand = rets[0][0]
                sum_sale_total_for_brand_percent = sum_sale_total_for_brand / sum_sale_total * 100
                tmp_table.append((brand_tag, sum_sale_total_for_brand, sum_sale_total_for_brand_percent))
        tmp_table.sort(key=lambda x: x[1], reverse=True)
        for item in tmp_table:
            preview_table.append([item[0], "{}".format(item[1]), "{:.2f}%".format(item[2])])
        # 计算各品牌-分类2销售额
        preview_table.append(["品牌-分类2销售额", "", ""])
        tmp_table = []
        for brand_tag_classification2_tag in ui_brand_classification2_tags_table:
            # TODO: 去除extra_classification_2的空格
            stmt = "SELECT SUM(sale_total) as sum_sale_total FROM ggfilm.inventories WHERE extra_brand = '{}' AND extra_classification_2 LIKE '{}%' AND create_time >= '{}' AND create_time <= '{}';".format(
                brand_tag_classification2_tag[0].strip(), brand_tag_classification2_tag[1].strip(), st_date, ed_date
            )
            rets = db_connector.query(stmt)
            if type(rets) is list and len(rets) > 0 and rets[0][0] is not None:
                sum_sale_total_for_brand_classification2 = rets[0][0]
                sum_sale_total_for_brand_classification2_percent = sum_sale_total_for_brand_classification2 / sum_sale_total * 100
                tmp_table.append(("{}-{}".format(
                    brand_tag_classification2_tag[0], brand_tag_classification2_tag[1]),
                    sum_sale_total_for_brand_classification2, sum_sale_total_for_brand_classification2_percent
                ))
        tmp_table.sort(key=lambda x: x[1], reverse=True)
        for item in tmp_table:
            preview_table.append([item[0], "{}".format(item[1]), "{:.2f}%".format(item[2])])

        response_object["preview_table"] = preview_table
        return jsonify(response_object)
    else:
        response_object = {"status": "not found"}
        return jsonify(response_object)


# 预下载"销售报表（按分类汇总）"的接口
@blueprint.route("/api/v1/case1/prepare", methods=["POST"])
@cost_count
def prepare_report_file_case1():
    payload = request.get_json()
    preview_table = payload.get("preview_table", [])

    ts = int(time.time())
    csv_file_sha256 = generate_digest("销售报表（按分类汇总）_{}.csv".format(ts))
    csv_file = "{}/ggfilm-server/send_queue/{}".format(os.path.expanduser("~"), csv_file_sha256)
    output_file = "销售报表（按分类汇总）_{}.csv".format(ts)
    with open(csv_file, "w", encoding='utf-8-sig') as fd:
        csv_writer = csv.writer(fd, delimiter=",")
        for row in preview_table:
            csv_writer.writerow(row)

    response_object = {"status": "success"}
    response_object["output_file"] = output_file
    response_object["server_send_queue_file"] = csv_file_sha256
    return jsonify(response_object)
