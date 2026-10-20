# Motor del TP4: oscilador amortiguado (sistema 1) y billar circular (sistema 2).
CXX ?= c++
FLAGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror -Iinclude
HEADERS := $(wildcard include/tp4/*.hpp)

.PHONY: release clean
release: build/release/tp4

build/release/tp4: src/main.cpp $(HEADERS)
	mkdir -p $(@D)
	$(CXX) $(FLAGS) -O3 -DNDEBUG $< -o $@

clean:
	rm -rf build
