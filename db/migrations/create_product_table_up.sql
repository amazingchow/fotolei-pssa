CREATE TABLE IF NOT EXISTS ggfilm.products (
    id                 INT        NOT NULL AUTO_INCREMENT,
    product_code       CHAR(64)   NOT NULL, /* 商品编码 */
    product_name       CHAR(128),           /* 商品名称 */
    specification_code CHAR(64)   NOT NULL, /* 规格编码 */
    specification_name CHAR(128),           /* 规格名称 */
    brand              CHAR(64),            /* 品牌 */
    classification_1   CHAR(64),            /* 分类1 */
    classification_2   CHAR(64),            /* 分类2 */
    product_series     CHAR(64),            /* 产品系列 */
    stop_status        CHAR(32),            /* STOP状态 */
    product_weight     INT,                 /* 重量/g */
    product_length     INT,                 /* 长度/cm */
    product_width      INT,                 /* 宽度/cm */
    product_hight      INT,                 /* 高度/cm */
    is_combined        CHAR(32) ,           /* 是否是组合商品 */
    be_aggregated      CHAR(32) ,           /* 是否参与统计 */
    is_import          CHAR(32) ,           /* 是否是进口产品 */
    supplier_name      CHAR(128),           /* 供应商名称 */
    purchase_name      CHAR(128),           /* 采购名称 */
    jit_inventory      INT,                 /* 即时库存 */
    PRIMARY KEY (id),
    KEY (product_code, specification_code)
) ENGINE=InnoDB;
