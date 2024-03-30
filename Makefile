.PHONY: install
install:
	@poetry install

.PHONY: update
update:
	@poetry update

.PHONY: run
run:
	@poetry run uvicorn uaissistant.main:app --host 0.0.0.0 --port 8000 --reload
