#!/bin/bash

function shutdown_mysql_server_inst
{
    docker-compose -f "$HOME/fotolei-pssa-db/docker-compose/docker-compose.yml" down
}

function run
{
    shutdown_mysql_server_inst
}

run "$@";
