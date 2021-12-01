.PHONY: init
init:
	@./init_server.sh

.PHONY: clean
clean:
	@./clean_server.sh

.PHONY: run_server
run_server:
	@export FLASK_APP=ggfilm_server && export FLASK_ENV=production && flask run --host="0.0.0.0" --port=15555

.PHONY: run_client_local
run_client_local:
	@cd frontend && npm run dev

.PHONY: build_client_prod
build_client_prod:
	@cd frontend && npm run build

.PHONY: run_client
run_client: build_client_prod
	@serve -s frontend/dist -l 8888
