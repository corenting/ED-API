
PYTHON=poetry run

SOURCE_FILES=app manage.py

.PHONY: format
format:
	$(PYTHON) black $(SOURCE_FILES)
	$(PYTHON) isort $(SOURCE_FILES)

.PHONY: style
style:
	$(PYTHON) black --check $(SOURCE_FILES)
	$(PYTHON) isort --check-only $(SOURCE_FILES)
	$(PYTHON) mypy -- $(SOURCE_FILES)
	$(PYTHON) pflake8 $(SOURCE_FILES)

.PHONY: run
run:
	$(PYTHON) uvicorn app.main:app --reload
