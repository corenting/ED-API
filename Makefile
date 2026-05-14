
PYTHON=poetry run

.PHONY: format
format:
	$(PYTHON) ruff format .
	$(PYTHON) ruff check --fix .

.PHONY: style
style:
	$(PYTHON) ruff format --check .
	$(PYTHON) ruff check .
	$(PYTHON) pyrefly check .

.PHONY: run
run:
	$(PYTHON) uvicorn app.main:app --reload

.PHONY: build
.SILENT: build
build:
	docker build -t ed-api .
