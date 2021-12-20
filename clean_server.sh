#!/bin/bash

docker_container_id=`docker container ls | grep mysql-deploy_db_1 | awk '{print $1}'`
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -u root -p"Pwd123!@" < /migrations/create_database_down.sql'

docker-compose -f "test/mysql-deploy/docker-compose.yml" down

rm -rf products_load_file_repetition_lookup_table
rm -rf products_load_file_repetition_lookup_table.db
rm -rf inventories_load_file_repetition_lookup_table
rm -rf inventories_load_file_repetition_lookup_table.db
