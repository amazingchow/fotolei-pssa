#!/bin/bash

function setup_mysql_server_inst
{
    docker-compose -f "$HOME/fotolei-pssa-db/docker-compose/docker-compose.yml" up -d --build
}

function run
{
    setup_mysql_server_inst
}

run "$@";
