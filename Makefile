-include ./var/commands.make

HOST_DIR?=$(shell pwd)
HOST_VENV?=$(HOST_DIR)/.venv
HOST_CONFIG_PYTHON=python3

.PHONY: help
help:
	@echo '============================= List of available commands ======================='
	@echo 'setup        - set up env'
	@echo 'test         - run tests'
	@echo 'run          - run web app'
	@echo 'run-worker   - run listener worker'


.PHONY: setup
setup:
	@echo '============================= Setting up environment ==========================='
	[ -d $(HOST_VENV) ] || { virtualenv -p $(HOST_CONFIG_PYTHON) $(HOST_VENV);}
	$(HOST_VENV)/bin/pip install --upgrade pip
	$(HOST_VENV)/bin/pip install --upgrade setuptools
	$(HOST_VENV)/bin/pip install --upgrade zc.buildout
	$(HOST_VENV)/bin/buildout -c $(HOST_DIR)/buildout.cfg


.PHONY: test
test:
	@echo '============================= Running tests ===================================='
	$(HOST_DIR)/bin/pytest $(HOST_DIR)/sev/tests.py


.PHONY: run
run:
	@echo '============================= Running app web listener ========================='
	$(HOST_DIR)/bin/gunicorn --paste $(HOST_DIR)/development.ini


.PHONY: run-worker
run:
	@echo '============================= Running app web listener ========================='
	$(HOST_DIR)/bin/worker

