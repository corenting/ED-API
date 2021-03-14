PYTHON=poetry run

.PHONY: format
format:
	$(PYTHON) black app
	$(PYTHON) isort app

.PHONY: style
style:
	$(PYTHON) black --check app
	$(PYTHON) isort --check-only app
	$(PYTHON) mypy --ignore-missing-imports --disallow-untyped-defs -- app
	$(PYTHON) flakehell lint

.PHONY: run
run:
	$(PYTHON) uvicorn app.main:app --reload
