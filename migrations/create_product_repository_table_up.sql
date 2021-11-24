CREATE TABLE IF NOT EXISTS ggfilm.product_inventory (
    id                 INT        NOT NULL AUTO_INCREMENT,
    product_code       CHAR(64)   NOT NULL, /* 商品编号 */
    product_name       CHAR(128)  NOT NULL, /* 商品名称 */
    specification_name CHAR(64),            /* 规格名称 */
    brand              CHAR(64)   NOT NULL, /* 品牌 */
    classification_1   CHAR(64)   NOT NULL, /* 分类一 */
    classification_2   CHAR(64)   NOT NULL, /* 分类二 */
    product_series     CHAR(64),            /* 商品系列 */
    stop_status        TINYINT    NOT NULL, /* STOP状态 */
    product_weight     INT,                 /* 商品重量, 单位g */
    product_length     INT,                 /* 商品长度, 单位cm */
    product_width      INT,                 /* 商品宽度, 单位cm */
    product_hight      INT,                 /* 商品高度, 单位cm */
    is_combined        TINYINT    NOT NULL, /* 是否是组合商品 */
    be_aggregated      TINYINT    NOT NULL, /* 是否参与统计 */
    is_import          TINYINT    NOT NULL, /* 是否是进口商品 */
    supplier_code      CHAR(64),            /* 供应商编号 */
    purchase_name      CHAR(128),           /* 采购名称 */
    extra_info         TEXT,                /* 拓展字段 */
    create_time        DATETIME   DEFAULT CURRENT_TIMESTAMP(),
    update_time        DATETIME   DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
    PRIMARY KEY (id),
    KEY (product_code)
) ENGINE=InnoDB;
