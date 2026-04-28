.PHONY: run smoke bootstrap whoami install

PY ?= python
ifeq (,$(wildcard .venv/bin/python))
else
PY = .venv/bin/python
endif

PORT ?= 8000

install:
	$(PY) -m pip install -r requirements.txt

run:
	bash scripts/run_dev.sh $(PORT)

smoke:
	$(PY) scripts/smoke_test.py

bootstrap:
	curl -s -X POST http://127.0.0.1:$(PORT)/api/v1/catalog/components/bootstrap \
	  -H 'Content-Type: application/json' -d '{"mode":"replace"}' | $(PY) -m json.tool

whoami:
	curl -s http://127.0.0.1:$(PORT)/api/v1/figma/whoami | $(PY) -m json.tool

