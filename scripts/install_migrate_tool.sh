#!/bin/bash

function install_migrate_tool
{
    if [[ "$OSTYPE" == "darwin"* ]]; then
        curl https://github.com/golang-migrate/migrate/releases/download/v4.15.1/migrate.darwin-amd64.tar.gz -O -L
        mkdir migrate-tmp
        tar -C ./migrate-tmp -zxvf migrate.darwin-amd64.tar.gz
        sudo mv ./migrate-tmp/migrate /usr/local/bin
        sudo chown root:root /usr/local/bin/migrate
        rm migrate.darwin-amd64.tar.gz
        rm -rf migrate-tmp
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl https://github.com/golang-migrate/migrate/releases/download/v4.15.1/migrate.linux-amd64.tar.gz -O -L
        mkdir migrate-tmp
        tar -C ./migrate-tmp -zxvf migrate.linux-amd64.tar.gz
        sudo mv ./migrate-tmp/migrate /usr/local/bin
        rm migrate.linux-amd64.tar.gz
        rm -rf migrate-tmp
    fi
}

function run
{
    install_migrate_tool
}

run "$@";
