.PHONY: check
check:
	@pyflakes pssa_server.py
	@pyflakes blueprint_factory/*.py
	@pyflakes db/*.py
	@pyflakes scripts/*.py
	@pycodestyle pssa_server.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle blueprint_factory/*.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle db/*.py --ignore=E501,W504,E502,E131,E402
	@pycodestyle scripts/*.py --ignore=E501,W504,E502,E131,E402

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
	@export FLASK_APP=pssa_server && export FLASK_ENV=development && flask run --host="0.0.0.0" --port=15555

.PHONY: run_server
run_server:
	@export FLASK_APP=pssa_server && export FLASK_ENV=production && flask run --host="0.0.0.0" --port=15555

.PHONY: run_serverd
run_serverd:
	@nohup `export FLASK_APP=pssa_server && export FLASK_ENV=production && flask run --host="0.0.0.0" --port=15555 2>&1 | tee serverd.log` &

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
	@nohup `serve -s frontend/dist -l 8888 2>&1 | tee clientd.log` &

.PHONY: stop
stop:
	@./scripts/stop.sh
