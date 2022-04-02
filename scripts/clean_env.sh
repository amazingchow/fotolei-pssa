#!/bin/bash

docker_container_id=`docker container ls | grep docker-compose_db_1 | awk '{print $1}'`
docker exec -i ${docker_container_id} /bin/bash -c 'mysql -u root -p"Pwd123Pwd" < /mysql/migrations/create_database_down.sql'

docker-compose -f "$HOME/fotolei-pssa-db/docker-compose/docker-compose.yml" down

rm -rf $HOME/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table
rm -rf $HOME/fotolei-pssa/tmp-files/products_load_file_repetition_lookup_table.db
rm -rf $HOME/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table
rm -rf $HOME/fotolei-pssa/tmp-files/inventories_load_file_repetition_lookup_table.db
rm -rf $HOME/fotolei-pssa/tmp-files/inventories_check_table
rm -rf $HOME/fotolei-pssa/tmp-files/inventories_check_table.db
rm -rf $HOME/fotolei-pssa/tmp-files/inventories_import_date_record_table
rm -rf $HOME/fotolei-pssa/tmp-files/inventories_import_date_record_table.db
