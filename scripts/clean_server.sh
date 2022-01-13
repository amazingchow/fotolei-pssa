#!/bin/bash

docker_container_id=`docker container ls | grep mysql-deploy_db_1 | awk '{print $1}'`
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -u root -p"Pwd123Pwd" < /mysql/migrations/create_database_down.sql'

docker-compose -f "$PWD/test/mysql-deploy/docker-compose.yml" down

rm -rf $PWD/tmp/products_load_file_repetition_lookup_table
rm -rf $PWD/tmp/products_load_file_repetition_lookup_table.db
rm -rf $PWD/tmp/inventories_load_file_repetition_lookup_table
rm -rf $PWD/tmp/inventories_load_file_repetition_lookup_table.db
rm -rf $PWD/tmp/inventories_check_table
rm -rf $PWD/tmp/inventories_check_table.db
