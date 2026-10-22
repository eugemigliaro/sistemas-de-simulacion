CXX ?= g++
TP3 := ../tp3-billar-metegol/cpp
PYTHON ?= $(firstword $(wildcard python/.venv/bin/python ../tp3-billar-metegol/python/.venv/bin/python) python3)
FLAGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror -O3 -DNDEBUG
TP4_SOURCES := $(filter-out cpp/src/main.cpp,$(wildcard cpp/src/*.cpp))
TP3_SOURCES := $(filter-out $(TP3)/src/main.cpp $(TP3)/src/naive.cpp,$(wildcard $(TP3)/src/*.cpp))
export PYTHONPATH := $(CURDIR)/python/src
export MPLBACKEND := Agg

.PHONY: release test sanitize bench python-env experiments benchmark figures videos presentation package

release:
	$(MAKE) -C cpp release

test: release
	$(MAKE) -C cpp test
	$(PYTHON) -m unittest discover -s python/tests

sanitize:
	$(MAKE) -C cpp sanitize

# Harness del punto 2.1.b: enlaza el motor del TP4 con el del TP3 sin modificarlo.
bench: cpp/build/release/benchmark

cpp/build/release/benchmark: cpp/bench/benchmark.cpp $(TP4_SOURCES) $(wildcard cpp/include/tp4/*.hpp) $(TP3_SOURCES)
	@mkdir -p $(@D)
	$(CXX) $(FLAGS) -Icpp/include -I$(TP3)/include $< $(TP4_SOURCES) $(TP3_SOURCES) -o $@

python-env:
	python3 -m venv python/.venv
	python/.venv/bin/python -m pip install -r python/requirements.txt

experiments: release
	$(PYTHON) scripts/run_oscillator.py
	$(PYTHON) scripts/run_energy.py
	$(PYTHON) scripts/run_speed.py
	$(PYTHON) scripts/run_conversion.py position
	$(PYTHON) scripts/run_conversion.py map
	$(PYTHON) scripts/run_conversion.py density

# Secuencial y con la computadora sin otras tareas: mide tiempos.
benchmark: bench
	$(PYTHON) scripts/run_benchmark.py

figures:
	$(PYTHON) scripts/build_figures.py

videos: release
	$(PYTHON) scripts/build_videos.py

presentation:
	$(PYTHON) scripts/build_presentation.py

package: release
	$(PYTHON) scripts/package_delivery.py
