#!/bin/bash

function shutdown_mysql_server_inst
{
    docker-compose -f "$HOME/fotolei-pssa-db/docker-compose/docker-compose.yml" down
}

function clean_system_data
{
    sudo rm -rf $HOME/fotolei-pssa
    sudo rm -rf $HOME/fotolei-pssa-db
}

function run
{
    shutdown_mysql_server_inst
    clean_system_data
}

run "$@";
