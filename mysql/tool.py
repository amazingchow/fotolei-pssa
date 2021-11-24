# -*- coding: utf-8 -*-
import pathlib
from client import MySQLConnector
from pprint import pprint


if __name__ == "__main__":
    """
    history_data/产品目录.xls是一份产品目录, 利用脚本导入数据库来验证数据库代码.

    在测试前, 请先使用migration脚本建好库和表!!!
    """
    inst = MySQLConnector.instance()
    inst.init_conn("ggfilm")
    inst.load_data_infile(
        """LOAD DATA LOCAL INFILE "{}/{}" """.format(pathlib.Path().cwd(), "history_data/产品目录.csv") +
        "INTO TABLE ggfilm.product_repository " +
        "FIELDS TERMINATED BY ',' " +
        """ENCLOSED BY '"' """ +
        "LINES TERMINATED BY '\n' " +
        "IGNORE 1 LINES " +
        "(product_code, product_name, specification_name, " +
        "brand, classification_1, classification_2, " +
        "product_series, stop_status, product_weight, " +
        "product_length, product_width, product_hight, " +
        "is_combined, be_aggregated, is_import, " +
        "supplier_code, purchase_name, extra_info);"
    )
    ret = inst.query_sql("SELECT COUNT(*) FROM ggfilm.product_repository;")
    pprint(ret)
    inst.release_conn()
