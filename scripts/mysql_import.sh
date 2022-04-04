#!/bin/bash

function do_mysql_recover
{
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysql -hmysql_server -P3306 -uroot -pPwd123Pwd fotolei_pssa < /backup/fotolei_pssa_products.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysql -hmysql_server -P3306 -uroot -pPwd123Pwd fotolei_pssa < /backup/fotolei_pssa_product_summary.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysql -hmysql_server -P3306 -uroot -pPwd123Pwd fotolei_pssa < /backup/fotolei_pssa_inventories.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysql -hmysql_server -P3306 -uroot -pPwd123Pwd fotolei_pssa < /backup/fotolei_pssa_inventory_summary.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysql -hmysql_server -P3306 -uroot -pPwd123Pwd fotolei_pssa < /backup/fotolei_pssa_operation_logs.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysql -hmysql_server -P3306 -uroot -pPwd123Pwd fotolei_pssa < /backup/fotolei_pssa_users.sql'
}

function run
{
    do_mysql_recover
}

run "$@";
