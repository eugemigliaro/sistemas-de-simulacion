CXX ?= g++
CPPFLAGS := -Iinclude
COMMON_FLAGS := -std=c++20 -Wall -Wextra -Wpedantic
DEBUG_FLAGS := $(COMMON_FLAGS) -O0 -g3
RELEASE_FLAGS := $(COMMON_FLAGS) -O3 -DNDEBUG
SANITIZE_FLAGS := $(DEBUG_FLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer

MAIN_SOURCE := src/main.cpp
LIB_SOURCES := $(sort $(filter-out $(MAIN_SOURCE),$(wildcard src/*.cpp)))
TEST_SOURCES := $(sort $(wildcard tests/test_*.cpp))
HEADERS := $(sort $(wildcard include/tp1/*.hpp))

DEBUG_BINARY := build/debug/tp1
RELEASE_BINARY := build/release/tp1
TEST_BINARIES := $(patsubst tests/%.cpp,build/test/%,$(TEST_SOURCES))
SANITIZE_BINARIES := $(patsubst tests/%.cpp,build/sanitize/%,$(TEST_SOURCES))

.PHONY: debug release test sanitize run clean

debug: $(DEBUG_BINARY)

release: $(RELEASE_BINARY)

test: $(TEST_BINARIES)
	@set -e; for test_binary in $(TEST_BINARIES); do $$test_binary; done

sanitize: $(SANITIZE_BINARIES)
	@set -e; for test_binary in $(SANITIZE_BINARIES); do $$test_binary; done

run: debug
	$(DEBUG_BINARY) $(ARGS)

$(DEBUG_BINARY): $(MAIN_SOURCE) $(LIB_SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUG_FLAGS) $(MAIN_SOURCE) $(LIB_SOURCES) -o $@

$(RELEASE_BINARY): $(MAIN_SOURCE) $(LIB_SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(RELEASE_FLAGS) $(MAIN_SOURCE) $(LIB_SOURCES) -o $@

build/test/%: tests/%.cpp $(LIB_SOURCES) $(HEADERS) tests/test_support.hpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUG_FLAGS) $< $(LIB_SOURCES) -o $@

build/sanitize/%: tests/%.cpp $(LIB_SOURCES) $(HEADERS) tests/test_support.hpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(SANITIZE_FLAGS) $< $(LIB_SOURCES) -o $@

clean:
	rm -rf build
