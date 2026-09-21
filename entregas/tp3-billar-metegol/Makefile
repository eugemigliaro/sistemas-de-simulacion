PYTHON ?= $(if $(wildcard python/.venv/bin/python),python/.venv/bin/python,python3)
PYTHONPATH := python/src

.PHONY: debug release test cpp-test python-test python-env sanitize clean

debug:
	$(MAKE) -C cpp debug

release:
	$(MAKE) -C cpp release

test: cpp-test python-test

cpp-test:
	$(MAKE) -C cpp test

python-test:
	PYTHONPATH=$(PYTHONPATH):python/tests $(PYTHON) -m unittest discover -s python/tests -v

sanitize:
	$(MAKE) -C cpp sanitize

clean:
	$(MAKE) -C cpp clean

python-env:
	uv venv python/.venv
	uv pip install --python python/.venv/bin/python -r python/requirements.txt
