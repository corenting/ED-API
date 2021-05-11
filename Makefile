PYTHON=poetry run

.PHONY: format
format:
	$(PYTHON) black app
	$(PYTHON) isort app

.PHONY: style
style:
	$(PYTHON) black --check app
	$(PYTHON) isort --check-only app
	$(PYTHON) mypy -- app
	$(PYTHON) pflake8 app

.PHONY: run
run:
	$(PYTHON) uvicorn app.main:app --reload
