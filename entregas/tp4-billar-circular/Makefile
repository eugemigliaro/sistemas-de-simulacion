CXX ?= c++
PYTHON ?= $(if $(wildcard python/.venv/bin/python),python/.venv/bin/python,python3)
FLAGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror -Icpp/include
HEADERS := $(wildcard cpp/include/tp4/*.hpp)
TESTS := $(patsubst cpp/tests/%.cpp,cpp/build/test/%,$(wildcard cpp/tests/test_*.cpp))
export MPLBACKEND := Agg
export MPLCONFIGDIR := $(CURDIR)/python/.matplotlib
export XDG_CACHE_HOME := $(CURDIR)/python/.cache
export CXX

.PHONY: release test sanitize oscillator-study energy-study python-env package
# El motor se compila con cpp/Makefile, el mismo que viaja en el ZIP de entrega.
release:
	$(MAKE) -C cpp release

cpp/build/test/%: cpp/tests/%.cpp $(HEADERS)
	mkdir -p $(@D)
	$(CXX) $(FLAGS) -O0 -g $< -o $@

test: release $(TESTS)
	@set -e; for binary in $(TESTS); do ./$$binary; done
	$(PYTHON) -m unittest discover -s python/tests -v

sanitize:
	mkdir -p cpp/build/sanitize
	@set -e; for source in cpp/tests/test_*.cpp; do \
	  binary=cpp/build/sanitize/$$(basename $$source .cpp); \
	  $(CXX) $(FLAGS) -O0 -g -fsanitize=address,undefined -fno-omit-frame-pointer $$source -o $$binary; \
	  ./$$binary; \
	done

oscillator-study: release
	$(PYTHON) python/study.py

energy-study: release
	$(PYTHON) python/energy_study.py

package: release
	$(PYTHON) python/package_delivery.py

python-env:
	python3 -m venv python/.venv
	python/.venv/bin/python -m pip install -r python/requirements.txt
