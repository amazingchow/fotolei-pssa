#!/bin/bash

function do_mysql_dump
{
    # --single-transaction --quick : it will use less RAM and also produce consistent dumps without locking tables.
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysqldump -hmysql_server -P3306 -uroot -pPwd123Pwd --single-transaction --quick --no-create-info fotolei_pssa products > /backup/fotolei_pssa_products.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysqldump -hmysql_server -P3306 -uroot -pPwd123Pwd --single-transaction --quick --no-create-info fotolei_pssa product_summary > /backup/fotolei_pssa_product_summary.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysqldump -hmysql_server -P3306 -uroot -pPwd123Pwd --single-transaction --quick --no-create-info fotolei_pssa inventories > /backup/fotolei_pssa_inventories.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysqldump -hmysql_server -P3306 -uroot -pPwd123Pwd --single-transaction --quick --no-create-info fotolei_pssa inventory_summary > /backup/fotolei_pssa_inventory_summary.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysqldump -hmysql_server -P3306 -uroot -pPwd123Pwd --single-transaction --quick --no-create-info fotolei_pssa operation_logs > /backup/fotolei_pssa_operation_logs.sql'
    docker run -it --rm --network=mysql_service_network -v $HOME/fotolei-pssa/backup:/backup summychoutoto/mysql:5.7-support-logs-and-socket /bin/bash -c 'mysqldump -hmysql_server -P3306 -uroot -pPwd123Pwd --single-transaction --quick --no-create-info fotolei_pssa users --where="id > 1" > /backup/fotolei_pssa_users.sql'
}

function run
{
    do_mysql_dump
}

run "$@";
