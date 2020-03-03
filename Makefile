PYTHON=poetry run

.SILENT: lint
.PHONY: lint
lint:
	$(PYTHON) black .
