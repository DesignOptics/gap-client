ROOT_DIR:=$(shell dirname "$(realpath $(lastword $(MAKEFILE_LIST)))")
APP_DIR:=${ROOT_DIR}/..
TESTS_DIR:=${APP_DIR}/tests
TEST_CMD:=python -m pytest

.PHONY: h all unit integration load help

h: help

all: unit integration load

unit:
	$(TEST_CMD) -vv unit

integration:
	$(TEST_CMD) -vv integration

load:
	$(TEST_CMD) -vv load


############### Help ####################


gap:
	$(TEST_CMD) -vv integration/test_gap.py

############### Help ####################

help:
	@echo ""
	@echo " General targets:"
	@echo ""
	@echo " + make help            Show this help"
	@echo " + make all             Run all tests"
	@echo " + make load            Run all load tests"
	@echo " + make unit            Run all unit tests"
	@echo " + make integration     Run all integration tests"
	@echo ""
	@echo "Unit targets:"
	@echo ""
	@echo " + make gap             Run unit tests for gap"
	@echo ""
