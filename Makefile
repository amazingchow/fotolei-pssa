.PHONY: check
check:
	@pyflakes pssa_server.py
	@pyflakes blueprint_factory/*.py
	@pyflakes db/*.py
	@pyflakes utils/*.py
	@pyflakes scripts/*.py
	@pycodestyle pssa_server.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle blueprint_factory/*.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle db/*.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle utils/*.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle scripts/*.py --ignore=E501,W504,E502,E131,E402

.PHONY: sql_check
sql_check:
	@sqlfluff lint db/migrations/*.sql

.PHONY: init_env
init_env:
	@./scripts/init_env.sh

.PHONY: clean_env
clean_env:
	@./scripts/clean_env.sh

.PHONY: run_mysql
run_mysql:
	@./scripts/run_mysql.sh

.PHONY: stop_mysql
stop_mysql:
	@./scripts/stop_mysql.sh

.PHONY: run_server_local
run_server_local:
	@python pssa_server.py || true

.PHONY: run_serverd
run_serverd:
	@nohup python pssa_server.py 2>&1 | tee serverd.log &

.PHONY: run_client_local
run_client_local:
	@cd frontend && npm run dev

.PHONY: build_client_prod
build_client_prod:
	@cd frontend && npm run build

.PHONY: run_client
run_client: build_client_prod
	@serve -s frontend/dist -l 8888

.PHONY: run_clientd
run_clientd: build_client_prod
	@nohup serve -s frontend/dist -l 8888 2>&1 | tee clientd.log &

.PHONY: stop
stop:
	@./scripts/stop.sh

# 导出MySQL数据库"fotolei_pssa"下的所有表数据作为备份数据(不包括库结构和表结构).
.PHONY: mysql_dump
mysql_dump:
	@./scripts/mysql_dump.sh

# 给MySQL数据库"fotolei_pssa"导入备份数据(基于库结构和表结构已建好的前提下).
.PHONY: mysql_import
mysql_import:
	@./scripts/mysql_import.sh
