CXX ?= g++
CPPFLAGS := -Iinclude
COMMON_FLAGS := -std=c++20 -Wall -Wextra -Wpedantic -Werror
DEBUG_FLAGS := $(COMMON_FLAGS) -O0 -g3
SANITIZE_FLAGS := $(DEBUG_FLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer

MAIN_SOURCE := src/main.cpp
LIB_SOURCES := $(sort $(filter-out $(MAIN_SOURCE),$(wildcard src/*.cpp)))
TEST_SOURCES := $(sort $(wildcard tests/test_*.cpp))
HEADERS := $(sort $(wildcard include/tp2/*.hpp))
TEST_BINARIES := $(patsubst tests/%.cpp,build/test/%,$(TEST_SOURCES))
SANITIZE_BINARIES := $(patsubst tests/%.cpp,build/sanitize/%,$(TEST_SOURCES))
DEBUG_BINARY := build/debug/tp2
RELEASE_BINARY := build/release/tp2

.PHONY: debug release test sanitize clean

debug: $(DEBUG_BINARY)

release: $(RELEASE_BINARY)

test: $(DEBUG_BINARY) $(TEST_BINARIES)
	@set -e; for test_binary in $(TEST_BINARIES); do $$test_binary; done
	@sh tests/test_cli.sh $(DEBUG_BINARY)

sanitize: $(SANITIZE_BINARIES)
	@set -e; for test_binary in $(SANITIZE_BINARIES); do $$test_binary; done

build/test/%: tests/%.cpp $(LIB_SOURCES) $(HEADERS) tests/test_support.hpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUG_FLAGS) $< $(LIB_SOURCES) -o $@

build/sanitize/%: tests/%.cpp $(LIB_SOURCES) $(HEADERS) tests/test_support.hpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(SANITIZE_FLAGS) $< $(LIB_SOURCES) -o $@

$(DEBUG_BINARY): $(MAIN_SOURCE) $(LIB_SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUG_FLAGS) $(MAIN_SOURCE) $(LIB_SOURCES) -o $@

$(RELEASE_BINARY): $(MAIN_SOURCE) $(LIB_SOURCES) $(HEADERS)
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(COMMON_FLAGS) -O3 -DNDEBUG \
		$(MAIN_SOURCE) $(LIB_SOURCES) -o $@

clean:
	rm -rf build
