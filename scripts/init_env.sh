#!/bin/bash

mkdir -p $HOME/fotolei-pssa-db/data
mkdir -p $HOME/fotolei-pssa-db/logs
mkdir -p $HOME/fotolei-pssa-db/docker-compose
cp $PWD/mysql_docker_compose/docker-compose.yml $HOME/fotolei-pssa-db/docker-compose
mkdir -p $HOME/fotolei-pssa-db/conf.d
cp $PWD/mysql_docker_compose/conf.d/*.cnf $HOME/fotolei-pssa-db/conf.d
mkdir -p $HOME/fotolei-pssa-db/migrations
cp $PWD/migrations/*.sql $HOME/fotolei-pssa-db/migrations
mkdir -p $HOME/fotolei-pssa/logs
mkdir -p $HOME/fotolei-pssa/tmp-files
mkdir -p $HOME/fotolei-pssa/inventories
mkdir -p $HOME/fotolei-pssa/jit-inventory
mkdir -p $HOME/fotolei-pssa/products
mkdir -p $HOME/fotolei-pssa/send_queue
mkdir -p $HOME/fotolei-pssa/session
mkdir -p $HOME/fotolei-pssa/recv_queue
mkdir -p $HOME/fotolei-pssa/unit-price

docker-compose -f "$HOME/fotolei-pssa-db/docker-compose/docker-compose.yml" up -d --build
docker_container_id=`docker container ls | grep docker-compose_db_1 | awk '{print $1}'`
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -pPwd123Pwd < /mysql/migrations/create_database_up.sql'

migrate -source file://$PWD/migrations -database "mysql://root:Pwd123Pwd@(127.0.0.1:13306)/fotolei_pssa" up
if [ $? -ne 0 ]; then
    docker run --rm -v $PWD/migrations:/migrations --network host migrate/migrate:v4.15.1 -path=/migrations/ -database "mysql://root:Pwd123Pwd@(127.0.0.1:13306)/fotolei_pssa" up
fi
