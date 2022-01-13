CREATE TABLE IF NOT EXISTS fotolei_pssa.operation_logs (
    id          INT          NOT NULL AUTO_INCREMENT,
    oplog       VARCHAR(256) NOT NULL,
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
