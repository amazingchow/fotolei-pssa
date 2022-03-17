#!/bin/bash

mkdir -p ~/fotolei-pssa-db/data
mkdir -p ~/fotolei-pssa-db/logs
mkdir -p ~/fotolei-pssa-db/conf.d
cp $PWD/test/mysql-deploy/conf.d/*.cnf ~/fotolei-pssa-db/conf.d
mkdir -p ~/fotolei-pssa-db/migrations
cp $PWD/db/migrations/*.sql ~/fotolei-pssa-db/migrations
mkdir -p ~/fotolei-pssa/logs
mkdir -p ~/fotolei-pssa/tmp-files
mkdir -p ~/fotolei-pssa/inventories
mkdir -p ~/fotolei-pssa/jit-inventory
mkdir -p ~/fotolei-pssa/products
mkdir -p ~/fotolei-pssa/send_queue
mkdir -p ~/fotolei-pssa/recv_queue
mkdir -p $PWD/tmp

docker-compose -f "$PWD/test/mysql-deploy/docker-compose.yml" up -d --build
docker_container_id=`docker container ls | grep mysql-deploy | awk '{print $1}'`
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123Pwd" < /mysql/migrations/create_database_up.sql'

migrate -source file://$PWD/db/migrations -database "mysql://root:Pwd123Pwd@(127.0.0.1:13306)/fotolei_pssa" up
if [ $? -ne 0 ]; then
    docker run -v $PWD/db/migrations:/migrations --network host migrate/migrate:v4.15.1 -path=/migrations/ -database "mysql://root:Pwd123Pwd@(127.0.0.1:13306)/fotolei_pssa" up
fi
