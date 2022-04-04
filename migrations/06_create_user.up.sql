CREATE TABLE IF NOT EXISTS fotolei_pssa.users (
    id              INT          NOT NULL AUTO_INCREMENT,
    username        VARCHAR(32)  NOT NULL,
    password_sha256 VARCHAR(64)  NOT NULL,
    salt            VARCHAR(10)  NOT NULL,
    role_type       TINYINT      NOT NULL, /* 角色分为: 0 - 超级管理员 1 - 管理员 2 - 普通用户 */
    create_time     DATETIME     DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id),
    KEY users_usr_pwd (username, password_sha256),
    KEY users_usr_salt (username, salt)
) ENGINE=InnoDB;

INSERT INTO fotolei_pssa.users (username, password_sha256, salt, role_type) VALUES (
    "fotolei", "3d825201968dfb37611a604a67ec590bcaf97d397c840d34518088ddb49ec6ff", "FVgFQm39iZ", 0);
