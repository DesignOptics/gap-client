.SUFFIXES: .js .css .html .svg .jpeg .png .htm

.EXPORT_ALL_VARIABLES:
SHELL:=/bin/bash

ROOT_DIR:=$(shell dirname "$(realpath $(lastword $(MAKEFILE_LIST)))")
TESTS_DIR:=${ROOT_DIR}/tests
REQUIREMENTS_DIR:=${ROOT_DIR}/requirements
CODE_QUALITY_DIR:=${ROOT_DIR}/code_quality

GAP_BARE_VERSION:=$(shell cat "$(ROOT_DIR)/VERSION")


CI_COMMIT_REF_NAME?=$(shell git rev-parse --abbrev-ref HEAD)
GAP_GIT_ACTUAL_BRANCH:=$(CI_COMMIT_REF_NAME)
GAP_GIT_HASH?=$(shell git rev-parse HEAD)
GAP_GIT_HASH_SHORT?=$(shell git rev-parse --short HEAD)
GAP_BUILD_DATE=?=$(shell date -u +'%Y-%m-%dT%H:%M:%SZ')

export GAP_VERSION:=$(shell \
	branch=$(GAP_GIT_ACTUAL_BRANCH); \
	version='$(GAP_BARE_VERSION)'; \
	if [[ "$${branch}" == production ]]; then \
		echo "$${version}"; \
	elif [[ "$${branch}" == beta ]]; then \
		echo "$${version}-beta"; \
	elif [[ "$${branch}" == stage-* ]] && [[ "$${branch:6}" != "" ]] ; then \
		echo "$${version}-$${branch:6}"; \
	else \
		echo "$${version}-test-$${branch//[      ]/_}"; \
	fi )

VENV_NAME:=gap_venv

GAP_PROJECT_GROUP_BASE_NAME:=gap-solutions
GAP_PROJECT_BASE_NAME:=gap-client
GAP_TOOL_NAME:=$(GAP_PROJECT_BASE_NAME)
GAP_PROJECT_NAME:=$(GAP_PROJECT_GROUP)/$(GAP_PROJECT_BASE_NAME)

PYPI_REGISTRY_USERNAME:=__token__
PYPI_REGISTRY_PASSWORD:=${PYPI_TOKEN}


define twine_config
[distutils]
index-servers=pypi
[pypi]
username=__token__
password=$(PYPI_REGISTRY_PASSWORD)
endef
export twine_config

.PHONY: all
all: help

.PHONY: info
info:
	@echo "CI_COMMIT_REF_NAME=$(CI_COMMIT_REF_NAME)"
	@echo "CI_COMMIT_TAG=$(CI_COMMIT_TAG)"
	@echo "CI_PROJECT_DIR=$(CI_PROJECT_DIR)"
	@echo "CODE_QUALITY_DIR=$(CODE_QUALITY_DIR)"
	@echo "GAP_BARE_VERSION=$(GAP_VERSION)"
	@echo "GAP_BUILD_DATE=$(GAP_BUILD_DATE)"
	@echo "GAP_GIT_ACTUAL_BRANCH=$(GAP_GIT_ACTUAL_BRANCH)"
	@echo "GAP_GIT_HASH=$(GAP_GIT_HASH)"
	@echo "GAP_GIT_HASH_SHORT=$(GAP_GIT_HASH_SHORT)"
	@echo "GAP_PROJECT_BASE_NAME=$(GAP_PROJECT_BASE_NAME)"
	@echo "GAP_PROJECT_GROUP_BASE_NAME=$(GAP_PROJECT_GROUP_BASE_NAME)"
	@echo "GAP_PROJECT_NAME=$(GAP_PROJECT_NAME)"
	@echo "GAP_TOOL_NAME=$(GAP_TOOL_NAME)"
	@echo "GAP_VERSION=$(GAP_VERSION)"
	@echo "PYPI_REGISTRY_PASSWORD=\"$(shell echo $(PYPI_REGISTRY_PASSWORD))\""  # Escaping and quoting the password
	@echo "PYPI_REGISTRY_USERNAME=$(PYPI_REGISTRY_USERNAME)"
	@echo "PYPI_TOKEN=\"$(shell echo $(PYPI_TOKEN))\""  # Escaping and quoting the password
	@echo "REQUIREMENTS_DIR=$(REQUIREMENTS_DIR)"
	@echo "ROOT_DIR=$(ROOT_DIR)"
	@echo "SHELL=$(SHELL)"
	@echo "TESTS_DIR=$(TESTS_DIR)"
	@echo "VENV_NAME=$(VENV_NAME)"

.PHONY: env
env:
	@echo "=== ENV"
	export -p
	@echo " "

.PHONY: ver
ver:
	@echo "=== DOCKER TAG / PYPI VERSION:"
	@echo "$(GAP_VERSION)"
	@echo " "
	@echo "=== PYTHON & PIP:"
	@python --version || python3 --version || echo "NO PYTHON"
	@pip --version || pip3 --version || echo "NO PIP"
	@echo " "

# Caluclate checksum of source directory
.PHONY: checksum
checksum:
	@find ./gap-client -type d -name '__pycache__' -prune -o  -type f  -print -exec md5sum {} + | LC_ALL=C sort | md5sum | head -c 12 > CHECKSUM
	@cat CHECKSUM


# Python requirements management
###################################################################

.PHONY: req-base
req-base:
	pip install --upgrade pip
	pip install --upgrade pip-tools wheel twine

.PHONY: req-src
req-src:
	cd "$(REQUIREMENTS_DIR)"; \
	pip-compile --no-header --no-emit-index-url --output-file=requirements.txt \
		requirements.in; \
	pip-compile --no-header --no-emit-index-url --output-file=test_requirements.txt \
		requirements.in \
		test_requirements.in; \

.PHONY: req-install
req-install:
	cd "$(REQUIREMENTS_DIR)"; \
	pip install -r requirements.txt

.PHONY: req-install-test
req-install-test:
	cd "$(REQUIREMENTS_DIR)"; \
	pip install -r test_requirements.txt

.PHONY: uninstall
uninstall:
	GAP_GIT_ACTUAL_BRANCH=$(GAP_GIT_ACTUAL_BRANCH) pip uninstall -y $(GAP_PROJECT_BASE_NAME);

# Build and re-install package locally
.PHONY: setup
setup: uninstall
	GAP_GIT_ACTUAL_BRANCH=$(GAP_GIT_ACTUAL_BRANCH) pip install -e $(ROOT_DIR);

.PHONY: req
req: uninstall req-base req-src setup


# Python package management
###################################################################

.PHONY: pypi-build
pypi-build:
	GAP_GIT_ACTUAL_BRANCH=$(GAP_GIT_ACTUAL_BRANCH) python setup.py build --parallel 99
	GAP_GIT_ACTUAL_BRANCH=$(GAP_GIT_ACTUAL_BRANCH) python setup.py sdist bdist_wheel
	ls -halt dist/

.PHONY: pypi-push
pypi-push:
	echo "$$twine_config" > 'twine.conf'
	twine upload --config-file twine.conf dist/*.tar.gz --skip-existing --verbose
	rm 'twine.conf'

.PHONY: pypi-push-local
pypi-push-local:
	@echo "Pushing using username and pass"
	twine upload dist/*.tar.gz --skip-existing --verbose




# Code quality and testing
###################################################################

.PHONY: test
test:
	cd "${TESTS_DIR}" && make all || echo "OOOPS"

.PHONY: code-quality
code-quality:
	cd $(CODE_QUALITY_DIR); \
	make all


.PHONY: help
help:
	@echo ""
	@echo " Convenience Makefile for Gap Client"
	@echo " -----------------------------------"
	@echo ""
	@echo ""
	@echo "  Information output:"
	@echo ""
	@echo "    make info                        - Lists internal variables"
	@echo "    make env                         - Lists environment variables"
	@echo "    make ver                         - Lists current tool versions"
	@echo ""
	@echo "  Requirements:"
	@echo ""
	@echo "    make req                         - Rebuild pinned versions in *requirements.txt from *requirements.in"
	@echo ""
	@echo "  Preparation:"
	@echo ""
	@echo "    make pypi-build                  - Build and pack into PyPi package"
	@echo "    make pypi-push                   - Push the package to PyPi using credentials from environment"
	@echo "    make pypi-push-local             - Push the package to PyPi using manual entry of credentials"
	@echo ""
	@echo "  Code quality:"
	@echo ""
	@echo "    make test                        - Run tests. NOTE: For more options see tests/Makefile"
	@echo "    make code-quality                - Run all code quality checks. NOTE: For more options see code_quality/Makefile"
	@echo ""
