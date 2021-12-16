CREATE TABLE IF NOT EXISTS ggfilm.products (
    id                 INT          NOT NULL AUTO_INCREMENT,
    product_code       VARCHAR(64)  NOT NULL, /* 商品编码 */
    product_name       VARCHAR(128) NOT NULL, /* 商品名称 */
    specification_code VARCHAR(64)  NOT NULL, /* 规格编码 */
    specification_name VARCHAR(128),          /* 规格名称 */
    brand              VARCHAR(64),           /* 品牌 */
    classification_1   VARCHAR(64),           /* 分类1 */
    classification_2   VARCHAR(64),           /* 分类2 */
    product_series     VARCHAR(64),           /* 产品系列 */
    stop_status        VARCHAR(32),           /* STOP状态 */
    product_weight     INT,                   /* 重量/g */
    product_length     INT,                   /* 长度/cm */
    product_width      INT,                   /* 宽度/cm */
    product_height     INT,                   /* 高度/cm */
    is_combined        VARCHAR(32) ,          /* 是否是组合商品 */
    be_aggregated      VARCHAR(32) ,          /* 是否参与统计 */
    is_import          VARCHAR(32) ,          /* 是否是进口产品 */
    supplier_name      VARCHAR(128),          /* 供应商名称 */
    purchase_name      VARCHAR(128),          /* 采购名称 */
    jit_inventory      INT,                   /* 即时库存 */
    PRIMARY KEY (id),
    KEY (product_code, specification_code)
) ENGINE=InnoDB;
