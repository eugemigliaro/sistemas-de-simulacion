PYTHON ?= python3

.PHONY: debug release test cpp-test python-test sanitize cpp-run python-run clean

debug:
	$(MAKE) -C cpp debug

release:
	$(MAKE) -C cpp release

test: cpp-test python-test

cpp-test:
	$(MAKE) -C cpp test

python-test:
	PYTHONPATH=python/src $(PYTHON) -m unittest discover -s python/tests -v

sanitize:
	$(MAKE) -C cpp sanitize

cpp-run: debug
	./cpp/build/debug/tp1 $(ARGS)

python-run:
	PYTHONPATH=python/src $(PYTHON) -m tp1viz $(ARGS)

clean:
	$(MAKE) -C cpp clean
	find python -type d -name __pycache__ -prune -exec rm -r {} +
