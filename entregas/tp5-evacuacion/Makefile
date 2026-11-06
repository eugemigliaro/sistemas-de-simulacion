PYTHON ?= $(firstword $(wildcard python/.venv/bin/python ../tp3-billar-metegol/python/.venv/bin/python) python3)
export PYTHONPATH := $(CURDIR)/python/src
export MPLBACKEND := Agg

.PHONY: release test sanitize python-env atascos dt segundo-target tstar poblacion recuperacion tiempos-c tiempos-d consulta figures videos presentation delivery

release:
	$(MAKE) -C cpp release

test: release
	$(MAKE) -C cpp test
	$(PYTHON) -m unittest discover -s python/tests

sanitize:
	$(MAKE) -C cpp sanitize

python-env:
	python3 -m venv python/.venv
	python/.venv/bin/python -m pip install -r python/requirements.txt

# Estudios, en el orden en que dependen unos de otros (ver docs/decisiones.md).
atascos: release
	$(PYTHON) scripts/run_atascos.py && $(PYTHON) scripts/resumen_atascos.py
dt: release
	$(PYTHON) scripts/run_dt.py && $(PYTHON) scripts/resumen_dt.py
segundo-target: release
	$(PYTHON) scripts/run_segundo_target.py && $(PYTHON) scripts/resumen_segundo_target.py
tstar: release
	$(PYTHON) scripts/run_tstar.py
poblacion: release
	$(PYTHON) scripts/run_poblacion.py && $(PYTHON) scripts/resumen_poblacion.py
recuperacion: release
	$(PYTHON) scripts/run_recuperacion.py && $(PYTHON) scripts/resumen_recuperacion.py

# Tiempos de ejecución: en una sola computadora, sin otras tareas, con el mismo commit.
tiempos-c: release
	$(PYTHON) scripts/run_tiempos.py c && $(PYTHON) scripts/resumen_tiempos.py c
tiempos-d: release
	$(PYTHON) scripts/run_tiempos.py d && $(PYTHON) scripts/resumen_tiempos.py d

consulta:
	$(PYTHON) scripts/build_consulta.py

# Presentación y entrega (ver presentacion/README.md).
figures:
	$(PYTHON) scripts/build_figures.py
videos:
	$(PYTHON) scripts/build_videos.py
presentation: figures
	$(PYTHON) scripts/build_presentation.py
delivery:
	$(PYTHON) scripts/package_delivery.py
