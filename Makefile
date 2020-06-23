PYTHON=poetry run

.PHONY: format
format:
	$(PYTHON) black --exclude=workdir .
	$(PYTHON) isort **/*.py *.py

.PHONY: style
style:
	$(PYTHON) black --exclude=workdir --check .
	$(PYTHON) isort --check-only **/*.py *.py

.PHONY: run
run:
	FLASK_ENV=development $(PYTHON) flask run
