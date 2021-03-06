CREATE TABLE IF NOT EXISTS fotolei_pssa.products (
    id                 INT           NOT NULL AUTO_INCREMENT,
    product_code       VARCHAR(64),                           /* 商品编码 */
    product_name       VARCHAR(128),                          /* 商品名称 */
    specification_code VARCHAR(64)   NOT NULL,                /* 规格编码 */
    specification_name VARCHAR(128),                          /* 规格名称 */
    brand              VARCHAR(64),                           /* 品牌 */
    classification_1   VARCHAR(64),                           /* 分类1 */
    classification_2   VARCHAR(64),                           /* 分类2 */
    product_series     VARCHAR(64),                           /* 产品系列 */
    stop_status        VARCHAR(32),                           /* STOP状态 */
    product_weight     FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 重量/g */
    product_length     FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 长度/cm */
    product_width      FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 宽度/cm */
    product_height     FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 高度/cm */
    is_combined        VARCHAR(32),                           /* 是否是组合商品 */
    be_aggregated      VARCHAR(32),                           /* 是否参与统计 */
    is_import          VARCHAR(32),                           /* 是否是进口商品 */
    supplier_name      VARCHAR(128),                          /* 供应商名称 */
    purchase_name      VARCHAR(128),                          /* 采购名称 */
    jit_inventory      INT           NOT NULL DEFAULT 0,      /* 实时可用库存 */
    moq                INT           NOT NULL DEFAULT 0,      /* 最小订货单元 */
    unit_price         FLOAT(10,2)   NOT NULL DEFAULT '0.00', /* 单价 */
    PRIMARY KEY (id),
    KEY products_specification_code (specification_code),
    KEY products_specification_code_jit_inventory (specification_code, jit_inventory),
    KEY products_specification_code_unit_price (specification_code, unit_price),
    KEY products_is_combined_product_series (is_combined, product_series),
    KEY products_is_combined_stop_status_be_aggregated_supplier_name (is_combined, stop_status, be_aggregated, supplier_name)
) ENGINE=InnoDB;
