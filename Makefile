.PHONY: check
check:
	@pyflakes ggfilm_server.py
	@pycodestyle ggfilm_server.py --ignore=E501,W504,E502,E131

.PHONY: init
init:
	@./init_server.sh

.PHONY: clean
clean:
	@./clean_server.sh

.PHONY: run_server_local
run_server_local:
	@export FLASK_APP=ggfilm_server && export FLASK_ENV=development && flask run --host="0.0.0.0" --port=15555

.PHONY: run_server
run_server:
	@export FLASK_APP=ggfilm_server && export FLASK_ENV=production && flask run --host="0.0.0.0" --port=15555

.PHONY: run_serverd
run_serverd:
	@nohup `export FLASK_APP=ggfilm_server && export FLASK_ENV=production && flask run --host="0.0.0.0" --port=15555 2>&1 | tee serverd.log` &

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
