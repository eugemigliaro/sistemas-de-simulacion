PYTHON ?= $(if $(wildcard python/.venv/bin/python),python/.venv/bin/python,python3)
PYTHONPATH := python/src

.PHONY: debug release test cpp-test python-test python-env experiments assets package sanitize clean

debug:
	$(MAKE) -C cpp debug

release:
	$(MAKE) -C cpp release

test: cpp-test python-test

cpp-test:
	$(MAKE) -C cpp test

python-test:
	MPLBACKEND=Agg MPLCONFIGDIR=python/.matplotlib \
		PYTHONPATH=$(PYTHONPATH):python/tests \
		$(PYTHON) -m unittest discover -s python/tests -v

sanitize:
	$(MAKE) -C cpp sanitize

clean:
	$(MAKE) -C cpp clean

python-env:
	python3 -m venv python/.venv
	python/.venv/bin/python -m pip install -r python/requirements.txt

experiments: release
	python/.venv/bin/python scripts/run_experiments.py all

assets:
	MPLBACKEND=Agg MPLCONFIGDIR=python/.matplotlib \
		python/.venv/bin/python scripts/build_assets.py

package: release
	python/.venv/bin/python scripts/package_delivery.py
