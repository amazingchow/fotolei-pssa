init:
	./init.sh

brun:
	python server.py

frun:
	cd frontend && npm run dev

.PHONY: init brun frun
