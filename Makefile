PYTHON=poetry run

.PHONY: format
format:
	$(PYTHON) black .
	$(PYTHON) isort **/*.py *.py

.PHONY: format-check
style:
	$(PYTHON) black --check .

.PHONY: run
run:
	FLASK_ENV=development $(PYTHON) flask run
