PYTHON := .venv/bin/python

.PHONY: setup data analysis notebooks test all

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[dev]"

data:
	$(PYTHON) scripts/bootstrap_data.py --refresh

analysis:
	$(PYTHON) scripts/run_all.py --offline

notebooks:
	$(PYTHON) scripts/build_notebooks.py

test:
	$(PYTHON) -m pytest -q
	$(PYTHON) scripts/validate_portfolio.py

all: analysis notebooks test
