.PHONY: clean
clean: clean-pyc clean-test clean-venv clean-docs clean-install clean-mypy ## remove all build, test, coverage and Python artifacts

.PHONY: clean-pyc
clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .tox/
	rm -rf .pytest_cache/
	rm -rf .cache/

.PHONY: clean-install
clean-install:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: clean-docs
clean-docs:
	rm -rf docs/build
	rm -rf docs/source/$(NAME)*.rst
	rm -rf docs/source/modules.rst

.PHONY: clean-mypy
clean-mypy:
	rm -rf .mypy_cache


.PHONY: mypy
mypy:# launch mypy
	poetry run mypy src


.PHONY: flake8
flake8:
	poetry run flake8 src


.PHONY: safety
safety:# launch mypy
	poetry run safety check


.PHONY: isort
isort:
	poetry run isort src --check


.PHONY: lint
    lint: flake8 mypy safety


.PHONY: patch
patch:
	poetry run bump2version patch


.PHONY: minor
minor:
	poetry run bump2version minor


.PHONY: major
major:
	poetry run bump2version major


.PHONY: push
push:
	git push origin master --tags


.PHONY: test-version
test-version:
	bump2version --dry-run --verbose --allow-dirty patch


.PHONY: release-patch
release-patch:
	make test-version patch push


.PHONY: release-minor
release-minor:
	make test-version minor push


.PHONY: release-major
release-major:
	make test-version major push

.PHONY: help
help:  ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-23s\033[0m %s\n", $$1, $$2}'

