#!/bin/bash

mkdir -p ~/mysql/data
mkdir -p ~/mysql/migrations
cp ./db/migrations/*.sql ~/mysql/migrations
mkdir -p ~/ggfilm-server/added_skus
mkdir -p ~/ggfilm-server/inventories
mkdir -p ~/ggfilm-server/jit_inventory
mkdir -p ~/ggfilm-server/products
mkdir -p ~/ggfilm-server/send_queue

docker-compose -f "test/mysql-deploy/docker-compose.yml" up -d --build
docker_container_id=`docker container ls | grep mysql-deploy | awk '{print $1}'`
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /migrations/create_database_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /migrations/create_product_table_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /migrations/create_product_summary_table_up.sql'
sleep 2
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -uroot -p"Pwd123!@" < /migrations/create_inventory_table_up.sql'
