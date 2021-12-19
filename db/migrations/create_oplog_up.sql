CREATE TABLE IF NOT EXISTS ggfilm.operation_log (
    id          INT          NOT NULL AUTO_INCREMENT,
    oplog       VARCHAR(256) NOT NULL,
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
) ENGINE=InnoDB;
