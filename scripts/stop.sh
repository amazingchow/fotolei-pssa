#!/bin/bash

function shutdown_clientd
{
    lsof -i:8888 | grep node | awk '{print $2}' | xargs kill
}

function shutdown_serverd
{
    lsof -i:15555 | grep flask | awk '{print $2}' | xargs kill
}

function run
{
    shutdown_clientd
    shutdown_serverd
}

run "$@";
