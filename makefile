# Local automation contract for 2605_DS5111_zdd3ga
# Explicit virtual-environment routing - no reliance on shell activation.

ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip
PYLINTRC = pylintrc

.PHONY: default env update lint test run load

default:
	@cat makefile

env:
	python3 -m venv $(ENV)
	$(PIP) install --upgrade pip

update: env
	$(PIP) install -r requirements.txt

lint:
	$(PYTHON) -m pylint --rcfile=$(PYLINTRC) bin/ tests/

test:
	$(PYTHON) -m pytest -vv tests/

run:
	$(PYTHON) bin/enrich_transcripts.py < mock_transcripts.jsonl | $(PYTHON) bin/validate_schema.py

load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat data/enriched_transcripts.jsonl | python bin/load_snowflake.py

# ---- LAB08: Docker targets ----

docker_build:
	docker build -t hankelmhurst/ds5111-pipeline:latest .

docker_run:
	cat data/youtube_ids.txt | docker run -i --env-file .env hankelmhurst/ds5111-pipeline:latest

docker_push:
	docker push hankelmhurst/ds5111-pipeline:latest

docker_pull_test:
	docker rmi -f hankelmhurst/ds5111-pipeline:latest
	cat data/youtube_ids.txt | docker run -i --env-file .env hankelmhurst/ds5111-pipeline:latest
