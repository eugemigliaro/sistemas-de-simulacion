PYTHON ?= python3
PYTHONPATH := python/src

.PHONY: debug release test cpp-test python-test sanitize clean

debug:
	$(MAKE) -C cpp debug

release:
	$(MAKE) -C cpp release

test: cpp-test

cpp-test:
	$(MAKE) -C cpp test

python-test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s python/tests -v

sanitize:
	$(MAKE) -C cpp sanitize

clean:
	$(MAKE) -C cpp clean
