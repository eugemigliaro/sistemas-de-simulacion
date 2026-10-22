CXX ?= g++
CPPFLAGS := -Iinclude
FLAGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror
DEBUG_FLAGS := $(FLAGS) -O0 -g
SANITIZE_FLAGS := $(DEBUG_FLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer

SOURCES := $(sort $(filter-out src/main.cpp,$(wildcard src/*.cpp)))
HEADERS := $(wildcard include/tp4/*.hpp)
TEST_SOURCES := $(sort $(wildcard tests/test_*.cpp))
TESTS := $(patsubst tests/%.cpp,build/test/%,$(TEST_SOURCES))
SANITIZED := $(patsubst tests/%.cpp,build/sanitize/%,$(TEST_SOURCES))

.PHONY: release debug test sanitize clean

release: build/release/tp4

debug: build/debug/tp4

build/release/tp4: src/main.cpp $(SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(FLAGS) -O3 -DNDEBUG src/main.cpp $(SOURCES) -o $@

build/debug/tp4: src/main.cpp $(SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUG_FLAGS) src/main.cpp $(SOURCES) -o $@

build/test/%: tests/%.cpp tests/test_support.hpp $(SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(FLAGS) -O2 -g $< $(SOURCES) -o $@

build/sanitize/%: tests/%.cpp tests/test_support.hpp $(SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(SANITIZE_FLAGS) $< $(SOURCES) -o $@

test: $(TESTS) build/debug/tp4
	@set -e; for binary in $(TESTS); do $$binary; done
	@if [ -f tests/test_cli.sh ]; then sh tests/test_cli.sh build/debug/tp4; fi

sanitize: $(SANITIZED)
	@set -e; for binary in $(SANITIZED); do $$binary; done

clean:
	rm -rf build
