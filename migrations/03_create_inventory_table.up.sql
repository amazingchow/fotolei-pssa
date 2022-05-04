CREATE TABLE IF NOT EXISTS fotolei_pssa.inventories (
    id                         INT           NOT NULL AUTO_INCREMENT,
    product_code               VARCHAR(64),                           /* 商品编码 */
    product_name               VARCHAR(128),                          /* 商品名称 */
    specification_code         VARCHAR(64)   NOT NULL,                /* 规格编码 */
    specification_name         VARCHAR(128),                          /* 规格名称 */
    st_inventory_qty           INT           NOT NULL DEFAULT 0,      /* 起始库存数量 */
    st_inventory_total         FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 起始库存总额 */
    purchase_qty               INT           NOT NULL DEFAULT 0,      /* 采购数量 */
    purchase_total             FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 采购总额 */
    purchase_then_return_qty   INT           NOT NULL DEFAULT 0,      /* 采购退货数量 */
    purchase_then_return_total FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 采购退货总额 */
    sale_qty                   INT           NOT NULL DEFAULT 0,      /* 销售数量 */
    sale_total                 FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 销售总额 */
    sale_then_return_qty       INT           NOT NULL DEFAULT 0,      /* 销售退货数量 */
    sale_then_return_total     FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 销售退货总额 */
    others_qty                 INT           NOT NULL DEFAULT 0,      /* 其他变更数量 */
    others_total               FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 其他变更总额 */
    ed_inventory_qty           INT           NOT NULL DEFAULT 0,      /* 截止库存数量 */
    ed_inventory_total         FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 截止库存总额 */
    create_time                VARCHAR(10),                           /* 年月的格式 */
    extra_brand                VARCHAR(64),                           /* 品牌 */
    extra_classification_1     VARCHAR(64),                           /* 分类1 */
    extra_classification_2     VARCHAR(64),                           /* 分类2 */
    extra_is_combined          VARCHAR(32),                           /* 是否是组合商品 */
    anchor                     TINYINT       NOT NULL DEFAULT 0,      /* 锚，防止‘组合商品‘读出来带空格 */
    PRIMARY KEY (id),
    KEY inventories_ct (create_time),
    KEY inventories_specification_code_ct (specification_code, create_time),
    KEY inventories_extra_is_combined_ct (extra_is_combined, create_time),
    KEY inventories_extra_is_combined_extra_brand_ct (extra_is_combined, extra_brand, create_time),
    KEY inventories_extra_is_combined_extra_c1_ct (extra_is_combined, extra_classification_1, create_time),
    KEY inventories_extra_is_combined_extra_c2_ct (extra_is_combined, extra_classification_2, create_time)
) ENGINE=InnoDB;
