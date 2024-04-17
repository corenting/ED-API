
PYTHON=poetry run

SOURCE_FILES=app manage.py

.PHONY: format
format:
	$(PYTHON) ruff format $(SRC)
	$(PYTHON) ruff check --fix $(SRC)

.PHONY: style
style:
	$(PYTHON) ruff format --check $(SRC)
	$(PYTHON) ruff check $(SOURCE_FILES)
	$(PYTHON) mypy -- $(SOURCE_FILES)

.PHONY: run
run:
	$(PYTHON) uvicorn app.main:app --reload

.PHONY: build
.SILENT: build
build:
	docker build -t ed-api .
