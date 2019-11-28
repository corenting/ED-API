PYTHON=.venv/bin/python

.SILENT: lint
.PHONY: lint
lint:
	$(PYTHON) -m black --exclude venv .
