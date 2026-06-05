PYTHON ?= python3

.PHONY: check test compile lint format format-check type build ci dev-install clean

check:
	$(PYTHON) scripts/check.py

test:
	$(PYTHON) -m unittest

compile:
	$(PYTHON) -m compileall -q email_app tests main.py "smtp app.py" "pop3 app.py"

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

format-check:
	$(PYTHON) -m ruff format --check .

type:
	$(PYTHON) -m mypy email_app tests

build:
	$(PYTHON) -m build

ci: check format-check lint type build

dev-install:
	$(PYTHON) -m pip install -e ".[dev]"

clean:
	$(PYTHON) scripts/clean.py
