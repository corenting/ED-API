PYTHON=poetry run

.SILENT: format
.PHONY: format
format:
	$(PYTHON) black .

.SILENT: isort
.PHONY: isort
isort:
	$(PYTHON) isort **/*.py *.py
