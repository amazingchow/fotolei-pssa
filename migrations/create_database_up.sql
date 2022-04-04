/* change time zone to what we need */
SET GLOBAL time_zone = "Asia/Shanghai";
SET time_zone = "+08:00";
SET @@session.time_zone = "+08:00";

CREATE DATABASE IF NOT EXISTS fotolei_pssa CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';
