
PYTHON=poetry run

SOURCE_FILES=app manage.py

.PHONY: format
format:
	$(PYTHON) black $(SOURCE_FILES)
	$(PYTHON) ruff --fix $(SOURCE_FILES)

.PHONY: style
style:
	$(PYTHON) black --check $(SOURCE_FILES)
	$(PYTHON) ruff $(SOURCE_FILES)
	$(PYTHON) mypy -- $(SOURCE_FILES)

.PHONY: run
run:
	$(PYTHON) uvicorn app.main:app --reload

.PHONY: build
.SILENT: build
build:
	docker build -t ed-api .
