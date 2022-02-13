#!/bin/bash

docker-compose -f "$PWD/test/mysql-deploy/docker-compose.yml" up -d --build
