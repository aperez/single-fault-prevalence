.PHONY: run upreqs

ENV = env
REQS = requirements.txt

PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip3
PEP8 = $(ENV)/bin/pep8

all: run

run: $(ENV)
	$(PYTHON) classify.py

install-plugin: $(ENV)
	$(PYTHON) classify.py -i

$(ENV): $(ENV)/bin/activate
$(ENV)/bin/activate: $(REQS)
	test -d $(ENV) || virtualenv -p python3 $(ENV)
	$(PIP) install -r $(REQS)
	touch $(ENV)/bin/activate

upreqs:
	$(PIP) freeze > $(REQS)
