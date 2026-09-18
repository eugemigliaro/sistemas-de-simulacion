#pragma once

#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string_view>

namespace test {

inline int failures = 0;

inline void expect_true(
    bool condition,
    std::string_view expression,
    std::string_view file,
    int line
) {
    if (!condition) {
        std::cerr << file << ':' << line
                  << ": expected true: " << expression << '\n';
        ++failures;
    }
}

inline void expect_near(
    double actual,
    double expected,
    double tolerance,
    std::string_view expression,
    std::string_view file,
    int line
) {
    if (!std::isfinite(actual)
        || std::abs(actual - expected) > tolerance) {
        std::cerr << file << ':' << line
                  << ": expected " << expression
                  << " near " << expected
                  << ", actual " << actual << '\n';
        ++failures;
    }
}

template <typename Callable>
void expect_invalid_argument(
    Callable&& callable,
    std::string_view expression,
    std::string_view file,
    int line
) {
    try {
        callable();
        std::cerr << file << ':' << line
                  << ": expected invalid_argument: "
                  << expression << '\n';
        ++failures;
    } catch (const std::invalid_argument&) {
    } catch (...) {
        std::cerr << file << ':' << line
                  << ": expected invalid_argument but caught another type\n";
        ++failures;
    }
}

inline int finish(std::string_view suite_name) {
    if (failures == 0) {
        std::cout << suite_name << " OK\n";
        return 0;
    }
    std::cerr << suite_name << " failed with "
              << failures << " assertion(s)\n";
    return 1;
}

}  // namespace test

#define EXPECT_TRUE(expression) \
    ::test::expect_true((expression), #expression, __FILE__, __LINE__)

#define EXPECT_FALSE(expression) \
    ::test::expect_true(!(expression), "!(" #expression ")", __FILE__, __LINE__)

#define EXPECT_NEAR(actual, expected, tolerance) \
    ::test::expect_near( \
        (actual), (expected), (tolerance), \
        #actual, __FILE__, __LINE__ \
    )

#define EXPECT_INVALID_ARGUMENT(statement) \
    ::test::expect_invalid_argument( \
        [&]() { static_cast<void>(statement); }, \
        #statement, __FILE__, __LINE__ \
    )
