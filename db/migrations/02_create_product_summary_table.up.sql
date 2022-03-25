DROP TABLE IF EXISTS fotolei_pssa.product_summary;

CREATE TABLE IF NOT EXISTS fotolei_pssa.product_summary (
    id          INT      NOT NULL AUTO_INCREMENT,
    total       INT      NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
