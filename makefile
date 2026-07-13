# Local automation contract for 2605_DS5111_zdd3ga
# Explicit virtual-environment routing - no reliance on shell activation.

ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip
PYLINTRC = pylintrc

.PHONY: default env update lint test run

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
