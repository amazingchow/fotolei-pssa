CREATE TABLE IF NOT EXISTS ggfilm.inventories (
    id                         INT        NOT NULL AUTO_INCREMENT,
    product_code               VARCHAR(64)   NOT NULL, /* 商品编码 */
    product_name               VARCHAR(128)  NOT NULL, /* 商品名称 */
    specification_code         VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name         VARCHAR(128),           /* 规格名称 */
    st_inventory_qty           INT,                    /* 起始库存数量 */
    st_inventory_total         INT,                    /* 起始库存总额 */
    purchase_qty               INT,                    /* 采购数量 */
    purchase_total             INT,                    /* 采购总额 */
    purchase_then_return_qty   INT,                    /* 采购退货数量 */
    purchase_then_return_total INT,                    /* 采购退货总额 */
    sale_qty                   INT,                    /* 销售数量 */
    sale_total                 INT,                    /* 销售总额 */
    sale_then_return_qty       INT,                    /* 销售退货数量 */
    sale_then_return_total     INT,                    /* 销售退货总额 */
    others_qty                 INT,                    /* 其他变更数量 */
    others_total               INT,                    /* 其他变更总额 */
    ed_inventory_qty           INT,                    /* 截止库存数量 */
    ed_inventory_total         INT,                    /* 截止库存总额 */
    create_time                VARCHAR(10),            /* 年月的格式 */
    extra_brand                VARCHAR(64),            /* 品牌 */
    extra_classification_1     VARCHAR(64),            /* 分类1 */
    extra_classification_2     VARCHAR(64),            /* 分类2 */
    PRIMARY KEY (id),
    KEY (specification_code, extra_brand, extra_classification_1, extra_classification_2)
) ENGINE=InnoDB;
