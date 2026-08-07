#include <iostream>

#include "tp1/version.hpp"
#include "test_support.hpp"

int main() {
    EXPECT_FALSE(tp1::kVersion.empty());
    return test::finish("C++ smoke test");
}
