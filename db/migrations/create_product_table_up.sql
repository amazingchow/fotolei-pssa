CREATE TABLE IF NOT EXISTS ggfilm.products (
    id                 INT           NOT NULL AUTO_INCREMENT,
    product_code       VARCHAR(64),            /* 商品编码 */
    product_name       VARCHAR(128),           /* 商品名称 */
    specification_code VARCHAR(64)   NOT NULL, /* 规格编码 */
    specification_name VARCHAR(128),           /* 规格名称 */
    brand              VARCHAR(64),            /* 品牌 */
    classification_1   VARCHAR(64),            /* 分类1 */
    classification_2   VARCHAR(64),            /* 分类2 */
    product_series     VARCHAR(64),            /* 产品系列 */
    stop_status        VARCHAR(32),            /* STOP状态 */
    product_weight     FLOAT,                  /* 重量/g */
    product_length     FLOAT,                  /* 长度/cm */
    product_width      FLOAT,                  /* 宽度/cm */
    product_height     FLOAT,                  /* 高度/cm */
    is_combined        VARCHAR(32),            /* 是否是组合商品 */
    be_aggregated      VARCHAR(32),            /* 是否参与统计 */
    is_import          VARCHAR(32),            /* 是否是进口商品 */
    supplier_name      VARCHAR(128),           /* 供应商名称 */
    purchase_name      VARCHAR(128),           /* 采购名称 */
    jit_inventory      INT,                    /* 实时可用库存 */
    moq                INT,                    /* 最小订货单元 */
    PRIMARY KEY (id),
    KEY (specification_code)
) ENGINE=InnoDB;
