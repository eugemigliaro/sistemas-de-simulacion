PYTHON ?= python3
PYTHONPATH := python/src

.PHONY: debug release test cpp-test python-test visual-test sanitize clean informe informe-ver

debug:
	$(MAKE) -C cpp debug

release:
	$(MAKE) -C cpp release

test: cpp-test python-test

cpp-test:
	$(MAKE) -C cpp test

python-test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s python/tests -v

visual-test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) python/tests/visual_smoke.py

sanitize:
	$(MAKE) -C cpp sanitize

clean:
	$(MAKE) -C cpp clean

informe:
	cd informe && tectonic -X compile informe.tex
	@echo "PDF generado en informe/informe.pdf"

informe-ver: informe
	open informe/informe.pdf
