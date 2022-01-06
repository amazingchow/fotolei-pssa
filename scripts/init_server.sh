#!/bin/bash

mkdir -p ~/mysql/data
mkdir -p ~/mysql/logs
mkdir -p ~/mysql/conf.d
cp $PWD/test/mysql-deploy/conf.d/*.cnf ~/mysql/conf.d
mkdir -p ~/mysql/migrations
cp $PWD/db/migrations/*.sql ~/mysql/migrations
mkdir -p ~/ggfilm-server/inventories
mkdir -p ~/ggfilm-server/jit_inventory
mkdir -p ~/ggfilm-server/products
mkdir -p ~/ggfilm-server/send_queue
mkdir -p ~/ggfilm-server/recev_queue
mkdir -p $PWD/tmp

docker-compose -f "$PWD/test/mysql-deploy/docker-compose.yml" up -d --build
docker_container_id=`docker container ls | grep mysql-deploy | awk '{print $1}'`
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /mysql/migrations/create_database_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /mysql/migrations/create_product_table_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /mysql/migrations/create_product_summary_table_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /mysql/migrations/create_inventory_table_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /mysql/migrations/create_inventory_summary_table_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /mysql/migrations/create_oplog_up.sql'
