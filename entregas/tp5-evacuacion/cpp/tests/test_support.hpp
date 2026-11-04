#pragma once

#include <cmath>
#include <iostream>
#include <string_view>

namespace test {

inline int failures = 0;

inline void check(bool condition, std::string_view expression, std::string_view file, int line) {
    if (!condition) {
        std::cerr << file << ':' << line << ": falla: " << expression << '\n';
        ++failures;
    }
}

inline void check_near(double actual, double expected, double tolerance, std::string_view expression,
                       std::string_view file, int line) {
    if (!std::isfinite(actual) || std::abs(actual - expected) > tolerance) {
        std::cerr << file << ':' << line << ": " << expression << " = " << actual
                  << ", se esperaba " << expected << " +- " << tolerance << '\n';
        ++failures;
    }
}

template <typename Exception, typename Callable>
void check_throws(Callable&& callable, std::string_view expression, std::string_view file, int line) {
    try {
        callable();
    } catch (const Exception&) {
        return;
    } catch (...) {
    }
    std::cerr << file << ':' << line << ": no lanzo la excepcion esperada: " << expression << '\n';
    ++failures;
}

inline int finish(std::string_view name) {
    if (failures == 0) {
        std::cout << name << ": OK\n";
        return 0;
    }
    std::cerr << name << ": " << failures << " fallas\n";
    return 1;
}

}  // namespace test

#define CHECK(condition) test::check((condition), #condition, __FILE__, __LINE__)
#define CHECK_NEAR(actual, expected, tolerance) \
    test::check_near((actual), (expected), (tolerance), #actual, __FILE__, __LINE__)
#define CHECK_THROWS(Exception, statement) \
    test::check_throws<Exception>([&] { statement; }, #statement, __FILE__, __LINE__)
