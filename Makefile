.PHONY: test lint format clean install generate

install:
	pip install -r requirements.txt

test:
	pytest

test-verbose:
	pytest -v -s

lint:
	flake8 src tests
	mypy src

format:
	black src tests

clean:
	rm -rf reports/ .pytest_cache/ .coverage htmlcov/

generate:
	python scripts/generate_collection.py --csv $(CSV) --output $(OUTPUT)
