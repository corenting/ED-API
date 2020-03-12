PYTHON=poetry run

.SILENT: format
.PHONY: format
format:
	$(PYTHON) black .

.SILENT: format-check
.PHONY: format-check
format-check:
	$(PYTHON) black --check .

.SILENT: isort
.PHONY: isort
isort:
	$(PYTHON) isort **/*.py *.py
