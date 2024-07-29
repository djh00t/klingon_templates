# Makefile for klingon-tools Python package

# Variables
APP_NAME = "klingon-tools"
TWINE_USERNAME ?= __token__
TEST_TWINE_PASSWORD ?= $(TEST_PYPI_USER_AGENT)
PYPI_TWINE_PASSWORD ?= $(PYPI_USER_AGENT)

# Clean target
clean:
	@echo "Cleaning up repo.............................................................🧹"
	@make push-prep
	@pre-commit clean
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '.aider*' ! -path './.aider_logs/*' -delete
	@find . -type d -name '.aider*' ! -path './.aider_logs' -exec rm -rf {} +
	@rm -rf .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf .tox
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist
	@rm -rf htmlcov
	@rm -rf node_modules
	@echo "Repo cleaned up..............................................................✅"

# Pre-push cleanup target
push-prep:
	@echo "Removing temporary files.....................................................🧹"
	@find . -type f -name '*.pyc' -delete
	@if [ -f requirements.txt ]; then \
		echo "Resetting requirements.txt to empty state....................................✅"; \
		rm -rf requirements.txt; \
		touch requirements.txt; \
	fi
	@if [ -f requirements-dev.txt ]; then \
		echo "Resetting requirements-dev.txt to empty state................................✅"; \
		rm -rf requirements-dev.txt; \
		touch requirements-dev.txt; \
	fi
	@echo "Removed temporary files......................................................✅"

## check-packages: Check for required pip packages and requirements.txt, install if missing
check-packages:
	@echo "Installing pip-tools..."
	@pip install pip-tools
	@echo "Compiling requirements.txt..."
	@pip-compile requirements.in
	@echo "Checking for required pip packages and requirements.txt..."
	@if [ ! -f requirements.txt ]; then \
		echo "requirements.txt not found. Please add it to the project root."; \
		exit 1; \
	fi
	@echo "Installing missing packages from requirements.txt..."
	@pip install -r requirements.txt
	@pre-commit install --overwrite

## sdist: Create a source distribution package
sdist: clean
	python setup.py sdist

## wheel: Create a wheel distribution package
wheel: clean
	python setup.py sdist bdist_wheel

## upload-test: Run tests, if they pass update version number, echo it to console and upload the distribution package to TestPyPI
upload-test: test wheel
	@echo "Uploading Version $$NEW_VERSION to TestPyPI..."
	twine upload --repository-url https://test.pypi.org/legacy/ --username $(TWINE_USERNAME) --password $(TEST_TWINE_PASSWORD) dist/*

## upload: Run tests, if they pass update version number and upload the distribution package to PyPI
upload: test wheel
	@echo "Uploading Version $$NEW_VERSION to PyPI..."
	twine upload --username $(TWINE_USERNAME) --password $(PYPI_TWINE_PASSWORD) dist/*

## install: Install the package locally
install:
	@echo "Checking for requirements..."
	@make check-packages
	@echo "Installing $$APP_NAME..."
	@pip install -e .

## install-pip: Install the package locally using pip
install-pip:
	pip install $(APP_NAME)

## install-pip-test: Install the package locally using pip from TestPyPI
install-pip-test:
	pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple $(APP_NAME)

## uninstall: Uninstall the local package
uninstall:
	pip uninstall $(APP_NAME)

# Run tests
test:
	@pip install pytest
	@echo "Running unit tests..."
	pytest -v --disable-warnings tests/

## update-version: Read the version number from VERSION file and save it as
## CURRENT_VERSION variable it will look like A.B.C Increment the third (C)
## number by 1 and write it back to the VERSION file. Validate that the new
## version number is valid and echo it to console then commit it to git and
## push to origin. Confirm that VERSION and setup.py are in sync.
update-version:
	@CURRENT_VERSION=$$(cat VERSION); \
	echo "Current version is:		$$CURRENT_VERSION"; \
	NEW_VERSION=$$(awk -F. '{print $$1"."$$2"."$$3+1}' VERSION); \
	PYPI_VERSION=$$(curl -s https://pypi.org/pypi/$(APP_NAME)/json | jq -r .info.version); \
	TEST_PYPI_VERSION=$$(curl -s https://test.pypi.org/pypi/$(APP_NAME)/json | jq -r .info.version); \
	HIGHEST_VERSION=$$(echo -e "$$NEW_VERSION\n$$PYPI_VERSION\n$$TEST_PYPI_VERSION" | sort -V | tail -n 1); \
	if [ "$$HIGHEST_VERSION" != "$$NEW_VERSION" ]; then \
		NEW_VERSION=$$(echo $$HIGHEST_VERSION | awk -F. '{print $$1"."$$2"."$$3+1}'); \
	fi; \
	echo $$NEW_VERSION > VERSION; \
	sed -i "s/version=\"[0-9]*\.[0-9]*\.[0-9]*\"/version=\"$$NEW_VERSION\"/" setup.py; \
	git add VERSION setup.py; \
	git commit -m "Bump version to $$NEW_VERSION"; \
	git push origin version-bump; \
	echo $$NEW_VERSION > VERSION; \
	echo "New version is:			$$NEW_VERSION"; \
	sed -i "s/version=\"[0-9]*\.[0-9]*\.[0-9]*\"/version=\"$$NEW_VERSION\"/" setup.py; \
	@SETUP_VERSION=$$(grep "version=" setup.py | awk -F"'" '{print $$2}'); \
	if [ "$$NEW_VERSION" != "$$SETUP_VERSION" ]; then \
		echo "Error: VERSION and setup.py are not in sync"; \
		exit 1; \
	fi; \
	git add VERSION setup.py; \
	git commit -m "Bump version to $$NEW_VERSION"; \
	git push origin version-bump

## generate-pyproject: Generate a pyproject.toml file
generate-pyproject:
	@echo "[build-system]" > pyproject.toml
	@echo "requires = ['setuptools', 'wheel']" >> pyproject.toml
	@echo "build-backend = 'setuptools.build_meta'" >> pyproject.toml

.PHONY: clean check-packages sdist wheel upload-test upload install uninstall test update-version generate-pyproject gh-actions
