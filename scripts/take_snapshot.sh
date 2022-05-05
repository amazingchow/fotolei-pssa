#!/bin/bash

function prepare_snapshot_dirs
{
    mkdir -p $HOME/fotolei-pssa-snapshot/mysqldump-files
    mkdir -p $HOME/fotolei-pssa-snapshot/system-logs
    mkdir -p $HOME/fotolei-pssa-snapshot/shelve-files
}

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

function take_snapshot
{
    cp -r $HOME/fotolei-pssa/backup/* $HOME/fotolei-pssa-snapshot/mysqldump-files/
    cp -r $HOME/fotolei-pssa/logs/* $HOME/fotolei-pssa-snapshot/system-logs/
    cp -r $HOME/fotolei-pssa/tmp-files/* $HOME/fotolei-pssa-snapshot/shelve-files/
    cp -r $HOME/fotolei-pssa-keep/* $HOME/fotolei-pssa-snapshot/shelve-files/

    rm -rf /mnt/pssa/*
    mv $HOME/fotolei-pssa-snapshot /mnt/pssa/
}

function run
{
    prepare_snapshot_dirs
    do_mysql_dump
    take_snapshot
}

run "$@";
