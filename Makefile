BASE := $(shell /bin/pwd)
CODE_COVERAGE = 72
PIPENV ?= pipenv

build: clean install test lint
	$(PIPENV) run sam build

clean:
	-rm -rfv .pytest_cache

shell:
	@$(PIPENV) shell

install: ##=> Install dependencies
	$(PIPENV) install --dev

test: ##=> Run pytest
	$(PIPENV) run python -m pytest --disable-pytest-warnings --cov $(BASE) --cov-report term-missing --cov-fail-under $(CODE_COVERAGE) tests/ -v

lint: ##=> Run pylint
	$(PIPENV) run python -m pylint --rcfile=.pylintrc *