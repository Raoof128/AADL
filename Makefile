.PHONY: install lint format test

install:
	@pip install -r requirements.txt
	@pip install -e .[dev]

lint:
	@flake8 src tests
	@black --check src tests
	@mypy src

format:
	@black src tests

test:
	@pytest
