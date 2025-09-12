.PHONY: install dev lint test format

install:
	python -m pip install -U pip
	pip install -e ".[dev]"

dev: install

lint:
	ruff check .
	black --check .

format:
	black .
	ruff check --fix .

test:
	pytest -q
