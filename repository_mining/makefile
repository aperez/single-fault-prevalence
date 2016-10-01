.PHONY: run upreqs plots

ENV = env
REQS = requirements.txt

PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip3
PEP8 = $(ENV)/bin/pep8
PROFILE = -m cProfile -s tottime

all: run

run: $(ENV)
	$(PYTHON) miner.py

read_db: $(ENV)
	$(PYTHON) read_db.py

statistics: $(ENV)
	$(PYTHON) statistics.py

$(ENV): $(ENV)/bin/activate
$(ENV)/bin/activate: $(REQS)
	test -d $(ENV) || virtualenv -p python3 $(ENV)
	$(PIP) install cython
	$(PIP) install -r $(REQS)
	touch $(ENV)/bin/activate

upreqs:
	$(PIP) freeze > $(REQS)
