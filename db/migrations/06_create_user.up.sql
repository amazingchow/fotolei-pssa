CREATE TABLE IF NOT EXISTS fotolei_pssa.users (
    id              INT          NOT NULL AUTO_INCREMENT,
    username        VARCHAR(32)  NOT NULL,
    password_sha256 VARCHAR(64)  NOT NULL,
    salt            VARCHAR(10)  NOT NULL,
    create_time     DATETIME     DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id),
    KEY users_usr_pwd (username, password_sha256),
    KEY users_usr_salt (username, salt)
) ENGINE=InnoDB;
