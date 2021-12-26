# -*- coding: utf-8 -*-
import csv
import os
import sys
import time
from flask import jsonify, request
sys.path.append(os.path.abspath("../utils"))
from . import blueprint
from utils import reg_positive_int
from utils import db_connector
from utils import lookup_table_brand_classification_2_association
from utils import lookup_table_classification_1_2_association
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
    for tag in ui_classification1_classification2_tags:
        c1_tag, c2_tag = tag.split("|")
        if c1_tag not in lookup_table_classification_1_2_association.keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的分类1|分类2 - 分类1：{}不存在！".format(c1_tag)
            return jsonify(response_object)
        if tag not in lookup_table_classification_1_2_association[c1_tag]:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的分类1|分类2 - 分类2：{}不存在！".format(c2_tag)
            return jsonify(response_object)
    ui_classification1_topk_tags = payload.get("ui_classification1_topk_tags", [])
    for tag in ui_classification1_topk_tags:
        c1_tag, topk_tag = tag.split("|")
        if c1_tag not in lookup_table_classification_1_2_association.keys():
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
    for tag in ui_brand_classification2_tags:
        brand_tag, c2_tag = tag.split("|")
        if brand_tag not in lookup_table_classification_1_2_association.keys():
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的品牌|分类2 - 品牌：{}不存在！".format(brand_tag)
            return jsonify(response_object)
        if tag not in lookup_table_classification_1_2_association[brand_tag]:
            response_object = {"status": "invalid tag"}
            response_object["err_msg"] = "参与统计的品牌|分类2 - 分类2：{}不存在！".format(c2_tag)
            return jsonify(response_object)

    response_object = {"status": "success"}
    preview_table = []
    preview_table.append(["{} ~ {}销售报表".format(st_date, ed_date), "", ""])
    # 计算202X年XX月~202X年XX月的总销售额
    preview_table.append(["总销售额", "xxx", "占比"])
    # 计算龟龟销售额
    preview_table.append(["龟龟销售额", "xxx", "xx%"])
    # 计算2店销售额
    preview_table.append(["2店销售额", "xxx", "xx%"])
    # 计算数码类目销售额
    preview_table.append(["数码类目销售额", "xxx", "xx%"])
    # 计算分类1为数码，分类2为背带的销售额
    preview_table.append(["背带", "xxx", "xx%"])
    # 计算分类1为数码，分类2为包&收纳的销售额
    preview_table.append(["包&收纳", "xxx", "xx%"])
    # 计算分类1为数码，分类2为快挂的销售额
    preview_table.append(["快挂", "xxx", "xx%"])
    # 计算传统类目销售额
    preview_table.append(["传统类目销售额", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为暗房冲洗设备的销售额
    preview_table.append(["暗房冲洗设备", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为胶片的销售额
    preview_table.append(["胶片", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为页片的销售额
    preview_table.append(["页片", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为相纸的销售额
    preview_table.append(["相纸", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为彩色药水的销售额
    preview_table.append(["彩色药水", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为黑白药水的销售额
    preview_table.append(["黑白药水", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为底片收纳保护的销售额
    preview_table.append(["底片收纳保护", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为翻拍器的销售额
    preview_table.append(["翻拍器", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为放大机类的销售额
    preview_table.append(["放大机类", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为胶片相机的销售额
    preview_table.append(["胶片相机", "xxx", "xx%"])
    # 计算分类1为传统耗材，分类2为机械快门线/纽的销售额
    preview_table.append(["机械快门线/纽", "xxx", "xx%"])
    # 计算各品牌销售额
    preview_table.append(["各品牌销售额", "xxx", "xx%"])
    # 品牌为巅峰设计的销售额
    preview_table.append(["巅峰设计", "xxx", "xx%"])
    # 品牌为cam-in的销售额
    preview_table.append(["cam-in", "xxx", "xx%"])
    # 品牌为poilotfoto的销售额
    preview_table.append(["poilotfoto", "xxx", "xx%"])
    # 计算各品牌-分类2销售额
    preview_table.append(["各品牌-分类2销售额", "xxx", "xx%"])
    # 品牌为伊尔福，分类2为黑白药水的销售额
    preview_table.append(["伊尔福|黑白药水", "xxx", "xx%"])
    # 品牌为伊尔福，分类2为相纸的销售额
    preview_table.append(["伊尔福|相纸", "xxx", "xx%"])
    response_object["preview_table"] = preview_table

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
